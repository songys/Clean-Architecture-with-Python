# TaskController에서의 5단계 데이터 변환 흐름 예시
# - 외부 입력 -> 요청 모델 -> 유스케이스 실행 -> 뷰 모델 -> OperationResult
# - 각 단계마다 데이터 형식이 해당 계층에 맞게 변환됨


def handle_create(self, title: str, description: str) -> OperationResult[TaskViewModel]:

    try:

        # 1단계: 외부 입력(기본 타입)을 요청 모델로 변환 - 입력 검증 포함

        request = CreateTaskRequest(title=title, description=description)

        # 2단계: 요청 모델을 유스케이스에 전달하여 도메인 로직 실행

        result = self.use_case.execute(request)

        if result.is_success:

            # 3단계: 도메인 응답(TaskResponse)을 화면 표시용 뷰 모델(TaskViewModel)로 변환

            view_model = self.presenter.present_task(result.value)

            return OperationResult.succeed(view_model)

        # 4단계: 도메인 오류를 사용자 친화적 오류 메시지로 변환

        error_vm = self.presenter.present_error(result.error.message, str(result.error.code.name))

        return OperationResult.fail(error_vm.message, error_vm.code)

    except ValueError as e:

        # 5단계: 입력 검증 오류를 유스케이스 도달 전에 포착하여 처리

        error_vm = self.presenter.present_error(str(e), "VALIDATION_ERROR")

        return OperationResult.fail(error_vm.message, error_vm.code)
