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


# 핵심 도메인 엔터티 - 비즈니스 규칙과 상태 전이를 캡슐화
# 외부 인프라(웹, DB)에 대한 의존성 없이 순수 비즈니스 로직만 포함
@dataclass
class Task(Entity):
    """완료해야 할 작업."""

    title: str
    description: str
    project_id: UUID
    due_date: Optional[Deadline] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)

    def start(self) -> None:
        """작업을 진행 중으로 표시한다."""
        if self.status != TaskStatus.TODO:
            raise ValueError("'TODO' 상태의 작업만 시작할 수 있습니다")
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, notes: Optional[str] = None) -> None:
        """
        작업을 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모

        Raises:
            ValueError: 작업이 이미 완료된 경우
        """
        if self.status == TaskStatus.DONE:
            raise ValueError("작업이 이미 완료되었습니다")
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.completion_notes = notes

    def is_overdue(self) -> bool:
        """작업이 기한 초과인지 확인한다."""
        return self.due_date is not None and self.due_date.is_overdue()
