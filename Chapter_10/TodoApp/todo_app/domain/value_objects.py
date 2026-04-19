"""
도메인 계층의 값 객체(Value Object) 모듈.
- 값 객체: 식별자 없이 속성값으로만 동일성을 판단하는 불변 객체
- 이 객체들을 하나의 파일에 배치할지 각각의 파일에 배치할지는
  판단의 문제다. 개발자의 선호에 따라 결정하면 된다.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업 상태 열거형 (상태 전이: TODO -> IN_PROGRESS -> DONE)
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# 프로젝트 상태 열거형
class ProjectStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# 프로젝트 유형 열거형 (INBOX는 미할당 작업을 위한 특수 프로젝트)
class ProjectType(Enum):
    REGULAR = "REGULAR"
    INBOX = "INBOX"


# 작업 우선순위 열거형 (숫자 값으로 비교 가능)
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# frozen=True는 값 객체에 적합하도록 이를 불변으로 만든다
@dataclass(frozen=True)
class Deadline:
    """마감일 값 객체.
    - 불변(frozen) 객체로 한번 생성되면 변경 불가
    - 생성 시점에 유효성 검증 (타임존 필수, 과거 날짜 불가)
    - 마감일 관련 비즈니스 로직(초과 여부, 남은 시간, 임박 여부) 캡슐화
    """
    due_date: datetime

    def __post_init__(self):
        # 값 객체 생성 시 유효성 검증 (자기 보호)
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 타임존 인식 datetime을 사용해야 합니다")
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없습니다")

    def is_overdue(self) -> bool:
        """마감일 초과 여부 확인"""
        return datetime.now(timezone.utc) > self.due_date

    def time_remaining(self) -> timedelta:
        """마감일까지 남은 시간 계산"""
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        """마감일 임박 여부 확인 (기본 임계값: 1일)"""
        return timedelta(0) < self.time_remaining() <= warning_threshold
