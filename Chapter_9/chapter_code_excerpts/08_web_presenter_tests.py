from datetime import datetime, timedelta, timezone


# 웹 프레젠터의 단위 테스트
# 웹 프레임워크(Flask) 설정 없이도 프레젠터의 포맷팅 로직을 독립적으로 검증
# 클린 아키텍처의 관심사 분리 덕분에 가능한 테스트 방식
def test_web_presenter_formats_overdue_date():
    """프레젠터가 기한 초과 날짜를 올바르게 포맷하는지 테스트한다."""
    # 준비 - 과거 날짜를 가진 작업 응답 DTO 생성
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

    # 실행
    view_model = presenter.present_task(task_response)

    # 검증
    assert "기한 초과" in view_model.due_date_display
    assert past_date.strftime("%Y-%m-%d") in view_model.due_date_display


# 미래 마감일에 대한 포맷팅 검증 테스트
def test_web_presenter_formats_future_date():
    """프레젠터가 미래 날짜를 올바르게 포맷하는지 테스트한다."""
    # 준비 - 미래 날짜를 가진 작업 응답 DTO 생성
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

    # 실행
    view_model = presenter.present_task(task_response)

    # 검증
    assert "기한 초과" not in view_model.due_date_display
    assert future_date.strftime("%Y-%m-%d") in view_model.due_date_display
