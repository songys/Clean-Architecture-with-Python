"""
이 모듈은 클린 아키텍처의 인터페이스 어댑터 계층을 구현하는 프로젝트 컨트롤러를 포함한다.

프로젝트 컨트롤러는 다음을 보여준다:
1. 컨트롤러가 인터페이스와 유스 케이스 사이를 어떻게 라우팅하는지
2. 외부와 내부 데이터 형식 간의 깔끔한 변환
3. 인터페이스를 위한 적절한 오류 처리와 포맷팅
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

import logging

logger = logging.getLogger(__name__)

@dataclass
class ProjectController:
    """
    클린 아키텍처 패턴을 구현하는 프로젝트 관련 작업 컨트롤러.

    이 컨트롤러는 주요 클린 아키텍처 원칙을 보여준다:
    - 컨트롤러는 인터페이스 어댑터 계층에 존재한다
    - 유스 케이스에 대해 안쪽으로 의존한다 (의존성 규칙)
    - 계층 간 데이터 변환을 처리한다
    - 인터페이스 관심사를 비즈니스 로직으로부터 격리한다

    이 클린 아키텍처 구현의 이점:
    - 비즈니스 로직이 유스 케이스에서 보호된다
    - 핵심 로직을 변경하지 않고 새 인터페이스를 추가할 수 있다
    - 의존성 주입을 통해 테스트가 단순화된다
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
        모든 인터페이스에서의 프로젝트 생성 요청을 처리한다.

        이 메서드는 다음과 같이 클린 아키텍처를 따른다:
        1. 원시 타입을 받아들인다 (인터페이스 비의존적)
        2. 데이터를 유스 케이스 형식으로 변환한다
        3. 유스 케이스를 통해 비즈니스 로직을 실행한다
        4. 결과를 인터페이스에 적합한 형식으로 변환한다

        Args:
            name: 프로젝트 이름
            description: 선택적 프로젝트 설명

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 인터페이스용으로 포맷된 ProjectViewModel
            - 실패: 인터페이스용으로 포맷된 오류 정보
        """
        try:
            logger.info(
                "Handling project creation request",
                extra={"context": {"name": name}},
            )
            request = CreateProjectRequest(name=name, description=description)
            result = self.create_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                logger.info(
                    "Project creation handled successfully",
                    extra={"context": {"project_id": str(result.value.id)}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Project creation failed",
                extra={
                    "context": {
                        "name": name,
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
                "Validation error in project creation",
                extra={"context": {"name": name, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_complete(self, project_id: str, notes: Optional[str] = None) -> OperationResult:
        """
        모든 인터페이스에서의 프로젝트 완료 요청을 처리한다.

        클린 아키텍처의 이점을 보여준다:
        1. 인터페이스 비의존적 - 같은 메서드가 모든 인터페이스에서 작동
        2. 유스 케이스에서의 비즈니스 로직 격리
        3. 인터페이스를 위한 적절한 오류 처리와 포맷팅

        Args:
            project_id: 프로젝트의 고유 식별자
            notes: 선택적 완료 메모

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 완료 정보가 포함된 ProjectViewModel
            - 실패: 인터페이스용으로 포맷된 오류 정보
        """
        try:
            logger.info(
                "Handling project completion request",
                extra={"context": {"project_id": project_id}},
            )
            request = CompleteProjectRequest(project_id=project_id, completion_notes=notes)
            result = self.complete_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                logger.info(
                    "Project completion handled successfully",
                    extra={"context": {"project_id": project_id}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Project completion failed",
                extra={
                    "context": {
                        "project_id": project_id,
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
                "Validation error in project completion",
                extra={"context": {"project_id": project_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_get(self, project_id: str) -> OperationResult[ProjectViewModel]:
        """
        프로젝트 조회 요청을 처리한다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: 프로젝트 상세 정보가 포함된 ProjectViewModel
            - 실패: 오류 정보
        """
        try:
            logger.info(
                "Handling project retrieval request",
                extra={"context": {"project_id": project_id}},
            )
            result = self.get_use_case.execute(project_id)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                logger.info(
                    "Project retrieval handled successfully",
                    extra={"context": {"project_id": project_id}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Project retrieval failed",
                extra={
                    "context": {
                        "project_id": project_id,
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
                "Validation error in project retrieval",
                extra={"context": {"project_id": project_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)

    def handle_list(self) -> OperationResult[list[ProjectViewModel]]:
        """
        프로젝트 목록 요청을 처리한다.

        Returns:
            다음 중 하나를 포함하는 OperationResult:
            - 성공: ProjectViewModel 객체 목록
            - 실패: 오류 정보
        """
        logger.info("Handling project list request")
        result = self.list_use_case.execute()

        if result.is_success:
            view_models = [self.presenter.present_project(proj) for proj in result.value]
            logger.info(
                "Project list handled successfully",
                extra={"context": {"count": len(view_models)}},
            )
            return OperationResult.succeed(view_models)

        logger.error(
            "Project list failed",
            extra={
                "context": {
                    "error": result.error.message,
                    "error_code": str(result.error.code.name),
                }
            },
        )
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
            logger.info(
                "Handling project update request",
                extra={
                    "context": {
                        "project_id": project_id,
                        "update_fields": [f for f, v in [("name", name), ("description", description)] if v is not None],
                    }
                },
            )
            request = UpdateProjectRequest(
                project_id=project_id,
                name=name,
                description=description
            )
            result = self.update_use_case.execute(request)

            if result.is_success:
                view_model = self.presenter.present_project(result.value)
                logger.info(
                    "Project update handled successfully",
                    extra={"context": {"project_id": project_id}},
                )
                return OperationResult.succeed(view_model)

            logger.error(
                "Project update failed",
                extra={
                    "context": {
                        "project_id": project_id,
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
                "Validation error in project update",
                extra={"context": {"project_id": project_id, "error": str(e)}},
            )
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
