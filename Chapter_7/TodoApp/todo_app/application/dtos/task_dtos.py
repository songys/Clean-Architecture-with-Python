"""
이 모듈은 작업 관련 요청 및 응답 데이터 전송 객체(DTO)를 포함한다.
이 DTO들은 외부 계층과 애플리케이션 핵심 간의 데이터 변환을 처리한다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self
from uuid import UUID
from dateutil import tz
from datetime import timezone

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Deadline, Priority, TaskStatus


@dataclass(frozen=True)
class CompleteTaskRequest:
    """작업 완료를 위한 요청 데이터."""

    task_id: str
    completion_notes: Optional[str] = None

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("Task ID is required")
        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValueError("Completion notes cannot exceed 1000 characters")
        try:
            UUID(self.task_id)
        except ValueError:
            raise ValueError("Invalid task ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 파라미터로 변환한다."""
        return {
            "task_id": UUID(self.task_id),
            "completion_notes": self.completion_notes,
        }


@dataclass
class CreateTaskRequest:
    """새 작업 생성을 위한 요청 데이터."""

    title: str
    description: str
    due_date: Optional[str] = None
    priority: Optional[str] = None
    project_id: Optional[str] = None

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.title.strip():
            raise ValueError("Title is required")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        if len(self.description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")
        if self.project_id:
            try:
                UUID(self.project_id)
            except ValueError:
                raise ValueError("Invalid project ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 파라미터로 변환한다."""
        params = {
            "title": self.title.strip(),
            "description": self.description.strip(),
        }

        if self.due_date:
            # UTC 기준 시간대 인식 datetime 생성
            dt = datetime.fromisoformat(self.due_date)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=tz.tzutc())
            params["deadline"] = Deadline(dt)

        if self.priority:
            params["priority"] = Priority[self.priority.upper()]

        if self.project_id:
            params["project_id"] = UUID(self.project_id)

        return params


@dataclass(frozen=True)
class TaskResponse:
    """도메인->애플리케이션 경계를 넘기 위한 응답 데이터."""

    id: str  # 경계 통과를 위해 UUID 변환 필요
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    project_id: str  # 경계 통과를 위해 UUID 변환 필요
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    completion_notes: Optional[str] = None

    @classmethod
    def from_entity(cls, task: Task) -> Self:
        """Task 엔터티에서 응답을 생성한다."""
        return cls(
            id=str(task.id),  # 경계 통과를 위한 기본 변환
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date.due_date if task.due_date else None,
            project_id=str(task.project_id),
            completion_date=task.completed_at,
            completion_notes=task.completion_notes,
        )


@dataclass(frozen=True)
class SetTaskPriorityRequest:
    """작업 우선순위 업데이트를 위한 요청 데이터."""

    task_id: str
    priority: str

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("Task ID is required")

        try:
            priority_value = self.priority.strip().upper()
            if not priority_value:
                raise ValueError
            if priority_value not in [p.name for p in Priority]:
                raise ValueError
        except (AttributeError, ValueError):
            raise ValueError(f"Priority must be one of: {', '.join(p.name for p in Priority)}")
        try:
            UUID(self.task_id)
        except ValueError:
            raise ValueError("Invalid task ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 파라미터로 변환한다."""
        return {
            "task_id": UUID(self.task_id),
            "priority": Priority[self.priority.upper()],
        }


@dataclass(frozen=True)
class UpdateTaskRequest:
    """작업 업데이트를 위한 요청 데이터."""

    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[str] = None

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("Task ID is required")
        if self.title is not None:
            if not self.title.strip():
                raise ValueError("Title cannot be empty")
            if len(self.title) > 200:
                raise ValueError("Title cannot exceed 200 characters")
        if self.description is not None and len(self.description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")
        if self.due_date:
            try:
                datetime.fromisoformat(self.due_date)
            except ValueError:
                raise ValueError("Invalid due date format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 파라미터로 변환한다."""
        params = {"task_id": UUID(self.task_id)}

        if self.title is not None:
            params["title"] = self.title.strip()
        if self.description is not None:
            params["description"] = self.description.strip()
        if self.status is not None:
            params["status"] = self.status
        if self.priority is not None:
            params["priority"] = self.priority
        # due_date가 제공된 경우 항상 deadline을 params에 포함
        if self.due_date is not None:
            if self.due_date:  # 비어있지 않은 문자열
                dt = datetime.fromisoformat(self.due_date)
                if not dt.tzinfo:
                    dt = dt.replace(tzinfo=timezone.utc)
                params["deadline"] = Deadline(dt)
            else:  # 빈 문자열 - 마감일 삭제
                params["deadline"] = None

        return params
