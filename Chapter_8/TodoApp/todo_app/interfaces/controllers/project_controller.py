"""
이 모듈은 클린 아키텍처의 인터페이스 어댑터 계층을 구현하는 프로젝트 컨트롤러를 포함한다.

프로젝트 컨트롤러가 보여주는 것:
1. 컨트롤러가 인터페이스와 유스 케이스 사이를 어떻게 라우팅하는지
2. 외부와 내부 데이터 형식 간의 깔끔한 변환
3. 인터페이스를 위한 적절한 오류 처리 및 포맷팅
4. 의존성 규칙 준수
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from todo_app.interfaces.view_models.project_vm import ProjectViewModel
from todo_app.interfaces.presenters.base import ProjectPresenter
from todo_app.interfaces.view_models.base import OperationResult
from todo_app.application.dtos.project_dtos import CompleteProjectRequest, CreateProjectRequest, UpdateProjectRequest
from todo_app.application.use_cases.project_use_cases import (
    CompleteProjectUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
)


@dataclass
class ProjectController:
    """
    클린 아키텍처 패턴을 구현하는 프로젝트 관련 작업의 컨트롤러.

    이 컨트롤러가 보여주는 핵심 클린 아키텍처 원칙:
    - 컨트롤러는 인터페이스 어댑터 계층에 존재한다
    - 유스 케이스를 향해 안쪽으로 의존한다 (의존성 규칙)
    - 계층 간 데이터 변환을 처리한다
    - 인터페이스 관심사를 비즈니스 로직으로부터 격리한다

    이 클린 아키텍처 구현의 장점:
    - 비즈니스 로직은 유스 케이스에서 보호된다
    - 핵심 로직 변경 없이 새 인터페이스를 추가할 수 있다
    - 의존성 주입을 통해 테스트가 간소화된다
    - 프레젠테이션 관심사가 적절히 분리된다

    Attributes:
        create_use_case: 프로젝트 생성 유스 케이스
        complete_use_case: 프로젝트 완료 유스 케이스
        presenter: 인터페이스를 위한 프로젝트 데이터 포맷팅 처리
        update_use_case: 프로젝트 업데이트 유스 케이스
    """

    create_use_case: CreateProjectUseCase
    complete_use_case: CompleteProjectUseCase
    presenter: ProjectPresenter
    get_use_case: GetProjectUseCase
    list_use_case: ListProjectsUseCase
    update_use_case: UpdateProjectUseCase

    def handle_create(self, name: str, description: str = "") -> OperationResult:
        """
        모든 인터페이스에서 오는 프로젝트 생성 요청을 처리한다.

        이 메서드는 클린 아키텍처를 따른다:
        1. 원시 타입을 받아들인다 (인터페이스에 무관하게)
        2. 데이터를 유스 케이스 형식으로 변환한다
        3. 유스 케이스를 통해 비즈니스 로직을 실행한다
        4. 응답을 인터페이스에 적합한 형식으로 변환한다

        Args:
            name: 프로젝트 이름
            description: 선택적 프로젝트 설명

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 인터페이스용으로 포맷된 ProjectViewModel
            - 실패: 인터페이스용으로 포맷된 오류 정보
        """
        try:
            request = CreateProjectRequest(name=name, description=description)
            result = self.create_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(self, project_id: str, notes: Optional[str] = None) -> OperationResult:
        """
        모든 인터페이스에서 오는 프로젝트 완료 요청을 처리한다.

        클린 아키텍처의 장점을 보여준다:
        1. 인터페이스에 무관 - 동일한 메서드가 모든 인터페이스에서 작동
        2. 유스 케이스에서의 비즈니스 로직 격리
        3. 인터페이스를 위한 적절한 오류 처리 및 포맷팅

        Args:
            project_id: 프로젝트의 고유 식별자
            notes: 선택적 완료 메모

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 완료 정보가 포함된 ProjectViewModel
            - 실패: 인터페이스용으로 포맷된 오류 정보
        """
        try:
            request = CompleteProjectRequest(project_id=project_id, completion_notes=notes)
            result = self.complete_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_get(self, project_id: str) -> OperationResult[ProjectViewModel]:
        """
        프로젝트 조회 요청을 처리한다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 프로젝트 세부 정보가 포함된 ProjectViewModel
            - 실패: 오류 정보
        """
        try:
            result = self.get_use_case.execute(project_id)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_list(self) -> OperationResult[list[ProjectViewModel]]:
        """
        프로젝트 목록 조회 요청을 처리한다.

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: ProjectViewModel 객체의 리스트
            - 실패: 오류 정보
        """
        result = self.list_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_project(proj) for proj in result.value]
            return OperationResult.succeed(view_models)

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_update(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> OperationResult:
        """
        프로젝트 업데이트 요청을 처리한다.

        Args:
            project_id: 프로젝트의 고유 식별자
            name: 선택적 새 프로젝트 이름
            description: 선택적 새 프로젝트 설명

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 업데이트된 ProjectViewModel
            - 실패: 오류 정보
        """
        try:
            request = UpdateProjectRequest(
                project_id=project_id,
                name=name,
                description=description
            )
            result = self.update_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                return OperationResult.succeed(view_model)

            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
