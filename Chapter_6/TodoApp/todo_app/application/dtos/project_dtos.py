"""
이 모듈은 프로젝트 작업을 위한 요청 및 응답 데이터 전송 객체(DTO)를 포함한다.
이러한 DTO는 외부 계층과 애플리케이션 코어 간의 데이터 변환을 처리한다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence, Self
from uuid import UUID

from todo_app.domain.exceptions import BusinessRuleViolation
from todo_app.domain.value_objects import ProjectStatus
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.domain.entities.project import Project


# 프로젝트 생성을 위한 요청 DTO - 외부 입력을 검증하고 유스케이스 형식으로 변환
@dataclass(frozen=True)
class CreateProjectRequest:
    """새로운 프로젝트를 생성하기 위한 요청 데이터"""

    name: str  # 프로젝트 이름 (필수)
    description: str = ""  # 프로젝트 설명 (선택, 기본값 빈 문자열)

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.name.strip():
            raise ValueError("Project name is required")
        if len(self.name) > 100:
            raise ValueError("Project name cannot exceed 100 characters")
        if len(self.description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 실행에 필요한 파라미터로 변환"""
        return {
            "name": self.name.strip(),
            "description": self.description.strip(),
        }


# 프로젝트 완료를 위한 요청 DTO
@dataclass(frozen=True)
class CompleteProjectRequest:
    """프로젝트를 완료하기 위한 요청 데이터"""

    project_id: str  # 완료할 프로젝트의 ID (문자열 형태의 UUID)
    completion_notes: Optional[str] = None  # 선택적 완료 메모

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.project_id.strip():
            raise ValueError("Project ID is required")
        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValueError("Completion notes cannot exceed 1000 characters")
        try:
            UUID(self.project_id)
        except ValueError:
            raise ValueError("Invalid project ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 실행에 필요한 파라미터로 변환"""
        return {
            "project_id": UUID(self.project_id),
            "completion_notes": self.completion_notes,
        }


# 프로젝트 유스케이스 실행 결과를 외부 계층에 전달하기 위한 응답 DTO
@dataclass(frozen=True)
class ProjectResponse:
    """기본 프로젝트 작업에 대한 응답 데이터"""

    id: str
    name: str
    description: str
    status: ProjectStatus
    completion_date: Optional[datetime]
    tasks: Sequence[TaskResponse]  # 프로젝트에 속한 작업들의 응답 목록

    # 도메인 엔터티(Project)로부터 응답 DTO를 생성하는 팩토리 메서드
    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """Project 엔터티로부터 응답을 생성한다."""
        return cls(
            id=str(project.id),
            name=project.name,
            description=project.description,
            status=project.status,
            completion_date=project.completed_at if project.completed_at else None,
            tasks=[TaskResponse.from_entity(task) for task in project.tasks],
        )


# 프로젝트 완료 결과에 특화된 응답 DTO - 완료 관련 정보만 선별하여 전달
@dataclass(frozen=True)
class CompleteProjectResponse:
    """프로젝트 완료에 특화된 응답 데이터"""

    id: str
    status: ProjectStatus
    completion_date: datetime
    task_count: int  # 프로젝트에 포함된 작업 수
    completion_notes: Optional[str]

    @classmethod
    def from_entity(cls, project: Project) -> Self:
        """Project 엔터티로부터 응답을 생성한다."""
        if project.completed_at is None:
            raise BusinessRuleViolation("Project does not have a completion date")
        return cls(
            id=str(project.id),
            status=project.status,
            completion_date=project.completed_at,
            task_count=len(project.tasks),
            completion_notes=project.completion_notes,
        )
