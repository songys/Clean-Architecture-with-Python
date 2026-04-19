from datetime import datetime, timezone
from uuid import UUID
from todo_app.domain.value_objects import Priority
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.domain.entities.task import Task
from todo_app.interfaces.presenters.cli import CliTaskPresenter


# === 프레젠터 단위 테스트 ===
# DTO를 뷰 모델로 변환하는 과정에서 날짜 포맷, 상태 표시 등이 올바른지 검증
# 비즈니스 로직(영속성, 알림)은 관여하지 않고 출력 포맷팅만 테스트

# 날짜 포맷팅 검증: 완료일이 "YYYY-MM-DD HH:MM" 형식으로 표시되는지 확인
def test_presenter_formats_completion_date():
    """프레젠터가 인터페이스 요구사항에 따라 날짜를 포맷팅하는지 테스트한다."""
    # 준비 - 결정적(deterministic) 테스트를 위해 고정된 시간 사용
    completion_time = datetime(2024, 1, 15, 14, 30, tzinfo=timezone.utc)
    task = Task(
        title="Test Task",
        description="Test Description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    task.complete()
    # 결정론적 테스트를 위해 완료 시간을 재설정
    task.completed_at = completion_time

    # 엔티티 -> DTO -> 뷰 모델 변환 과정
    task_response = TaskResponse.from_entity(task)
    presenter = CliTaskPresenter()

    # 실행 - DTO를 뷰 모델로 변환
    view_model = presenter.present_task(task_response)

    # 검증 - 날짜 포맷이 기대 형식과 일치하는지 확인
    expected_format = "2024-01-15 14:30"
    assert view_model.completion_info is not None and expected_format in view_model.completion_info


# 뷰 모델 전체 필드 검증: 모든 표시 필드가 올바른 형식으로 채워지는지 확인
def test_presenter_provides_complete_view_model():
    """프레젠터가 모든 표시 필드를 포함한 올바르게 포맷된 뷰 모델을 생성하는지 테스트한다."""
    # 준비 - HIGH 우선순위, 완료 상태의 작업
    task = Task(
        title="Important Task",
        description="Testing view model creation",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
        priority=Priority.HIGH,
    )
    task.complete()  # 상태를 DONE으로 설정
    task_response = TaskResponse.from_entity(task)
    presenter = CliTaskPresenter()

    # 실행
    view_model = presenter.present_task(task_response)

    # 검증 - 뷰 모델의 각 필드가 사람이 읽기 좋은 형식인지 확인
    assert view_model.title == "Important Task"
    assert view_model.status_display == "[DONE]"  # 상태 표시 형식
    assert view_model.priority_display == "High"  # 우선순위 표시 형식
    assert isinstance(view_model.completion_info, str)  # 완료 정보 존재 여부
