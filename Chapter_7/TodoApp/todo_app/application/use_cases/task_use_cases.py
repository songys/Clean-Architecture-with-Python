"""
이 모듈은 작업 관련 유스 케이스를 포함한다.
"""

from copy import deepcopy
from dataclasses import dataclass
from uuid import UUID

from todo_app.application.dtos.operations import DeletionOutcome
from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.task_dtos import (
    CompleteTaskRequest,
    CreateTaskRequest,
    TaskResponse,
    UpdateTaskRequest,
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
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    TaskNotFoundError,
    ProjectNotFoundError,
    ValidationError,
    BusinessRuleViolation,
)
from todo_app.domain.value_objects import Priority


@dataclass
class CompleteTaskUseCase:
    """작업을 완료로 표시하고 이해관계자에게 알리는 유스 케이스."""

    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: CompleteTaskRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            task = self.task_repository.get(params["task_id"])

            # 초기 상태의 스냅샷 생성
            task_snapshot = deepcopy(task)

            try:
                task.complete(notes=params["completion_notes"])
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)

                return Result.success(TaskResponse.from_entity(task))

            except (ValidationError, BusinessRuleViolation) as e:
                # 작업 상태 복원
                self.task_repository.save(task_snapshot)
                raise  # 외부 try 블록에서 잡히도록 예외를 다시 발생시킨다

        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class CreateTaskUseCase:
    task_repository: TaskRepository
    project_repository: ProjectRepository

    def execute(self, request: CreateTaskRequest) -> Result:
        try:
            params = request.to_execution_params()
            project_id = params.get("project_id")

            if not project_id:
                project_id = self.project_repository.get_inbox().id
            else:
                self.project_repository.get(project_id)  # 존재 여부 확인

            task = Task(
                title=params["title"],
                description=params["description"],
                project_id=project_id,
                due_date=params.get("deadline"),
                priority=params.get("priority", Priority.MEDIUM),
            )
            self.task_repository.save(task)
            return Result.success(TaskResponse.from_entity(task))

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(project_id)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class GetTaskUseCase:
    """작업 세부 정보 조회를 위한 유스 케이스."""

    task_repository: TaskRepository

    def execute(self, task_id: UUID) -> Result[TaskResponse]:
        """
        특정 작업의 세부 정보를 가져온다.

        Args:
            task_id: 작업의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 Result:
            - 성공: 작업 세부 정보가 포함된 TaskResponse
            - 실패: 오류 정보
        """
        try:
            task = self.task_repository.get(task_id)
            return Result.success(TaskResponse.from_entity(task))
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(task_id)))


@dataclass
class UpdateTaskUseCase:
    """작업 세부 정보 업데이트를 위한 유스 케이스."""

    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: UpdateTaskRequest) -> Result[TaskResponse]:
        try:
            params = request.to_execution_params()
            task = self.task_repository.get(params["task_id"])

            if params.get("title") is not None:
                task.title = params["title"]
            if params.get("description") is not None:
                task.description = params["description"]
            if params.get("status") is not None:
                task.status = params["status"]
            if params.get("priority") is not None:
                task.priority = params["priority"]
                if task.priority == Priority.HIGH:
                    self.notification_service.notify_task_high_priority(task)
            if "deadline" in params:
                task.due_date = params["deadline"]

            self.task_repository.save(task)
            return Result.success(TaskResponse.from_entity(task))

        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class DeleteTaskUseCase:
    """작업 삭제를 위한 유스 케이스."""

    task_repository: TaskRepository

    def execute(self, task_id: UUID) -> Result[DeletionOutcome]:
        """유스 케이스를 실행한다.

        Args:
            task_id: 삭제할 작업의 고유 식별자

        Returns:
            성공 시 DeletionResult를 포함하는 Result
        """
        try:
            # 삭제 전 작업 존재 여부 확인
            self.task_repository.get(task_id)
            self.task_repository.delete(task_id)
            return Result.success(DeletionOutcome(task_id))
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(task_id)))
