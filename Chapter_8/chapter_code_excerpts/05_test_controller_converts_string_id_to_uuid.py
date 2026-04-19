from uuid import UUID
from unittest.mock import Mock


# 인터페이스 어댑터(컨트롤러) 계층의 단위 테스트
# 컨트롤러의 핵심 책임: 외부 형식(문자열)을 내부 형식(UUID)으로 변환
def test_controller_converts_string_id_to_uuid():
    """컨트롤러가 문자열 ID를 유스 케이스를 위한 UUID로 올바르게 변환하는지 테스트"""
    # 준비 - 외부에서 전달받는 문자열 ID
    task_id = "123e4567-e89b-12d3-a456-426614174000"
    # Mock 유스케이스: execute() 호출 시 성공 결과 반환 설정
    complete_use_case = Mock()
    complete_use_case.execute.return_value = Result.success(
        TaskResponse.from_entity(
            Task(
                title="Test Task",
                description="Test Description",
                project_id=UUID("12345678-1234-5678-1234-567812345678"),
            )
        )
    )
    # spec=TaskPresenter로 인터페이스 준수를 보장하는 Mock 프레젠터
    presenter = Mock(spec=TaskPresenter)

    controller = TaskController(
        complete_use_case=complete_use_case,
        presenter=presenter,
    )

    # 실행 - 문자열 ID로 컨트롤러 호출
    controller.handle_complete(task_id=task_id)

    # 검증 - 유스케이스에 전달된 요청의 task_id가 UUID 타입인지 확인
    complete_use_case.execute.assert_called_once()
    called_request = complete_use_case.execute.call_args[0][0]
    assert isinstance(called_request.task_id, UUID)
