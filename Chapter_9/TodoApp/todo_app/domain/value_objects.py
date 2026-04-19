"""
이 모든 객체를 하나의 파일에 배치할지 각각의 파일에 배치할지는
판단의 문제이다. 이는 전적으로 개발자의 선호에 따른다.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업 상태를 나타내는 열거형 값 객체
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# 프로젝트 상태를 나타내는 열거형 값 객체
class ProjectStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# 프로젝트 유형 - INBOX는 미할당 작업을 위한 특수 프로젝트
class ProjectType(Enum):
    REGULAR = "REGULAR"
    INBOX = "INBOX"


# 작업 우선순위를 나타내는 열거형 값 객체 - 숫자 값으로 비교 가능
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# 마감일 값 객체 - 불변(frozen) 보장으로 도메인 규칙 캡슐화
# 시간대 인식 필수, 과거 날짜 생성 불가 등의 유효성 검증 포함
# frozen=True는 값 객체에 적합하게 불변으로 만든다
@dataclass(frozen=True)
class Deadline:
    due_date: datetime

    def __post_init__(self):
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 시간대 인식 datetime을 사용해야 합니다")
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없습니다")

    def is_overdue(self) -> bool:
        return datetime.now(timezone.utc) > self.due_date

    def time_remaining(self) -> timedelta:
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        return timedelta(0) < self.time_remaining() <= warning_threshold
