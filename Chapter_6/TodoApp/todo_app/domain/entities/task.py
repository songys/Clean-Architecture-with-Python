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


# 할 일 도메인의 핵심 엔터티 - 비즈니스 규칙과 상태 전환 로직을 캡슐화
@dataclass
class Task(Entity):
    """완료해야 하는 작업"""

    title: str  # 작업 제목 (필수)
    description: str  # 작업 설명 (필수)
    due_date: Optional[Deadline] = None  # 마감일 값 객체 (선택)
    priority: Priority = Priority.MEDIUM  # 우선순위 (기본값: MEDIUM)
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)  # 작업 상태 (초기값: TODO)
    completed_at: Optional[datetime] = field(default=None, init=False)  # 완료 일시
    completion_notes: Optional[str] = field(default=None, init=False)  # 완료 메모
    project_id: Optional[UUID] = field(default=None, init=False)  # 소속 프로젝트 ID

    def start(self) -> None:
        """작업을 진행 중으로 표시한다."""
        if self.status != TaskStatus.TODO:
            raise ValueError("'TODO' 상태인 작업만 시작할 수 있다")
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
            raise ValueError("작업이 이미 완료되었다")
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.completion_notes = notes

    def is_overdue(self) -> bool:
        """작업이 기한을 초과했는지 확인한다."""
        return self.due_date is not None and self.due_date.is_overdue()
