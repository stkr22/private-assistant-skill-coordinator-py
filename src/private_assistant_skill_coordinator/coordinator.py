import logging
import pathlib
import threading
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta

import paho.mqtt.client as mqtt
from private_assistant_commons import messages as common_messages
from pydantic import BaseModel, ConfigDict, ValidationError

from private_assistant_skill_coordinator import config, messages

logger = logging.getLogger(__name__)


class CertaintyCollection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    responses: list[common_messages.SkillCertainty] = []
    expected: int
    timer: threading.Timer

    def all_responses_received(self) -> bool:
        return len(self.responses) >= self.expected

    def select_highest_certainty(self) -> common_messages.SkillCertainty | None:
        if self.responses:
            max_response = max(self.responses, key=lambda c: c.certainty)
            if max_response.certainty > 0.0:
                return max_response
        return None


class Coordinator:
    def __init__(self, config_path: pathlib.Path):
        self.config_obj = config.load_config(config_path)
        self.client: mqtt.Client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.config_obj.client_id,
            protocol=mqtt.MQTTv5,
        )
        self.client.on_connect, self.client.on_message = self.mqtt_function()
        self.skill_registrations: dict[str, messages.SkillRegistration] = {}
        self.certainties: dict[uuid.UUID, CertaintyCollection] = {}
        self.lock: threading.RLock = threading.RLock()
        # Initialize the repeating purge timer
        self.purge_timer = threading.Timer(600.0, self.purge_old_registrations)
        self.purge_timer.daemon = True
        self.purge_timer.start()

    def mqtt_function(self) -> tuple[Callable, Callable]:
        def on_connect(client: mqtt.Client, user_data, flags, rc: int, properties):
            logger.info("Connected with result code %s", rc)
            client.subscribe(
                [
                    (self.config_obj.certainty_topic, mqtt.SubscribeOptions(qos=1)),
                    (self.config_obj.register_topic, mqtt.SubscribeOptions(qos=1)),
                ]
            )

        def on_message(client: mqtt.Client, user_data, msg: mqtt.MQTTMessage):
            logger.debug("Received message %s", msg)
            if msg.topic == self.config_obj.certainty_topic:
                self.handle_certainty_message(msg.payload.decode("utf-8"))
            elif msg.topic == self.config_obj.register_topic:
                self.handle_registration_message(msg.payload.decode("utf-8"))

        return on_connect, on_message

    def handle_certainty_message(self, payload: str):
        try:
            certainty: common_messages.SkillCertainty = (
                common_messages.SkillCertainty.model_validate_json(payload)
            )
            with self.lock:
                if certainty.message_id not in self.certainties:
                    self.certainties[certainty.message_id] = CertaintyCollection(
                        expected=len(self.skill_registrations),
                        timer=threading.Timer(
                            self.config_obj.certainty_timeout,
                            self.select_skill,
                            args=[certainty.message_id],
                        ),
                    )
                    self.certainties[certainty.message_id].timer.daemon = True
                    self.certainties[certainty.message_id].timer.start()

                self.certainties[certainty.message_id].responses.append(certainty)
                if self.certainties[certainty.message_id].all_responses_received():
                    if self.certainties[certainty.message_id].timer:
                        self.certainties[certainty.message_id].timer.cancel()
                    self.select_skill(certainty.message_id)
        except ValidationError as e:
            logger.error("Error validating certainty message: %s", e)

    def handle_registration_message(self, payload: str):
        try:
            registration: messages.SkillRegistration = (
                messages.SkillRegistration.model_validate_json(payload)
            )
            with self.lock:
                self.skill_registrations[registration.skill_id] = registration
        except ValidationError as e:
            logger.error("Error validating registration message: %s", e)

    def select_skill(self, message_id: uuid.UUID):
        with self.lock:
            if message_id in self.certainties:
                certainty_collection = self.certainties[message_id]
                highest_certainty = certainty_collection.select_highest_certainty()
                if highest_certainty:
                    skill_registration = self.skill_registrations.get(
                        highest_certainty.skill_id
                    )
                    if skill_registration:
                        self.client.publish(
                            skill_registration.feedback_topic, str(message_id), qos=1
                        )
                    else:
                        logger.error(
                            "Skill %s is not registered. Skipping.",
                            highest_certainty.skill_id,
                        )
                del self.certainties[message_id]

    def purge_old_registrations(self):
        with self.lock:
            now = datetime.now()
            self.skill_registrations = {
                k: v
                for k, v in self.skill_registrations.items()
                if now - v.registered_at
                <= timedelta(seconds=self.config_obj.registration_purge_interval)
            }
        # Reschedule the purge operation
        self.purge_timer = threading.Timer(
            self.config_obj.registration_purge_interval, self.purge_old_registrations
        )
        self.purge_timer.daemon = True
        self.purge_timer.start()

    # Ensure to cleanly shutdown the timer when the application is exiting
    def shutdown(self):
        self.client.disconnect()

    def run(self):
        try:
            self.client.connect(
                self.config_obj.mqtt_server_host, self.config_obj.mqtt_server_port, 60
            )
            self.client.loop_forever()
        finally:
            self.shutdown()
