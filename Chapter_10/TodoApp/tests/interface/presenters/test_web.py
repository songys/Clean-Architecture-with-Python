# 웹 프레젠터 단위 테스트
# - 프레젠터가 DTO를 웹에 적합한 뷰 모델로 올바르게 변환하는지 검증
# - 기한 초과/미래 날짜의 표시 형식 차이 검증
from datetime import datetime, timedelta, timezone
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.presenters.web import WebTaskPresenter
from todo_app.domain.value_objects import TaskStatus, Priority


def test_web_presenter_formats_overdue_date():
    """프레젠터가 기한 초과 날짜를 올바르게 포맷하는지 테스트한다."""
    # Arrange
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    task_response = TaskResponse(
        id="123",
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
        project_id="456",
        due_date=past_date,
    )
    presenter = WebTaskPresenter()

    # Act
    view_model = presenter.present_task(task_response)

    # Assert
    assert view_model.due_date_display is not None
    assert "기한 초과" in view_model.due_date_display
    assert past_date.strftime("%Y-%m-%d") in view_model.due_date_display


def test_web_presenter_formats_future_date():
    """프레젠터가 미래 날짜를 올바르게 포맷하는지 테스트한다."""
    # Arrange
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    task_response = TaskResponse(
        id="123",
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
        project_id="456",
        due_date=future_date,
    )
    presenter = WebTaskPresenter()

    # Act
    view_model = presenter.present_task(task_response)

    # Assert
    assert view_model.due_date_display is not None
    assert "기한 초과" not in view_model.due_date_display
    assert future_date.strftime("%Y-%m-%d") in view_model.due_date_display
