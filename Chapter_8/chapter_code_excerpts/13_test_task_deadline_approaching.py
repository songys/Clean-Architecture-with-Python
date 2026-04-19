from datetime import timedelta, timezone
from uuid import UUID
from freezegun import freeze_time  # 시간 고정 라이브러리: 테스트에서 현재 시각을 제어
from unittest.mock import Mock


# 시간 의존적 비즈니스 로직 테스트: freezegun으로 현재 시각을 고정하여
# 마감일 임박 알림이 정확한 시간 경계에서 발동하는지 검증
def test_task_deadline_approaching():
    """마감일 알림이 시간 경계를 준수하는지 테스트"""
    # 준비 - freeze_time으로 작업 생성 시점의 시간 고정
    with freeze_time("2024-01-14 12:00:00"):
        task = Task(
            title="Time-sensitive task",
            description="Testing deadlines",
            project_id=UUID("12345678-1234-5678-1234-567812345678"),
            due_date=Deadline(datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)),  # 24시간 후 마감
        )
    notification_service = Mock(spec=NotificationPort)
    use_case = CheckDeadlinesUseCase(
        task_repository=Mock(spec=TaskRepository),
        notification_service=notification_service,
        warning_threshold=timedelta(days=1),  # 마감 1일 전부터 경고
    )

    # 실행 - 1시간 경과 후(마감 23시간 전) 시점에서 마감일 확인
    with freeze_time("2024-01-14 13:00:00"):
        result = use_case.execute()

    # 검증 - 경고 임계값(1일) 이내이므로 알림이 1회 발송되어야 함
    assert result.is_success
    notification_service.notify_task_deadline_approaching.assert_called_once()
