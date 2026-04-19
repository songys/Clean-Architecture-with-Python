from datetime import datetime, timezone
from uuid import UUID
from todo_app.domain.value_objects import Priority
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.domain.entities.task import Task
from todo_app.interfaces.presenters.cli import CliTaskPresenter


# CLI 프레젠터 단위 테스트 - 터미널 전용 날짜 포맷팅 검증
def test_presenter_formats_completion_date():
    """프레젠터가 인터페이스 요구사항에 따라 날짜를 포맷하는지 테스트한다."""
    # Arrange
    completion_time = datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc)
    task = Task(
        title="Test Task",
        description="Test Description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    task.complete()
    # 결정적 테스트를 위해 완료 시간 재정의
    task.completed_at = completion_time

    task_response = TaskResponse.from_entity(task)
    presenter = CliTaskPresenter()

    # Act
    view_model = presenter.present_task(task_response)

    # Assert
    expected_format = "2024-01-15 14:30"
    assert view_model.completion_info is not None and expected_format in view_model.completion_info


# CLI 프레젠터의 뷰 모델 생성 검증 - 모든 표시 필드가 올바르게 포맷되는지 확인
def test_presenter_provides_complete_view_model():
    """프레젠터가 모든 표시 필드를 가진 올바르게 포맷된 뷰 모델을 생성하는지 테스트한다."""
    # Arrange
    task = Task(
        title="Important Task",
        description="Testing view model creation",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
        priority=Priority.HIGH,
    )
    task.complete()  # Set status to DONE
    task_response = TaskResponse.from_entity(task)
    presenter = CliTaskPresenter()

    # Act
    view_model = presenter.present_task(task_response)

    # Assert
    assert view_model.title == "Important Task"
    assert view_model.status_display == "[DONE]"
    assert view_model.priority_display == "High"
    assert isinstance(view_model.completion_info, str)
