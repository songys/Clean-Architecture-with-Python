from datetime import datetime, timedelta, timezone
from uuid import UUID

from freezegun import freeze_time

from tests.application.conftest import (
    InMemoryTaskRepository,
    NotificationRecorder,
)
from todo_app.application.common.result import ErrorCode
from todo_app.application.use_cases.deadline_use_cases import (
    CheckDeadlinesUseCase,
)
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    BusinessRuleViolation,
    ValidationError,
    TaskNotFoundError,
)
from todo_app.domain.value_objects import Deadline


def test_check_deadlines_empty_repository():
    """작업이 없을 때 마감일 확인 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 0
    assert not notifications.deadline_warnings


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_no_approaching_deadlines():
    """마감일이 임박한 작업이 없을 때 마감일 확인 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    # 먼 미래에 마감일이 있는 작업 생성
    far_future_date = datetime.now(timezone.utc) + timedelta(days=10)
    task1 = Task(
        title="Future Task 1",
        description="Test",
        due_date=Deadline(far_future_date),
    )
    task2 = Task(
        title="Future Task 2",
        description="Test",
        due_date=Deadline(far_future_date + timedelta(days=1)),
    )

    repo.save(task1)
    repo.save(task2)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 0
    assert not notifications.deadline_warnings


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_approaching_deadlines():
    """마감일이 임박한 작업이 있을 때 마감일 확인 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    # 다양한 마감일을 가진 작업 생성
    approaching_date = datetime.now(timezone.utc) + timedelta(hours=23)  # 1일 이내
    future_date = datetime.now(timezone.utc) + timedelta(days=5)  # 임박하지 않음

    task1 = Task(
        title="Approaching Task",
        description="Test",
        due_date=Deadline(approaching_date),
    )
    task2 = Task(title="Future Task", description="Test", due_date=Deadline(future_date))

    repo.save(task1)
    repo.save(task2)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 1
    assert len(notifications.deadline_warnings) == 1
    assert notifications.deadline_warnings[0][0] == task1.id  # 첫 번째 작업에 경고가 발생해야 함
    assert notifications.deadline_warnings[0][1] == 0  # 1일 미만 남음


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_custom_threshold():
    """사용자 정의 경고 임계값으로 마감일 확인 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications, warning_threshold=timedelta(days=3))

    # 다양한 마감일을 가진 작업 생성
    two_days = Task(
        title="Two Days Task",
        description="Test",
        due_date=Deadline(datetime.now(timezone.utc) + timedelta(days=2)),
    )
    four_days = Task(
        title="Four Days Task",
        description="Test",
        due_date=Deadline(datetime.now(timezone.utc) + timedelta(days=4)),
    )

    repo.save(two_days)
    repo.save(four_days)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 1
    assert len(notifications.deadline_warnings) == 1
    assert notifications.deadline_warnings[0][0] == two_days.id
    assert notifications.deadline_warnings[0][1] == 2  # 2일 남음


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_completed_tasks():
    """완료된 작업은 마감일 확인에서 제외되는지 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    # 마감일이 임박한 완료된 작업 생성
    approaching_date = datetime.now(timezone.utc) + timedelta(hours=12)
    task = Task(
        title="Completed Task",
        description="Test",
        due_date=Deadline(approaching_date),
    )
    task.complete()  # 완료로 표시
    repo.save(task)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 0
    assert not notifications.deadline_warnings


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_multiple_notifications():
    """마감일이 임박한 여러 작업 확인 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    # 마감일이 임박한 여러 작업 생성
    base_time = datetime.now(timezone.utc)
    tasks = []
    for hours in [12, 18, 22]:  # 모두 24시간 이내
        task = Task(
            title=f"Task due in {hours} hours",
            description="Test",
            due_date=Deadline(base_time + timedelta(hours=hours)),
        )
        tasks.append(task)
        repo.save(task)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 3
    assert len(notifications.deadline_warnings) == 3
    # 각 작업에 경고가 발생했는지 확인
    task_ids = {warning[0] for warning in notifications.deadline_warnings}
    assert task_ids == {task.id for task in tasks}


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_handles_repository_errors():
    """마감일 확인 중 리포지토리 오류 처리 테스트"""

    class ErroringTaskRepository(InMemoryTaskRepository):
        def get_active_tasks(self):
            raise BusinessRuleViolation("Repository error")

    repo = ErroringTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    result = use_case.execute()

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Repository error" in result.error.message
    assert not notifications.deadline_warnings  # 알림이 전송되지 않아야 함


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_handles_notification_errors():
    """알림 서비스 오류 처리 테스트"""

    class ErroringNotificationService(NotificationRecorder):
        def notify_task_deadline_approaching(self, task_id, days_remaining):
            raise ValidationError("Notification error")

    repo = InMemoryTaskRepository()
    notifications = ErroringNotificationService()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    # 마감일이 임박한 작업 생성
    due_date = datetime.now(timezone.utc) + timedelta(hours=12)
    task = Task(title="Test Task", description="Test", due_date=Deadline(due_date))
    repo.save(task)

    result = use_case.execute()

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Notification error" in result.error.message


