# 올바름: 인터페이스에 구애받지 않는 컨트롤러
# 프레임워크 독립적인 기본 타입(str)만 받고, 모든 포맷팅은 프레젠터에 위임
def handle_create(self, title: str, description: str) -> OperationResult:
    """해야 할 것: 컨트롤러를 인터페이스에 구애받지 않게 유지"""
    try:
        # 1단계: 기본 타입을 유스 케이스 요청 DTO로 변환
        request = CreateTaskRequest(title=title, description=description)
        # 2단계: 비즈니스 로직 실행 (유스 케이스 호출)
        result = self.create_use_case.execute(request)
        if result.is_success:
            # 3단계: 프레젠터를 통해 인터페이스에 적합한 뷰 모델로 변환
            view_model = self.presenter.present_task(result.value)
            return OperationResult.succeed(view_model)

        # 실패 시에도 프레젠터를 통해 오류 메시지 포맷팅
        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))
        return OperationResult.fail(error_vm.message, error_vm.code)
    except ValueError as e:
        # 검증 오류도 프레젠터를 통해 일관된 형식으로 처리
        error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")
        return OperationResult.fail(error_vm.message, error_vm.code)
