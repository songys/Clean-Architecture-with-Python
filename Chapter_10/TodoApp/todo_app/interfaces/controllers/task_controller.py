"""
인터페이스 어댑터 계층의 작업 컨트롤러 모듈.

컨트롤러의 책임:
1. 외부 소스(CLI, 웹 등)로부터 입력을 받는다
2. 해당 입력을 유스 케이스가 요구하는 형식(DTO)으로 변환한다
3. 적절한 유스 케이스를 실행한다
4. 결과를 인터페이스에 적합한 뷰 모델로 변환한다
5. 발생하는 오류를 처리하고 포맷한다

구조화된 로깅 적용:
- 모든 핸들러 메서드에 요청/성공/실패 시점 로깅
- extra["context"]에 비즈니스 컨텍스트 포함하여 추적 가능
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from todo_app.application.dtos.operations import DeletionOutcome
from todo_app.domain.value_objects import Priority
from todo_app.application.dtos.task_dtos import CompleteTaskRequest, CreateTaskRequest
from todo_app.application.use_cases.task_use_cases import CompleteTaskUseCase, CreateTaskUseCase
from todo_app.domain.value_objects import TaskStatus
from todo_app.interfaces.presenters.base import TaskPresenter
from todo_app.interfaces.view_models.base import OperationResult
from todo_app.application.dtos.task_dtos import UpdateTaskRequest
from todo_app.application.use_cases.task_use_cases import (
    DeleteTaskUseCase,
    GetTaskUseCase,
    UpdateTaskUseCase,
)
from todo_app.interfaces.view_models.task_vm import TaskViewModel

import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskController:
    """작업 관련 작업 컨트롤러.
    - 유스 케이스와 프레젠터를 의존성 주입으로 받아 인터페이스 독립성 유지
    - 원시 타입(str)을 받아 DTO로 변환 후 유스 케이스 실행
    - 결과를 프레젠터를 통해 뷰 모델(OperationResult)로 변환
    """

    # 의존성 주입을 통해 제공되는 유스 케이스 및 프레젠터
    create_use_case: CreateTaskUseCase
    get_use_case: GetTaskUseCase
    complete_use_case: CompleteTaskUseCase
    update_use_case: UpdateTaskUseCase
    delete_use_case: DeleteTaskUseCase
    presenter: TaskPresenter

    def handle_create(
        self,
        title: str,
        description: str,
        project_id: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> OperationResult[TaskViewModel]:
        try:
            logger.info(
                "Handling task creation request",
                extra={
                    "context": {
                        "title": title,
                        "project_id": project_id,
                        "priority": priority,
                    }
                },
            )
            request = CreateTaskRequest(
                title=title,
                description=description,
                project_id=project_id,
                priority=priority,
                due_date=due_date,
            )
            result = self.create_use_case.execute(request)
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                logger.info(
                    "Task creation handled successfully",
                    extra={"context": {"task_id": str(result.value.id)}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Task creation failed",
                extra={
                    "context": {
                        "title": title,
                        "error": result.error.message,
                        "error_code": str(result.error.code.name),
                    }
                },
            )
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            logger.error(
                "Validation error in task creation",
                extra={"context": {"title": title, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_get(self, task_id: str) -> OperationResult[TaskViewModel]:
        try:
            logger.info(
                "Handling task retrieval request",
                extra={"context": {"task_id": task_id}},
            )
            result = self.get_use_case.execute(UUID(task_id))
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                logger.info(
                    "Task retrieval handled successfully",
                    extra={"context": {"task_id": task_id}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Task retrieval failed",
                extra={
                    "context": {
                        "task_id": task_id,
                        "error": result.error.message,
                        "error_code": str(result.error.code.name),
                    }
                },
            )
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            logger.error(
                "Validation error in task retrieval",
                extra={"context": {"task_id": task_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(
        self, task_id: str, notes: Optional[str] = None
    ) -> OperationResult[TaskViewModel]:
        """작업 완료 요청을 처리한다."""
        try:
            logger.info(
                "Handling task completion request",
                extra={"context": {"task_id": task_id}},
            )
            request = CompleteTaskRequest(task_id=task_id, completion_notes=notes)
            result = self.complete_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                logger.info(
                    "Task completion handled successfully",
                    extra={"context": {"task_id": task_id}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Task completion failed",
                extra={
                    "context": {
                        "task_id": task_id,
                        "error": result.error.message,
                        "error_code": str(result.error.code.name),
                    }
                },
            )
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            logger.error(
                "Validation error in task completion",
                extra={"context": {"task_id": task_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_update(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> OperationResult[TaskViewModel]:
        try:
            logger.info(
                "Handling task update request",
                extra={
                    "context": {
                        "task_id": task_id,
                        "update_fields": [
                            f for f, v in [
                                ("title", title),
                                ("description", description),
                                ("status", status),
                                ("priority", priority),
                                ("due_date", due_date),
                            ] if v is not None
                        ],
                    }
                },
            )
            # 제공된 경우 문자열 상태/우선순위를 열거형으로 변환
            status_enum = TaskStatus[status.upper()] if status else None
            priority_enum = Priority[priority.upper()] if priority else None

            request = UpdateTaskRequest(
                task_id=task_id,
                title=title,
                description=description,
                status=status_enum,
                priority=priority_enum,
                due_date=due_date,
            )
            result = self.update_use_case.execute(request)
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                logger.info(
                    "Task update handled successfully",
                    extra={"context": {"task_id": task_id}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Task update failed",
                extra={
                    "context": {
                        "task_id": task_id,
                        "error": result.error.message,
                        "error_code": str(result.error.code.name),
                    }
                },
            )
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except (ValueError, KeyError) as e:
            logger.error(
                "Validation error in task update",
                extra={"context": {"task_id": task_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_delete(self, task_id: str) -> OperationResult[DeletionOutcome]:
        """
        모든 인터페이스에서의 작업 삭제 요청을 처리한다.

        Args:
            task_id: 작업의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 삭제된 작업의 세부 정보가 포함된 DeletionResult
            - 실패: 인터페이스용으로 포맷된 오류 정보
        """
        try:
            logger.info(
                "Handling task deletion request",
                extra={"context": {"task_id": task_id}},
            )
            result = self.delete_use_case.execute(UUID(task_id))
            if result.is_success:
                logger.info(
                    "Task deletion handled successfully",
                    extra={"context": {"task_id": task_id}},
                )
                return OperationResult.succeed(result.value)

            logger.error(
                "Task deletion failed",
                extra={
                    "context": {
                        "task_id": task_id,
                        "error": result.error.message,
                        "error_code": str(result.error.code.name),
                    }
                },
            )
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            logger.error(
                "Validation error in task deletion",
                extra={"context": {"task_id": task_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
