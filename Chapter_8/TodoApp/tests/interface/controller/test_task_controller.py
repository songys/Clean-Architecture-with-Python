from unittest.mock import Mock
from uuid import UUID
from todo_app.application.use_cases.task_use_cases import CompleteTaskUseCase
from todo_app.application.common.result import Result
from todo_app.domain.entities.task import Task
from todo_app.interfaces.controllers.task_controller import TaskController
from todo_app.interfaces.presenters.base import TaskPresenter
from todo_app.application.dtos.task_dtos import TaskResponse


# === 컨트롤러 단위 테스트 ===
# 컨트롤러의 핵심 역할인 데이터 형식 변환(문자열 -> UUID)과
# 유스케이스 호출 위임을 Mock으로 검증

# 컨트롤러 -> 유스케이스 -> 저장소 간의 UUID 변환 검증
def test_controller_sends_uuid_to_repository():
    """리포지토리가 작업 작업을 위해 UUID를 수신하는지 테스트한다."""
    # 준비 - 외부에서 전달받는 문자열 ID
    task_id = "123e4567-e89b-12d3-a456-426614174000"
    expected_uuid = UUID(task_id)
    # Mock 저장소에 테스트용 작업 설정
    mock_repo = Mock()
    mock_repo.get.return_value = Task(
        title="Test Task",
        description="Test Description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    # 실제 유스케이스에 Mock 저장소 주입
    complete_use_case = CompleteTaskUseCase(task_repository=mock_repo, notification_service=Mock())

    controller = TaskController(
        complete_use_case=complete_use_case,
        get_use_case=Mock(),
        create_use_case=Mock(),
        update_use_case=Mock(),
        delete_use_case=Mock(),
        presenter=Mock(spec=TaskPresenter),
    )

    # 실행 - 문자열 ID로 컨트롤러 호출
    controller.handle_complete(task_id=task_id)

    # 검증 - 저장소에 UUID 타입으로 전달되었는지 확인
    mock_repo.get.assert_called_once()
    actual_uuid = mock_repo.get.call_args[0][0]
    assert isinstance(actual_uuid, UUID)  # 문자열이 아닌 UUID 타입 확인
    assert actual_uuid == expected_uuid
