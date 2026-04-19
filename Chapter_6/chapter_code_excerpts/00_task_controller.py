from dataclasses import dataclass


# 외부 입력을 유스케이스에 전달하고 결과를 뷰 모델로 변환하는 컨트롤러
# - 인터페이스 어댑터 계층의 핵심 구성 요소
# - 외부(CLI, 웹 등)와 내부(유스케이스) 사이의 중재자 역할
@dataclass
class TaskController:
    create_use_case: CreateTaskUseCase  # 작업 생성을 담당하는 유스케이스 (애플리케이션 계층)
    # 필요에 따라 추가 유스 케이스 정의
    presenter: TaskPresenter  # 도메인 응답을 화면 표시용으로 변환하는 프레젠터 (인터페이스 계층)

    # 작업 생성 요청을 처리하고 OperationResult로 감싼 뷰 모델을 반환하는 핸들러
    def handle_create(self, title: str, description: str) -> OperationResult[TaskViewModel]:
        try:
            # 기본 타입 입력을 유스케이스가 이해할 수 있는 요청 모델로 변환
            request = CreateTaskRequest(title=title, description=description)
            # 유스케이스 실행 - 비즈니스 로직은 유스케이스 내부에 캡슐화
            result = self.create_use_case.execute(request)

            if result.is_success:
                # 성공 시: 도메인 응답을 프레젠터를 통해 화면 표시용 뷰 모델로 변환
                view_model = self.presenter.present_task(result.value)
                return OperationResult.succeed(view_model)

            # 실패 시: 도메인 오류를 프레젠터를 통해 사용자 친화적 오류 메시지로 변환
            error_vm = self.presenter.present_error(
                result.error.message, str(result.error.code.name)
            )
            return OperationResult.fail(error_vm.message, error_vm.code)

        except ValueError as e:
            # 입력 검증 실패 시: 유스케이스에 도달하기 전에 오류를 포착하여 처리
            error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
            return OperationResult.fail(error_vm.message, error_vm.code)
