"""
도메인 값 객체(Value Objects) 모음.

값 객체는 식별자 없이 속성값으로만 동등성을 판단하는 불변 객체.
이 객체들을 하나의 파일에 모두 배치할지, 각각의 파일로 분리할지는
판단의 영역이다. 이는 전적으로 개발자의 선호에 달려 있다.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업 상태 열거형 — 작업의 생명주기 단계
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# 프로젝트 상태 열거형 — 활성 또는 완료
class ProjectStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# 프로젝트 유형 열거형 — 일반 프로젝트와 기본 수집함(INBOX) 구분
class ProjectType(Enum):
    REGULAR = "REGULAR"
    INBOX = "INBOX"


# 우선순위 열거형 — 숫자 값으로 비교 가능
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# frozen=True는 값 객체에 적합하도록 불변으로 만든다
@dataclass(frozen=True)
class Deadline:
    """마감일 값 객체 — 불변이며 시간대 인식 datetime 필수."""
    due_date: datetime

    def __post_init__(self):
        """생성 시 유효성 검증 — 시간대 정보 필수, 과거 날짜 불가"""
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 시간대를 인식하는 datetime이어야 한다")
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없다")

    def is_overdue(self) -> bool:
        """기한 초과 여부 확인"""
        return datetime.now(timezone.utc) > self.due_date

    def time_remaining(self) -> timedelta:
        """남은 시간 계산 — 기한 초과 시 timedelta(0) 반환"""
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        """마감일 임박 여부 — 경고 임계값(기본 1일) 이내인지 확인"""
        return timedelta(0) < self.time_remaining() <= warning_threshold
