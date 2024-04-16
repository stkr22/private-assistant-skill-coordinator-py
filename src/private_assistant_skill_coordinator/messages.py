from datetime import datetime

from private_assistant_commons import messages


class SkillRegistration(messages.SkillRegistration):
    registered_at: datetime = datetime.now()
