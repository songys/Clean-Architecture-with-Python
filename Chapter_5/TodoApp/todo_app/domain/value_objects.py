"""
이 객체들을 하나의 파일에 모을지 개별 파일로 분리할지는
개발자의 판단에 따른다. 전적으로 개발자의 선호도 문제다.
"""
# 도메인 값 객체(Value Object) 모음
# - 값 객체: ID가 아닌 값 자체로 동등성을 판단하는 불변 객체
# - 작업 상태, 프로젝트 상태, 우선순위 열거형과 마감일(Deadline) 값 객체로 구성

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업의 상태를 나타내는 열거형 (TODO → IN_PROGRESS → DONE)
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# 프로젝트의 상태를 나타내는 열거형 (ACTIVE → COMPLETED)
class ProjectStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# 작업 우선순위를 나타내는 열거형 (숫자 값으로 비교 가능)
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# 마감일 값 객체 - 불변(frozen)으로 정의하여 값 객체의 불변성 보장
# - 생성 시 타임존 포함 여부와 과거 날짜 여부를 검증
# - 기한 초과, 남은 시간, 임박 여부 판단 등 마감일 관련 도메인 로직 포함
# frozen=True는 값 객체에 적합하도록 불변으로 만든다
@dataclass(frozen=True)
class Deadline:
    due_date: datetime  # 마감 일시 (타임존 포함 필수)

    # 생성 시 검증: 타임존 정보 포함 여부 및 과거 날짜 여부 확인
    def __post_init__(self):
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 타임존 인식 datetime을 사용해야 합니다")
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없습니다")

    # 현재 시간 기준 기한 초과 여부 확인
    def is_overdue(self) -> bool:
        return datetime.now(timezone.utc) > self.due_date

    # 마감일까지 남은 시간 계산 (기한 초과 시 0 반환)
    def time_remaining(self) -> timedelta:
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    # 마감일이 경고 임계값 이내로 임박했는지 확인 (기본: 1일 이내)
    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        return timedelta(0) < self.time_remaining() <= warning_threshold
