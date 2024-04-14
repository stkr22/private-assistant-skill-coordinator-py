import os
import pathlib
import shutil
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from private_assistant_skill_coordinator import coordinator, messages


# Fixture for setting up the Coordinator
@pytest.fixture
def test_coordinator():
    if not os.path.exists("./local_config.yaml"):
        # Copy the file
        shutil.copy("./template.yaml", "./local_config.yaml")
    coord = coordinator.Coordinator(config_path=pathlib.Path("./local_config.yaml"))
    coord.client = MagicMock()  # Mock the MQTT client
    return coord


# Test purging old registrations
def test_purge_old_registrations(test_coordinator):
    old_registration = messages.SkillRegistration(
        skill_id="temp_sensor",
        feedback_topic="skill/temp_sensor/feedback",
        registered_at=datetime(2022, 1, 1, 12, 0, 0),
    )
    test_coordinator.skill_registrations["temp_sensor"] = old_registration
    test_coordinator.purge_old_registrations()

    assert "temp_sensor" not in test_coordinator.skill_registrations
