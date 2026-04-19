# todo_app/tests/application/conftest.py
"""애플리케이션 계층 테스트를 위한 테스트 픽스처와 유틸리티."""

from dataclasses import dataclass
from typing import Sequence
from uuid import UUID

from todo_app.application.repositories.project_repository import (
    ProjectRepository,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.application.service_ports.notifications import (
    NotificationPort,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    TaskNotFoundError,
    ProjectNotFoundError,
)
from todo_app.domain.value_objects import TaskStatus


@dataclass
class InMemoryTaskRepository(TaskRepository):
    """테스트를 위한 TaskRepository의 인메모리 구현."""

    _tasks: dict[UUID, Task]

    def __init__(self) -> None:
        self._tasks = {}

    def get(self, task_id: UUID) -> Task:
        if task := self._tasks.get(task_id):
            return task
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:
        self._tasks.pop(task_id, None)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        return [task for task in self._tasks.values() if task.project_id == project_id]

    def get_active_tasks(self) -> Sequence[Task]:
        return [task for task in self._tasks.values() if task.status != TaskStatus.DONE]


@dataclass
class InMemoryProjectRepository(ProjectRepository):
    """테스트를 위한 ProjectRepository의 인메모리 구현."""

    _projects: dict[UUID, Project]

    def __init__(self) -> None:
        self._projects = {}

    def get(self, project_id: UUID) -> Project:
        if project := self._projects.get(project_id):
            return project
        raise ProjectNotFoundError(project_id)

    def save(self, project: Project) -> None:
        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:
        self._projects.pop(project_id, None)


@dataclass
class NotificationRecorder(NotificationPort):
    """테스트 검증을 위한 알림을 기록한다."""

    completed_tasks: list[UUID]
    high_priority_tasks: list[UUID]
    deadline_warnings: list[tuple[UUID, int]]

    def __init__(self) -> None:
        self.completed_tasks = []
        self.high_priority_tasks = []
        self.deadline_warnings = []

    def notify_task_completed(self, task: Task) -> None:
        self.completed_tasks.append(task.id)

    def notify_task_high_priority(self, task: Task) -> None:
        self.high_priority_tasks.append(task.id)

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        self.deadline_warnings.append((task.id, days_remaining))
