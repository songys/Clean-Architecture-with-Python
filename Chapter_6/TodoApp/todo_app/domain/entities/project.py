from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import (
    TaskStatus,
    ProjectStatus,
)


# 여러 작업을 그룹화하는 프로젝트 엔터티 - 작업 관리와 프로젝트 완료 로직 캡슐화
@dataclass
class Project(Entity):
    """여러 작업을 포함하는 프로젝트"""

    name: str  # 프로젝트 이름 (필수)
    description: str = ""  # 프로젝트 설명 (선택)
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)  # 프로젝트 상태
    completed_at: Optional[datetime] = field(default=None, init=False)  # 완료 일시
    completion_notes: Optional[str] = field(default=None, init=False)  # 완료 메모
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)  # 프로젝트에 속한 작업 목록

    def add_task(self, task: Task) -> None:
        """프로젝트에 작업을 추가한다."""
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("완료된 프로젝트에는 작업을 추가할 수 없다")
        self._tasks[task.id] = task
        task.project_id = self.id

    def remove_task(self, task_id: UUID) -> None:
        """프로젝트에서 작업을 제거한다."""
        if task := self._tasks.pop(task_id, None):
            task.project_id = None

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """ID를 기준으로 작업을 가져온다."""
        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
        """프로젝트의 모든 작업을 가져온다."""
        return list(self._tasks.values())

    @property
    def incomplete_tasks(self) -> list[Task]:
        """프로젝트에서 미완료된 모든 작업을 가져온다."""
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def mark_completed(self, notes: Optional[str] = None) -> None:
        """
        프로젝트를 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모
        """
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
        self.completion_notes = notes
