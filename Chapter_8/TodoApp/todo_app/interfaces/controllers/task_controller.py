"""
이 모듈은 클린 아키텍처의 인터페이스 어댑터 계층을 구현하는 컨트롤러를 포함한다.

컨트롤러의 역할:
1. 외부 소스(CLI, 웹 등)에서 입력을 받는다
2. 해당 입력을 유스 케이스가 요구하는 형식으로 변환한다
3. 적절한 유스 케이스를 실행한다
4. 결과를 인터페이스에 적합한 뷰 모델로 변환한다
5. 발생하는 모든 오류를 처리하고 포맷팅한다

이 컨트롤러에서 보여주는 핵심 클린 아키텍처의 장점:
- 의존성 규칙 준수: 컨트롤러는 유스 케이스를 향해 안쪽으로 의존한다
- 관심사의 분리: 컨트롤러는 라우팅과 데이터 변환만 처리한다
- 독립성: 비즈니스 로직은 유스 케이스에서 격리된 상태를 유지한다
- 유연성: 유스 케이스 변경 없이 새 인터페이스를 추가할 수 있다
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


# 인터페이스 어댑터 계층의 컨트롤러
# 외부 입력(문자열 등)을 내부 형식(UUID, DTO)으로 변환하고 유스케이스 실행 후
# 결과를 프레젠터를 통해 뷰 모델로 변환하는 역할
@dataclass
class TaskController:
    """작업 관련 작업의 컨트롤러."""

    # 의존성 주입: 유스케이스와 프레젠터를 외부에서 주입
    create_use_case: CreateTaskUseCase
    get_use_case: GetTaskUseCase
    complete_use_case: CompleteTaskUseCase
    update_use_case: UpdateTaskUseCase
    delete_use_case: DeleteTaskUseCase
    presenter: TaskPresenter  # 출력 포맷팅 담당

    def handle_create(
        self,
        title: str,
        description: str,
        project_id: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> OperationResult[TaskViewModel]:
        try:
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
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_get(self, task_id: str) -> OperationResult[TaskViewModel]:
        try:
            result = self.get_use_case.execute(UUID(task_id))
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(
        self, task_id: str, notes: Optional[str] = None
    ) -> OperationResult[TaskViewModel]:
        """작업 완료 요청을 처리한다."""
        try:
            request = CompleteTaskRequest(task_id=task_id, completion_notes=notes)
            result = self.complete_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_update(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> OperationResult[TaskViewModel]:
        try:
            # 문자열 상태/우선순위가 제공된 경우 열거형으로 변환
            status_enum = TaskStatus[status.upper()] if status else None
            priority_enum = Priority[priority.upper()] if priority else None

            request = UpdateTaskRequest(
                task_id=task_id,
                title=title,
                description=description,
                status=status_enum,
                priority=priority_enum,
            )
            result = self.update_use_case.execute(request)
            if result.is_success:
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except (ValueError, KeyError) as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_delete(self, task_id: str) -> OperationResult[DeletionOutcome]:
        """
        모든 인터페이스에서 오는 작업 삭제 요청을 처리한다.

        Args:
            task_id: 작업의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 삭제된 작업의 세부 정보가 포함된 DeletionResult
            - 실패: 인터페이스용으로 포맷된 오류 정보
        """
        try:
            result = self.delete_use_case.execute(UUID(task_id))
            if result.is_success:
                return OperationResult.succeed(result.value)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)
        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
