"""
애플리케이션 계층의 작업 관련 유스 케이스 모듈.
- 각 유스 케이스는 하나의 비즈니스 작업을 캡슐화 (단일 책임 원칙)
- 표준 logging 모듈을 사용한 프레임워크 독립적 구조화 로깅
- 작업 시작/완료 시점에 비즈니스 컨텍스트를 포함한 로그 기록
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

import logging

# 모듈 단위 로거 (로거 이름이 모듈 경로를 자동 반영하여 로그 출처 추적 가능)
logger = logging.getLogger(__name__)


@dataclass
class CompleteTaskUseCase:
    """작업을 완료로 표시하고 관계자에게 알림을 보내는 유스 케이스.
    - 스냅샷 패턴으로 실패 시 원본 상태 복원 지원
    """

    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: CompleteTaskRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            logger.info("Completing task", extra={"context": {"task_id": str(params["task_id"])}})
            task = self.task_repository.get(params["task_id"])

            # 초기 상태의 스냅샷 생성
            task_snapshot = deepcopy(task)

            try:
                task.complete(notes=params["completion_notes"])
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)

                logger.info(
                    "Task completed successfully",
                    extra={
                        "context": {
                            "task_id": str(task.id),
                            "completion_notes": params["completion_notes"],
                        }
                    },
                )
                return Result.success(TaskResponse.from_entity(task))

            except (ValidationError, BusinessRuleViolation) as e:
                # 작업 상태 복원
                logger.error(
                    "Failed to complete task",
                    extra={"context": {"task_id": str(task.id), "error": str(e)}},
                )
                self.task_repository.save(task_snapshot)
                raise  # 외부 try 블록에서 잡히도록 예외를 다시 발생시킴

        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(params["task_id"])}})
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class CreateTaskUseCase:
    """새 작업을 생성하는 유스 케이스.
    - 프로젝트 미지정 시 INBOX 프로젝트에 자동 할당
    - 구조화된 로깅으로 작업 생성 과정의 추적 가능
    """
    task_repository: TaskRepository
    project_repository: ProjectRepository

    def execute(self, request: CreateTaskRequest) -> Result:
        try:
            # 작업 시작 시점 로깅 (입력 데이터를 비즈니스 컨텍스트로 기록)
            logger.info(
                "Creating new task",
                extra={"context": {"title": request.title, "project_id": request.project_id}},
            )

            params = request.to_execution_params()
            project_id = params.get("project_id")

            if not project_id:
                project_id = self.project_repository.get_inbox().id
            else:
                try:
                    self.project_repository.get(project_id)  # 존재 여부 확인
                except ProjectNotFoundError:
                    logger.error(
                        "Project not found", extra={"context": {"project_id": str(project_id)}}
                    )
                    return Result.failure(Error.not_found("Project", str(project_id)))

            task = Task(
                title=params["title"],
                description=params["description"],
                project_id=project_id,
                due_date=params.get("deadline"),
                priority=params.get("priority", Priority.MEDIUM),
            )

            self.task_repository.save(task)

            logger.info(
                "Task created successfully",
                extra={
                    "context": {
                        "task_id": str(task.id),
                        "project_id": str(project_id),
                        "title": task.title,
                        "priority": task.priority.name,
                    }
                },
            )

            return Result.success(TaskResponse.from_entity(task))

        except ValidationError as e:
            logger.error("Task creation validation error", extra={"context": {"error": str(e)}})
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            logger.error(
                "Task creation business rule violation", extra={"context": {"error": str(e)}}
            )
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class GetTaskUseCase:
    """작업 상세 정보를 조회하는 유스 케이스."""

    task_repository: TaskRepository

    def execute(self, task_id: UUID) -> Result:
        """
        특정 작업의 상세 정보를 가져온다.

        Args:
            task_id: 작업의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 Result:
            - 성공: 작업 상세 정보가 담긴 TaskResponse
            - 실패: 오류 정보
        """
        try:
            logger.info("Retrieving task details", extra={"context": {"task_id": str(task_id)}})
            task = self.task_repository.get(task_id)
            return Result.success(TaskResponse.from_entity(task))
        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(task_id)}})
            return Result.failure(Error.not_found("Task", str(task_id)))


@dataclass
class UpdateTaskUseCase:
    """작업 상세 정보를 업데이트하는 유스 케이스."""

    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: UpdateTaskRequest) -> Result:
        try:
            params = request.to_execution_params()
            logger.info("Updating task", extra={"context": {"task_id": str(params["task_id"])}})
            task = self.task_repository.get(params["task_id"])

            # 초기 상태의 스냅샷 생성
            task_snapshot = deepcopy(task)

            try:
                if "title" in params:
                    task.update_title(params["title"])
                if "description" in params:
                    task.update_description(params["description"])
                if "priority" in params:
                    task.update_priority(Priority(params["priority"]))
                if "due_date" in params:
                    task.update_due_date(params["due_date"])

                self.task_repository.save(task)
                logger.info(
                    "Task updated successfully",
                    extra={
                        "context": {
                            "task_id": str(task.id),
                            "updated_fields": [k for k in params.keys() if k != "task_id"],
                        }
                    },
                )
                return Result.success(TaskResponse.from_entity(task))

            except (ValidationError, BusinessRuleViolation) as e:
                # 작업 상태 복원
                logger.error(
                    "Failed to update task",
                    extra={"context": {"task_id": str(task.id), "error": str(e)}},
                )
                self.task_repository.save(task_snapshot)
                raise

        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(params["task_id"])}})
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


@dataclass
class DeleteTaskUseCase:
    """작업을 삭제하는 유스 케이스."""

    task_repository: TaskRepository

    def execute(self, task_id: UUID) -> Result:
        """유스 케이스를 실행한다.

        Args:
            task_id: 삭제할 작업의 고유 식별자

        Returns:
            성공 시 DeletionResult를 포함하는 Result
        """
        try:
            logger.info("Deleting task", extra={"context": {"task_id": str(task_id)}})
            self.task_repository.get(task_id)  # 존재 여부 확인
            self.task_repository.delete(task_id)
            logger.info("Task deleted successfully", extra={"context": {"task_id": str(task_id)}})
            return Result.success(DeletionOutcome(task_id))
        except TaskNotFoundError:
            logger.error("Task not found", extra={"context": {"task_id": str(task_id)}})
            return Result.failure(Error.not_found("Task", str(task_id)))
