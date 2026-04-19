"""
이 객체들을 하나의 파일에 모을지 각각의 파일에 나눌지는
개발자의 판단에 따른 선택이다.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


# 작업 상태 값 객체: 작업의 생명주기를 표현하는 열거형
# TODO → IN_PROGRESS → DONE 순서로 상태 전이
class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# 우선순위 값 객체: 작업의 중요도를 숫자 값으로 표현하는 열거형
# 숫자 값(1, 2, 3)을 통한 우선순위 간 비교 가능
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# 마감일 값 객체: frozen=True로 불변(immutable) 보장
# 값 객체의 핵심 특성인 불변성과 자체 유효성 검증을 구현
@dataclass(frozen=True)
class Deadline:
    due_date: datetime

    # 생성 시 자동 유효성 검증: 시간대 정보 필수, 과거 날짜 거부
    def __post_init__(self):
        if not self.due_date.tzinfo:
            raise ValueError("마감일은 시간대 정보가 포함된 datetime을 사용해야 합니다")
        if self.due_date < datetime.now(timezone.utc):
            raise ValueError("마감일은 과거일 수 없습니다")

    # 마감일 초과 여부 확인
    def is_overdue(self) -> bool:
        return datetime.now(timezone.utc) > self.due_date

    # 남은 시간 계산 - 음수 방지를 위해 최솟값 0으로 제한
    def time_remaining(self) -> timedelta:
        return max(timedelta(0), self.due_date - datetime.now(timezone.utc))

    # 마감일 임박 여부 확인 - 기본 경고 기준: 1일
    def is_approaching(self, warning_threshold: timedelta = timedelta(days=1)) -> bool:
        return timedelta(0) < self.time_remaining() <= warning_threshold
