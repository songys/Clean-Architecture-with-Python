"""
이 모듈은 프로젝트 연산을 위한 요청 및 응답 데이터 전송 객체(DTO)를 포함한다.
이 DTO들은 외부 계층과 애플리케이션 핵심부 사이의 데이터 변환을 처리한다.
"""
# 프로젝트 관련 요청/응답 DTO 모음
# - 요청 DTO: 외부 입력 데이터의 검증 및 도메인 타입 변환 담당
# - 응답 DTO: 도메인 엔터티를 외부에 전달하기 적합한 형태로 변환 담당

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence, Self
from uuid import UUID

from todo_app.domain.exceptions import BusinessRuleViolation
from todo_app.domain.value_objects import ProjectStatus
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.domain.entities.project import Project


# 새 프로젝트 생성 요청 DTO - 이름과 설명의 유효성 검증
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

    # 검증된 데이터를 유스케이스 실행 매개변수로 변환하는 메서드
    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        return {
            "name": self.name.strip(),
            "description": self.description.strip(),
        }


# 프로젝트 완료 요청 DTO - 프로젝트 ID와 완료 메모의 유효성 검증
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

    # 문자열 형태의 project_id를 UUID 도메인 타입으로 변환하는 메서드
    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        return {
            "project_id": UUID(self.project_id),
            "completion_notes": self.completion_notes,
        }


# 기본 프로젝트 응답 DTO - 프로젝트 엔터티의 전체 정보를 외부에 전달
@dataclass(frozen=True)
class ProjectResponse:
    """기본 프로젝트 연산을 위한 응답 데이터."""

    id: str
    name: str
    description: str
    status: ProjectStatus
    completion_date: Optional[datetime]
    tasks: Sequence[TaskResponse]

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
            # 프로젝트 내 각 작업도 TaskResponse DTO로 변환
            tasks=[TaskResponse.from_entity(task) for task in project.tasks],
        )


# 프로젝트 완료에 특화된 응답 DTO - 완료 관련 핵심 정보만 포함
@dataclass(frozen=True)
class CompleteProjectResponse:
    """프로젝트 완료에 특화된 응답 데이터."""

    id: str
    status: ProjectStatus
    completion_date: datetime
    task_count: int
    completion_notes: Optional[str]

    # 도메인 엔터티에서 완료 응답 DTO를 생성하는 팩토리 메서드
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