@freeze_time("2024-01-01 12:00:00")
def test_check_deadlines_handles_task_not_found():
    """마감일 확인 중 TaskNotFoundError 처리 테스트"""

    class TaskNotFoundRepository(InMemoryTaskRepository):
        def get_active_tasks(self):
            raise TaskNotFoundError(UUID("123e4567-e89b-12d3-a456-426614174000"))

    repo = TaskNotFoundRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    result = use_case.execute()

    assert not result.is_success
    assert result.error.code == ErrorCode.NOT_FOUND
    assert "Task" in result.error.message
    assert not notifications.deadline_warnings


@freeze_time("2024-01-10 12:00:00")
def test_check_deadlines_with_approaching_deadlines():
    """마감일이 임박한 작업들의 마감일 확인 테스트"""
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CheckDeadlinesUseCase(repo, notifications)

    # 마감일이 있는 작업 생성
    approaching_deadline = datetime.now(timezone.utc) + timedelta(hours=12)
    far_future_date = datetime.now(timezone.utc) + timedelta(days=10)
    past_due_date = datetime.now(timezone.utc) - timedelta(days=1)

    # 작업 1: 마감일 임박
    task1 = Task(
        title="Approaching Task",
        description="Test",
        due_date=Deadline(approaching_deadline),
    )

    # 작업 2: 미래 작업
    task2 = Task(
        title="Future Task",
        description="Test",
        due_date=Deadline(far_future_date),
    )

    # 작업 3: 기한 초과 (경고를 발생시키지 않아야 하며, 다른 곳에서 처리)
    task3 = Task(title="Past Due Task", description="Test", due_date=None)  # No deadline initially
    # 유스 케이스 로직을 테스트하기 위해 과거 날짜에 대한 Deadline 검증을 우회해야 한다
    # 실제 시나리오에서는 기한 초과 작업이 다르게 처리되거나 이 확인 전에 필터링될 수 있다.
    # 이 테스트에서는 생성 후 _due_date 속성을 수동으로 설정한다.
    task3._due_date = Deadline(
        datetime.now(timezone.utc) + timedelta(days=1)
    )  # 먼저 유효한 미래 마감일을 생성
    # 이제 과거 마감일을 시뮬레이션하기 위해 내부 속성을 직접 수정
    # 이는 일반적으로 권장되지 않지만 테스트 조건을 격리하기 위해 여기서는 필요하다.
    object.__setattr__(task3._due_date, "due_date", past_due_date)

    repo.save(task1)
    repo.save(task2)
    repo.save(task3)

    result = use_case.execute()

    assert result.is_success
    assert result.value["notifications_sent"] == 1
    assert len(notifications.deadline_warnings) == 1
    assert notifications.deadline_warnings[0][0] == task1.id
    assert notifications.deadline_warnings[0][1] == 0  # 1일 미만 남음
