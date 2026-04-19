"""
이 모듈은 프로젝트 연산을 위한 유스 케이스를 포함한다.
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


@dataclass
class CreateProjectUseCase:
    """새 프로젝트를 생성하는 유스 케이스."""

    project_repository: ProjectRepository

    def execute(self, request: CreateProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()

            project = Project(name=params["name"], description=params["description"])

            self.project_repository.save(project)

            return Result.success(ProjectResponse.from_entity(project))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
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
            project = self.project_repository.get(params["project_id"])

            # 초기 상태의 스냅샷 생성
            project_snapshot = deepcopy(project)
            task_snapshots = {task.id: deepcopy(task) for task in project.incomplete_tasks}

            try:
                # 미완료 작업 모두 완료
                for task in project.incomplete_tasks:
                    task.complete()
                    self.task_repository.save(task)

                project.mark_completed(
                    notes=params["completion_notes"],
                )

                self.project_repository.save(project)
                for task in project_snapshot.incomplete_tasks:
                    self.notification_service.notify_task_completed(task)
                return Result.success(CompleteProjectResponse.from_entity(project))

            except (ValidationError, BusinessRuleViolation) as e:
                # 프로젝트 상태 복원
                for task_id, task_snapshot in task_snapshots.items():
                    self.task_repository.save(task_snapshot)
                self.project_repository.save(project_snapshot)
                raise  # 외부 try 블록에서 잡히도록 예외를 다시 발생시킨다

        except ProjectNotFoundError:
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
            project = self.project_repository.get(UUID(project_id))
            return Result.success(ProjectResponse.from_entity(project))
        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", project_id))


@dataclass
class ListProjectsUseCase:
    project_repository: ProjectRepository

    def execute(self) -> Result[list[ProjectResponse]]:
        """
        모든 프로젝트를 나열한다.

        Returns:
            다음 중 하나를 포함하는 Result:
            - 성공: ProjectResponse 객체의 리스트
            - 실패: 오류 정보
        """
        try:
            projects = self.project_repository.get_all()
            return Result.success([ProjectResponse.from_entity(p) for p in projects])
        except Exception as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class UpdateProjectUseCase:
    """프로젝트를 업데이트하는 유스 케이스."""

    project_repository: ProjectRepository

    def execute(self, request: UpdateProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            project = self.project_repository.get(params["project_id"])

            # INBOX 프로젝트 편집 방지
            if project.project_type == ProjectType.INBOX:
                return Result.failure(
                    Error.business_rule_violation("INBOX 프로젝트는 수정할 수 없습니다")
                )

            if params["name"] is not None:
                project.name = params["name"]
            if params["description"] is not None:
                project.description = params["description"]

            self.project_repository.save(project)
            return Result.success(ProjectResponse.from_entity(project))

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
