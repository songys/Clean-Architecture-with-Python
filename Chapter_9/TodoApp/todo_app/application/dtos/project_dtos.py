"""
이 모듈은 프로젝트 연산을 위한 요청 및 응답 데이터 전송 객체(DTO)를 포함한다.
이 DTO들은 외부 계층과 애플리케이션 핵심 간의 데이터 변환을 처리한다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence, Self
from uuid import UUID

from todo_app.domain.exceptions import BusinessRuleViolation
from todo_app.domain.value_objects import ProjectStatus, ProjectType
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.domain.entities.project import Project


@dataclass(frozen=True)
class CreateProjectRequest:
    """새 프로젝트 생성을 위한 요청 데이터."""

    name: str
    description: str = ""

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.name.strip():
            raise ValueError("프로젝트 이름은 필수입니다")
        if len(self.name) > 100:
            raise ValueError("프로젝트 이름은 100자를 초과할 수 없습니다")
        if len(self.description) > 2000:
            raise ValueError("설명은 2000자를 초과할 수 없습니다")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        return {
            "name": self.name.strip(),
            "description": self.description.strip(),
        }


@dataclass(frozen=True)
class CompleteProjectRequest:
    """프로젝트 완료를 위한 요청 데이터."""

    project_id: str
    completion_notes: Optional[str] = None

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.project_id.strip():
            raise ValueError("프로젝트 ID는 필수입니다")
        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValueError("완료 메모는 1000자를 초과할 수 없습니다")
        try:
            UUID(self.project_id)
        except ValueError:
            raise ValueError("잘못된 프로젝트 ID 형식입니다")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        return {
            "project_id": UUID(self.project_id),
            "completion_notes": self.completion_notes,
        }


@dataclass(frozen=True)
class ProjectResponse:
    """기본 프로젝트 연산의 응답 데이터."""

    id: str
    name: str
    description: str
    status: ProjectStatus
    project_type: ProjectType
    completion_date: Optional[datetime]
    tasks: Sequence[TaskResponse]

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """Project 엔터티로부터 응답을 생성한다."""
        return cls(
            id=str(project.id),
            name=project.name,
            description=project.description,
            status=project.status,
            project_type=project.project_type,
            completion_date=project.completed_at if project.completed_at else None,
            tasks=[TaskResponse.from_entity(task) for task in project.tasks],
        )


@dataclass(frozen=True)
class CompleteProjectResponse:
    """프로젝트 완료에 특화된 응답 데이터."""

    id: str
    status: ProjectStatus
    completion_date: datetime
    task_count: int
    completion_notes: Optional[str]

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """Project 엔터티로부터 응답을 생성한다."""
        if project.completed_at is None:
            raise BusinessRuleViolation("프로젝트에 완료 날짜가 없습니다")
        return cls(
            id=str(project.id),
            status=project.status,
            completion_date=project.completed_at,
            task_count=len(project.tasks),
            completion_notes=project.completion_notes,
        )


@dataclass
class UpdateProjectRequest:
    """프로젝트 업데이트를 위한 요청 데이터."""

    project_id: str
    name: Optional[str] = None
    description: Optional[str] = None

    def to_execution_params(self) -> dict:
        """실행 매개변수로 변환한다."""
        return {
            "project_id": UUID(self.project_id),
            "name": self.name,
            "description": self.description,
        }
