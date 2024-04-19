from datetime import datetime

from private_assistant_commons import messages
from pydantic import Field


class SkillRegistration(messages.SkillRegistration):
    registered_at: datetime = Field(default_factory=datetime.now)
