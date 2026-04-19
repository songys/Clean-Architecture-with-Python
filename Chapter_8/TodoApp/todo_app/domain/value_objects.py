"""
이 모든 객체를 하나의 파일에 넣을지 각자의 파일에 넣을지는
개발자의 판단에 달려 있다. 전적으로 개발자의 선호도에 따른다.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업 상태를 나타내는 열거형: TODO -> IN_PROGRESS -> DONE 순서로 전이
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# 프로젝트 상태 열거형: ACTIVE(진행중) 또는 COMPLETED(완료)
class ProjectStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# 프로젝트 유형 열거형: INBOX(기본, 할당되지 않은 작업용) 또는 REGULAR(일반)
class ProjectType(Enum):
    REGULAR = "REGULAR"
    INBOX = "INBOX"


# 작업 우선순위 열거형: 숫자 값으로 비교 가능
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# 값 객체(Value Object): 불변(frozen)이며 값으로 동등성을 비교
# frozen=True는 값 객체에 필요한 불변성을 보장한다
@dataclass(frozen=True)
class Deadline:
    due_date: datetime

    def __post_init__(self):
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 시간대를 인식하는 datetime을 사용해야 합니다")
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없습니다")

    def is_overdue(self) -> bool:
        return datetime.now(timezone.utc) > self.due_date

    def time_remaining(self) -> timedelta:
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    # 마감일이 경고 임계값 이내로 다가왔는지 확인
    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        return timedelta(0) < self.time_remaining() <= warning_threshold
