"""
이 모듈은 클린 아키텍처의 인터페이스 어댑터 계층을 구현하는 컨트롤러를 포함한다.

컨트롤러의 책임:
1. 외부 소스(CLI, 웹 등)에서 입력을 받는다
2. 해당 입력을 유스 케이스가 요구하는 형식으로 변환한다
3. 적절한 유스 케이스를 실행한다
4. 결과를 인터페이스에 적합한 뷰 모델로 변환한다
5. 발생하는 모든 오류를 처리하고 형식화한다

이 컨트롤러에서 보여주는 클린 아키텍처의 주요 이점:
- 의존성 규칙을 준수한다: 컨트롤러가 유스 케이스를 향해 안쪽으로 의존한다
- 관심사 분리: 컨트롤러는 라우팅과 데이터 변환만 처리한다
- 독립성: 비즈니스 로직은 유스 케이스에 격리되어 유지된다
- 유연성: 유스 케이스를 변경하지 않고 새 인터페이스를 추가할 수 있다
"""

from dataclasses import dataclass
from typing import Optional

from todo_app.interfaces.presenters.base import TaskPresenter
from todo_app.interfaces.view_models.task_vm import TaskViewModel
from todo_app.interfaces.view_models.base import OperationResult
from todo_app.application.dtos.task_dtos import CompleteTaskRequest, CreateTaskRequest
from todo_app.application.use_cases.task_use_cases import CompleteTaskUseCase, CreateTaskUseCase


# 인터페이스 어댑터 계층의 핵심 - 외부 입력과 유스케이스를 연결하는 컨트롤러
# - 외부 소스(CLI, 웹 등)와 애플리케이션 계층 사이의 중재자
# - 의존성 주입으로 추상화에만 의존하므로 프레임워크에 독립적
@dataclass
class TaskController:
    """
    클린 아키텍처 원칙을 보여주는 작업 관련 작업의 컨트롤러.

    이 컨트롤러는 다음과 같이 클린 아키텍처를 준수한다:
    - 추상화(유스 케이스와 프레젠터)에만 의존한다
    - 외부 입력을 유스 케이스 요청 모델로 변환한다
    - 비즈니스 규칙이 유스 케이스에 유지되도록 한다
    - 프레젠터를 사용하여 인터페이스에 적합한 형태로 출력을 형식화한다

    명확한 관심사 분리를 통해 다음이 가능하다:
    - 의존성 주입을 통한 쉬운 테스트
    - 비즈니스 로직 변경 없이 새 인터페이스 추가
    - 핵심 기능에 영향 없이 프레젠테이션 로직 수정

    Attributes:
        create_use_case: 작업 생성을 위한 유스 케이스
        complete_use_case: 작업 완료를 위한 유스 케이스
        presenter: 인터페이스에 맞게 작업 데이터를 형식화하는 프레젠터
    """

    create_use_case: CreateTaskUseCase  # 작업 생성 비즈니스 로직을 담당하는 유스케이스
    complete_use_case: CompleteTaskUseCase  # 작업 완료 비즈니스 로직을 담당하는 유스케이스
    presenter: TaskPresenter  # 도메인 응답을 화면 표시용으로 변환하는 프레젠터

    def handle_create(self, title: str, description: str) -> OperationResult[TaskViewModel]:
        """
        모든 인터페이스에서의 작업 생성 요청을 처리한다.

        이 메서드는 다음과 같이 클린 아키텍처의 관심사 분리를 보여준다:
        1. 기본 타입을 입력으로 받는다 (인터페이스 독립적으로 만든다)
        2. 입력을 유스 케이스가 요구하는 형식으로 변환한다
        3. 구현 세부 사항을 알지 못한 채 유스 케이스를 실행한다
        4. 프레젠터를 사용하여 응답을 적절하게 형식화한다

        Args:
            title: 작업 제목
            description: 작업 설명

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 인터페이스에 맞게 형식화된 TaskViewModel
            - 실패: 인터페이스에 맞게 형식화된 오류 정보
        """
        try:
            # 기본 타입 입력을 인터페이스->애플리케이션 경계 교차를 위해
            # 특별히 설계된 유스 케이스 요청 모델로 변환
            # 애플리케이션 요구 사항에 특화된 검증을 포함
            # 애플리케이션 계층에 진입하는 데이터가 적절히 형식화되고 검증되도록 한다
            request = CreateTaskRequest(title=title, description=description)

            # 유스 케이스를 실행하고 도메인 지향 결과를 얻는다
            result = self.create_use_case.execute(request)

            if result.is_success:
                # 도메인 응답을 뷰 모델로 변환
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            # 도메인 오류 처리
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            # 검증 오류 처리
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(
        self, task_id: str, notes: Optional[str] = None
    ) -> OperationResult[TaskViewModel]:
        """
        모든 인터페이스에서의 작업 완료 요청을 처리한다.

        클린 아키텍처 원칙에 따라 이 메서드는:
        1. 인터페이스 세부 사항(CLI, 웹 등)을 알지 못한다
        2. 비즈니스 로직을 위해 유스 케이스를 사용한다
        3. 인터페이스에 적합한 뷰 모델을 반환한다

        Args:
            task_id: 작업의 고유 식별자
            notes: 선택적 완료 메모

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 완료 정보가 포함된 TaskViewModel
            - 실패: 인터페이스에 맞게 형식화된 오류 정보
        """
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
