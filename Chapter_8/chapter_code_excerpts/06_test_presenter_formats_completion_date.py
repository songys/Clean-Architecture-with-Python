from datetime import datetime, timezone
from uuid import UUID


# 프레젠터 단위 테스트: 도메인 데이터를 UI 표시 형식으로 올바르게 변환하는지 검증
# 프레젠터의 책임은 비즈니스 로직이 아닌 출력 포맷팅
def test_presenter_formats_completion_date():
    """프레젠터가 인터페이스 요구 사항에 따라 날짜를 포맷하는지 테스트"""
    # 준비 - 결정적(deterministic) 테스트를 위해 고정된 시간 사용
    completion_time = datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc)
    task = Task(
        title="Test Task",
        description="Test Description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    task.complete()
    # 결정적 테스트를 위해 완료 시간 재정의
    task.completed_at = completion_time
    # 엔티티 -> DTO(TaskResponse) -> 뷰 모델 변환 과정
    task_response = TaskResponse.from_entity(task)
    presenter = CliTaskPresenter()
    # 실행 - DTO를 뷰 모델로 변환
    view_model = presenter.present_task(task_response)
    # 검증 - 날짜가 "YYYY-MM-DD HH:MM" 형식으로 포맷팅되었는지 확인
    expected_format = "2024-01-15 14:30"
    assert view_model.completion_info is not None and expected_format in view_model.completion_info
