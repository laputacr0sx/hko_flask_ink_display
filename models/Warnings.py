from enum import Enum, unique
from datetime import datetime
from typing import Optional


@unique
class ActionCode(Enum):
    EXTEND = 'EXTEND'
    ISSUE = 'ISSUE'
    REISSUE = 'REISSUE'
    UPDATE = 'UPDATE'
    CANCEL = 'CANCEL'


class WarningValue:
    name: str
    code: str
    action_code: ActionCode
    issue_time: datetime
    update_time: datetime
    type: Optional[str]
    expire_time: Optional[datetime]

    def __init__(
        self,
        name: str,
        code: str,
        action_code: ActionCode,
        issue_time: datetime,
        update_time: datetime,
        type: Optional[str],
        expire_time: Optional[datetime],
    ) -> None:
        self.name = name
        self.code = code
        self.action_code = action_code
        self.issue_time = issue_time
        self.update_time = update_time
        self.type = type
        self.expire_time = expire_time
