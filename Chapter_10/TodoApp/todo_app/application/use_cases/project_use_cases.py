"""
애플리케이션 계층의 프로젝트 관련 유스 케이스 모듈.
- 프로젝트 CRUD, 완료 처리 등 비즈니스 작업 캡슐화
- 구조화된 로깅으로 모든 비즈니스 운영의 추적 가능
- 스냅샷 패턴으로 프로젝트 완료 실패 시 원본 상태 복원
"""

from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

from todo_app.domain.value_objects import ProjectType
from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.project_dtos import (
    CreateProjectRequest,
    ProjectResponse,
    CompleteProjectRequest,
    CompleteProjectResponse,
    UpdateProjectRequest,
)
from todo_app.application.service_ports.notifications import (
    NotificationPort,
)
from todo_app.application.repositories.project_repository import (
    ProjectRepository,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.exceptions import (
    ValidationError,
    BusinessRuleViolation,
    ProjectNotFoundError,
)

import logging

logger = logging.getLogger(__name__)


@dataclass
class CreateProjectUseCase:
    """새 프로젝트를 생성하는 유스 케이스."""

    project_repository: ProjectRepository

    def execute(self, request: CreateProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            logger.info("Creating new project", extra={"context": {"name": params["name"]}})

            project = Project(name=params["name"], description=params["description"])
            self.project_repository.save(project)

            logger.info(
                "Project created successfully",
                extra={"context": {"project_id": str(project.id), "name": project.name}},
            )
            return Result.success(ProjectResponse.from_entity(project))

        except ValidationError as e:
            logger.error("Validation error creating project", extra={"context": {"error": str(e)}})
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            logger.error("Business rule violation creating project", extra={"context": {"error": str(e)}})
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class CompleteProjectUseCase:
    """프로젝트를 완료로 표시하는 유스 케이스."""

    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: CompleteProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            logger.info("Completing project", extra={"context": {"project_id": str(params["project_id"])}})
            project = self.project_repository.get(params["project_id"])

            # 초기 상태의 스냅샷 생성
            project_snapshot = deepcopy(project)
            task_snapshots = {task.id: deepcopy(task) for task in project.incomplete_tasks}

            try:
                # 모든 미완료 작업 완료
                for task in project.incomplete_tasks:
                    task.complete()
                    self.task_repository.save(task)

                project.mark_completed(notes=params["completion_notes"])
                self.project_repository.save(project)

                for task in project_snapshot.incomplete_tasks:
                    self.notification_service.notify_task_completed(task)

                logger.info(
                    "Project completed successfully",
                    extra={
                        "context": {
                            "project_id": str(project.id),
                            "tasks_completed": len(project_snapshot.incomplete_tasks),
                        }
                    },
                )
                return Result.success(CompleteProjectResponse.from_entity(project))

            except (ValidationError, BusinessRuleViolation) as e:
                # 프로젝트 상태 복원
                logger.error(
                    "Failed to complete project",
                    extra={"context": {"project_id": str(project.id), "error": str(e)}},
                )
                for task_id, task_snapshot in task_snapshots.items():
                    self.task_repository.save(task_snapshot)
                self.project_repository.save(project_snapshot)
                raise  # 외부 try 블록에서 잡히도록 예외를 다시 발생시킴

        except ProjectNotFoundError:
            logger.error(
                "Project not found",
                extra={"context": {"project_id": str(params["project_id"])}},
            )
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class GetProjectUseCase:
    """프로젝트 상세 정보를 조회하는 유스 케이스."""

    project_repository: ProjectRepository

    def execute(self, project_id: str) -> Result[ProjectResponse]:
        """
        특정 프로젝트의 상세 정보를 가져온다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 Result:
            - 성공: 프로젝트 상세 정보가 담긴 ProjectResponse
            - 실패: 오류 정보
        """
        try:
            logger.info("Retrieving project details", extra={"context": {"project_id": project_id}})
            project = self.project_repository.get(UUID(project_id))
            return Result.success(ProjectResponse.from_entity(project))
        except ProjectNotFoundError:
            logger.error("Project not found", extra={"context": {"project_id": project_id}})
            return Result.failure(Error.not_found("Project", project_id))


@dataclass
class ListProjectsUseCase:
    project_repository: ProjectRepository

    def execute(self) -> Result[list[ProjectResponse]]:
        """
        모든 프로젝트를 나열한다.

        Returns:
            다음 중 하나를 포함하는 Result:
            - 성공: ProjectResponse 객체 목록
            - 실패: 오류 정보
        """
        try:
            logger.info("Retrieving all projects")
            projects = self.project_repository.get_all()
            logger.info("Projects retrieved successfully", extra={"context": {"count": len(projects)}})
            return Result.success([ProjectResponse.from_entity(p) for p in projects])
        except Exception as e:
            logger.error("Failed to retrieve projects", extra={"context": {"error": str(e)}})
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class UpdateProjectUseCase:
    """프로젝트를 업데이트하는 유스 케이스."""

    project_repository: ProjectRepository

    def execute(self, request: UpdateProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            logger.info("Updating project", extra={"context": {"project_id": str(params["project_id"])}})
            project = self.project_repository.get(params["project_id"])

            # INBOX 프로젝트 편집 방지
            if project.project_type == ProjectType.INBOX:
                logger.warning(
                    "Attempted to modify INBOX project",
                    extra={"context": {"project_id": str(project.id)}},
                )
                return Result.failure(
                    Error.business_rule_violation("INBOX 프로젝트는 수정할 수 없습니다")
                )

            updated_fields = []
            if params["name"] is not None:
                project.name = params["name"]
                updated_fields.append("name")
            if params["description"] is not None:
                project.description = params["description"]
                updated_fields.append("description")

            self.project_repository.save(project)
            logger.info(
                "Project updated successfully",
                extra={
                    "context": {
                        "project_id": str(project.id),
                        "updated_fields": updated_fields,
                    }
                },
            )
            return Result.success(ProjectResponse.from_entity(project))

        except ProjectNotFoundError:
            logger.error(
                "Project not found",
                extra={"context": {"project_id": str(params["project_id"])}},
            )
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            logger.error(
                "Validation error updating project",
                extra={"context": {"project_id": str(params["project_id"]), "error": str(e)}},
            )
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            logger.error(
                "Business rule violation updating project",
                extra={"context": {"project_id": str(params["project_id"]), "error": str(e)}},
            )
            return Result.failure(Error.business_rule_violation(str(e)))
