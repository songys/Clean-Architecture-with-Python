"""
이 객체들을 하나의 파일에 모두 배치할지 각각의 파일에 배치할지는
개발자의 판단에 달려 있다. 이것은 전적으로 개발자의 선호도에 따른다.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업 상태를 나타내는 열거형 값 객체
class TaskStatus(Enum):
    TODO = "TODO"  # 할 일
    IN_PROGRESS = "IN_PROGRESS"  # 진행 중
    DONE = "DONE"  # 완료


# 프로젝트 상태를 나타내는 열거형 값 객체
class ProjectStatus(Enum):
    ACTIVE = "ACTIVE"  # 활성
    COMPLETED = "COMPLETED"  # 완료


# 작업 우선순위를 나타내는 열거형 값 객체 - 숫자 값으로 비교 가능
class Priority(Enum):
    LOW = 1  # 낮음
    MEDIUM = 2  # 보통
    HIGH = 3  # 높음


# 마감일을 표현하는 불변 값 객체 - 비즈니스 규칙(시간대 필수, 과거 불허)을 강제
# frozen=True로 값 객체에 적합한 불변성을 보장한다
@dataclass(frozen=True)
class Deadline:
    due_date: datetime  # 시간대 정보(timezone)가 포함된 마감일

    def __post_init__(self):
        # 비즈니스 규칙: 시간대 정보 필수 (UTC 등)
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 시간대 정보가 포함된 datetime이어야 한다")
        # 비즈니스 규칙: 과거 날짜를 마감일로 설정 불가
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없다")

    # 현재 시각이 마감일을 지났는지 확인하는 메서드
    def is_overdue(self) -> bool:
        return datetime.now(timezone.utc) > self.due_date

    # 마감일까지 남은 시간을 반환하는 메서드 (기한 초과 시 0)
    def time_remaining(self) -> timedelta:
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    # 마감일이 임계값 이내로 다가왔는지 확인하는 메서드 (알림 발송 기준)
    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        return timedelta(0) < self.time_remaining() <= warning_threshold
