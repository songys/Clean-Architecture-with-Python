from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import (
    Deadline,
    Priority,
    TaskStatus,
)


# Task 도메인 엔티티: 클린 아키텍처의 가장 안쪽 계층에 위치
# 외부 의존성(DB, 프레임워크) 없이 순수 비즈니스 규칙만 포함
@dataclass
class Task(Entity):
    """완료해야 하는 작업."""

    title: str
    description: str
    project_id: UUID  # 소속 프로젝트의 ID (외래키 역할)
    due_date: Optional[Deadline] = None  # 마감일 (값 객체)
    priority: Priority = Priority.MEDIUM  # 기본 우선순위: MEDIUM
    # init=False: 생성자에서 직접 설정하지 않고 내부적으로 관리하는 필드
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)

    def start(self) -> None:
        """작업을 진행 중으로 표시한다."""
        # 상태 전이 규칙: TODO -> IN_PROGRESS만 허용
        if self.status != TaskStatus.TODO:
            raise ValueError("'TODO' 상태의 작업만 시작할 수 있습니다")
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, notes: Optional[str] = None) -> None:
        """
        작업을 완료로 표시한다.

        Args:
            notes: 선택적 완료 노트

        Raises:
            ValueError: 작업이 이미 완료된 경우
        """
        # 비즈니스 규칙: 이미 완료된 작업은 다시 완료할 수 없음
        if self.status == TaskStatus.DONE:
            raise ValueError("작업이 이미 완료되었습니다")
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()  # 완료 시각 자동 기록
        self.completion_notes = notes

    def is_overdue(self) -> bool:
        """작업이 기한을 초과했는지 확인한다."""
        return self.due_date is not None and self.due_date.is_overdue()
