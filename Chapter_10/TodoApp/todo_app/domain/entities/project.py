# 도메인 계층의 Project 엔터티
# - 작업(Task)을 그룹화하는 애그리게이트 루트
# - INBOX 프로젝트: 미할당 작업을 위한 특수 프로젝트 (삭제/완료 불가)
# - 비즈니스 규칙(완료 처리, INBOX 보호)을 엔터티 내부에 캡슐화
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

import logging

# 모듈 단위 로거 (프레임워크 독립적)
logger = logging.getLogger(__name__)


@dataclass
class Project(Entity):
    """여러 작업을 포함하는 프로젝트 (애그리게이트 루트)."""

    INBOX_NAME = "INBOX"  # 특별한 인박스 이름을 위한 클래스 상수

    name: str
    description: str = ""
    project_type: ProjectType = field(default=ProjectType.REGULAR)
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    @classmethod
    def create_inbox(cls) -> "Project":
        logger.info("Creating INBOX project")
        return cls(
            name="INBOX",
            description="미할당 작업을 위한 기본 프로젝트",
            project_type=ProjectType.INBOX,
        )

    def add_task(self, task: Task) -> None:
        """프로젝트에 작업을 추가한다."""
        if self.status == ProjectStatus.COMPLETED:
            logger.error(
                "Attempted to add task to completed project",
                extra={
                    "context": {
                        "project_id": str(self.id),
                        "project_name": self.name,
                        "task_id": str(task.id),
                    }
                },
            )
            raise ValueError("완료된 프로젝트에는 작업을 추가할 수 없습니다")
            
        logger.info(
            "Adding task to project",
            extra={
                "context": {
                    "project_id": str(self.id),
                    "project_name": self.name,
                    "task_id": str(task.id),
                    "task_title": task.title,
                }
            },
        )
        self._tasks[task.id] = task
        task.project_id = self.id

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """ID로 작업을 가져온다."""
        task = self._tasks.get(task_id)
        if task is None:
            logger.warning(
                "Task not found in project",
                extra={
                    "context": {
                        "project_id": str(self.id),
                        "project_name": self.name,
                        "task_id": str(task_id),
                    }
                },
            )
        return task

    @property
    def tasks(self) -> list[Task]:
        """프로젝트의 모든 작업을 가져온다."""
        logger.debug(
            "Retrieving all tasks from project",
            extra={
                "context": {
                    "project_id": str(self.id),
                    "project_name": self.name,
                    "task_count": len(self._tasks),
                }
            },
        )
        return list(self._tasks.values())

    @property
    def incomplete_tasks(self) -> list[Task]:
        """프로젝트의 모든 미완료 작업을 가져온다."""
        incomplete = [task for task in self.tasks if task.status != TaskStatus.DONE]
        logger.debug(
            "Retrieving incomplete tasks from project",
            extra={
                "context": {
                    "project_id": str(self.id),
                    "project_name": self.name,
                    "incomplete_count": len(incomplete),
                    "total_count": len(self._tasks),
                }
            },
        )
        return incomplete

    def mark_completed(self, notes: Optional[str] = None) -> None:
        """
        프로젝트를 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모
        """
        if self.project_type == ProjectType.INBOX:
            logger.error(
                "Attempted to complete INBOX project",
                extra={
                    "context": {
                        "project_id": str(self.id),
                        "project_name": self.name,
                    }
                },
            )
            raise BusinessRuleViolation("INBOX 프로젝트는 완료할 수 없습니다")
            
        logger.info(
            "Marking project as completed",
            extra={
                "context": {
                    "project_id": str(self.id),
                    "project_name": self.name,
                    "incomplete_tasks": len(self.incomplete_tasks),
                }
            },
        )
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
        self.completion_notes = notes
