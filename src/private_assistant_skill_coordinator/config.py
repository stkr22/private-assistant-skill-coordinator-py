import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class Config(BaseModel):
    mqtt_server_host: str = "localhost"
    mqtt_server_port: int = 1883
    client_id: str = "skill_coordinator"
    certainty_topic: str = "assistant/coordinator/certainty"
    register_topic: str = "assistant/coordinator/register"
    registration_purge_interval: float = 600.0
    certainty_timeout: float = 1.0


def load_config(config_path: Path) -> Config:
    try:
        with config_path.open("r") as file:
            config_data = yaml.safe_load(file)
        return Config.model_validate(config_data)
    except FileNotFoundError as err:
        logger.error("Config file not found: %s", config_path)
        raise err
    except ValidationError as err_v:
        logger.error("Validation error: %s", err_v)
        raise err_v
