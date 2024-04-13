import uuid
from datetime import datetime

from pydantic import BaseModel


class SkillCertainty(BaseModel):
    message_id: uuid.UUID
    certainty: float
    skill_id: str


class SkillRegistration(BaseModel):
    skill_id: str
    feedback_topic: str
    registered_at: datetime = datetime.now()
