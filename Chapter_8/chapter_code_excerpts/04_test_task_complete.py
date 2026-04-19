from unittest.mock import Mock
from uuid import UUID


# 유스케이스 단위 테스트: Mock으로 저장소와 알림 서비스를 대체
# 비즈니스 로직(작업 완료)만 검증하고, 인프라 동작은 Mock으로 격리
def test_successful_task_completion():
    """모의 의존성을 사용한 작업 완료 테스트"""
    # 준비 - 순수 도메인 객체 생성
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    # Mock 저장소: get() 호출 시 위에서 생성한 task를 반환하도록 설정
    task_repo = Mock()
    task_repo.get.return_value = task
    # Mock 알림 서비스: 실제 알림 전송 없이 호출 여부만 추적
    notification_service = Mock()

    # 유스케이스에 Mock 의존성 주입
    use_case = CompleteTaskUseCase(
        task_repository=task_repo, notification_service=notification_service
    )
    request = CompleteTaskRequest(task_id=str(task.id))
    # 실행
    result = use_case.execute(request)

    # 검증 - 유스케이스 성공 여부와 의존성 호출 확인
    assert result.is_success
    task_repo.save.assert_called_once_with(task)  # 저장소에 1회 저장 확인
    notification_service.notify_task_completed.assert_called_once_with(task)  # 알림 1회 전송 확인
