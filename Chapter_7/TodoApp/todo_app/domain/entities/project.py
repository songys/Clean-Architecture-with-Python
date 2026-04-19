from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import BusinessRuleViolation
from todo_app.domain.value_objects import (
    ProjectType,
    TaskStatus,
    ProjectStatus,
)


@dataclass
class Project(Entity):
    """여러 작업을 포함하는 프로젝트."""

    INBOX_NAME = "INBOX"  # 특수 inbox 이름을 위한 클래스 상수

    name: str
    description: str = ""
    project_type: ProjectType = field(default=ProjectType.REGULAR)
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    # def __post_init__(self) -> None:
    #     # Only allow INBOX_NAME as project name if created via create_inbox()
    #     if self.name == self.INBOX_NAME:
    #         caller_frames = stack()
    #         create_inbox_called = any(frame.function == "create_inbox" for frame in caller_frames)
    #         if not create_inbox_called:
    #             raise BusinessRuleViolation(f"'{self.INBOX_NAME}' is a reserved name.")

    @classmethod
    def create_inbox(cls) -> "Project":
        return cls(
            name="INBOX",
            description="할당되지 않은 작업을 위한 기본 프로젝트",
            project_type=ProjectType.INBOX,
        )

    def add_task(self, task: Task) -> None:
        """프로젝트에 작업을 추가한다."""
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("완료된 프로젝트에는 작업을 추가할 수 없다")
        self._tasks[task.id] = task
        task.project_id = self.id

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """ID로 작업을 가져온다."""
        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
        """프로젝트의 모든 작업을 가져온다."""
        return list(self._tasks.values())

    @property
    def incomplete_tasks(self) -> list[Task]:
        """프로젝트의 모든 미완료 작업을 가져온다."""
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def mark_completed(self, notes: Optional[str] = None) -> None:
        """
        프로젝트를 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모
        """
        if self.project_type == ProjectType.INBOX:
            raise BusinessRuleViolation("INBOX 프로젝트는 완료할 수 없다")
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
        self.completion_notes = notes
