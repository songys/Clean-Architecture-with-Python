# todo_app/tests/application/test_task_use_cases.py
"""작업 관련 유스 케이스 테스트."""
# 작업 생성, 완료, 우선순위 설정 유스케이스의 성공/실패 시나리오 및 롤백 동작 검증

from uuid import uuid4

import pytest

from tests.application.conftest import (
    InMemoryTaskRepository,
    InMemoryProjectRepository,
    NotificationRecorder,
)
from todo_app.application.common.result import ErrorCode
from todo_app.application.dtos.task_dtos import (
    CreateTaskRequest,
    CompleteTaskRequest,
    SetTaskPriorityRequest,
)
from todo_app.application.use_cases.task_use_cases import (
    CreateTaskUseCase,
    CompleteTaskUseCase,
    SetTaskPriorityUseCase,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    BusinessRuleViolation,
    ValidationError,
)
from todo_app.domain.value_objects import Priority, TaskStatus


def test_create_task_basic():
    """기본 정보로 작업 생성을 테스트한다."""
    # 준비
    repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(repo, project_repo)

    request = CreateTaskRequest(title="Test Task", description="Test Description")

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.title == "Test Task"
    assert result.value.description == "Test Description"
    assert result.value.status == TaskStatus.TODO
    assert result.value.priority == Priority.MEDIUM


def test_create_task_with_project():
    """프로젝트에 연결된 작업 생성을 테스트한다."""
    # 준비
    task_repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    # 먼저 프로젝트 생성
    project = Project(name="Test Project")
    project_repo.save(project)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id=str(project.id),
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.project_id == str(project.id)


def test_create_task_with_invalid_project():
    """존재하지 않는 프로젝트 ID로 작업 생성을 테스트한다."""
    # 준비
    task_repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id=str(uuid4()),
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert not result.is_success
    assert result.error.code.value == "NOT_FOUND"


def test_complete_task():
    """작업 완료를 테스트한다."""
    # 준비
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    # 작업 생성 및 저장
    task = Task(title="Test Task", description="Test Description")
    repo.save(task)

    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.status == TaskStatus.DONE
    assert result.value.completion_notes == "Done!"
    assert task.id in notifications.completed_tasks


def test_complete_nonexistent_task():
    """존재하지 않는 작업 완료를 테스트한다."""
    # 준비
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    request = CompleteTaskRequest(task_id=str(uuid4()), completion_notes="Done!")

    # 실행
    result = use_case.execute(request)

    # 검증
    assert not result.is_success
    assert result.error.code.value == "NOT_FOUND"
    assert not notifications.completed_tasks  # 알림이 전송되지 않아야 함


def test_set_task_priority():
    """작업 우선순위 설정을 테스트한다."""
    # 준비
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = SetTaskPriorityUseCase(repo, notifications)

    # 작업 생성 및 저장
    task = Task(title="Test Task", description="Test Description")
    repo.save(task)

    request = SetTaskPriorityRequest(task_id=str(task.id), priority="HIGH")

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.priority == Priority.HIGH
    assert task.id in notifications.high_priority_tasks


def test_set_task_invalid_priority():
    """잘못된 우선순위 설정을 테스트한다."""
    # 준비
    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()
    use_case = SetTaskPriorityUseCase(repo, notifications)

    task = Task(title="Test Task", description="Test Description")
    repo.save(task)

    with pytest.raises(ValueError) as exc_info:
        SetTaskPriorityRequest(task_id=str(task.id), priority="INVALID")

    assert "우선순위는 다음 중 하나여야 합니다" in str(exc_info.value)


def test_complete_task_handles_validation_error():
    """작업 완료 중 ValidationError 처리를 테스트한다."""
    task = Task(title="Test Task", description="Test Description")

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid completion state")

    repo = ValidationErrorTaskRepository()
    repo._tasks[task.id] = task  # 작업을 리포지토리에 직접 추가
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid completion state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_task_handles_business_rule_violation():
    """작업 완료 중 BusinessRuleViolation 처리를 테스트한다."""
    task = Task(title="Test Task", description="Test Description")

    class BusinessRuleTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise BusinessRuleViolation("Cannot complete task in current state")

    repo = BusinessRuleTaskRepository()
    repo._tasks[task.id] = task  # 작업을 리포지토리에 직접 추가
    notifications = NotificationRecorder()
    use_case = CompleteTaskUseCase(repo, notifications)

    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Cannot complete task in current state" in result.error.message
    assert not notifications.completed_tasks


def test_create_task_request_validates_project_id_format():
    """CreateTaskRequest가 프로젝트 ID 형식을 검증하는지 테스트한다."""
    # 유효한 UUID는 작동해야 함
    valid_request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id="123e4567-e89b-12d3-a456-426614174000",
    )
    assert valid_request.project_id == "123e4567-e89b-12d3-a456-426614174000"

    # 잘못된 UUID는 ValueError를 발생시켜야 함
    with pytest.raises(ValueError, match="잘못된 프로젝트 ID 형식입니다"):
        CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            project_id="not-a-uuid",
        )

    # 빈 project_id는 허용되어야 함 (Optional)
    no_project_request = CreateTaskRequest(
        title="Test Task", description="Test Description", project_id=None
    )
    assert no_project_request.project_id is None


def test_create_task_handles_validation_error():
    """작업 생성 중 ValidationError 처리를 테스트한다."""

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid task data")

    task_repo = ValidationErrorTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(title="Test Task", description="Test Description")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid task data" in result.error.message


def test_create_task_handles_business_rule_violation():
    """작업 생성 중 BusinessRuleViolation 처리를 테스트한다."""

    class BusinessRuleTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise BusinessRuleViolation("Task limit exceeded")

    task_repo = BusinessRuleTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(title="Test Task", description="Test Description")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Task limit exceeded" in result.error.message


def test_create_task_handles_validation_error_with_project():
    """프로젝트가 포함된 작업 생성 중 ValidationError 처리를 테스트한다."""
    project = Project(name="Test Project")

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid task data")

    task_repo = ValidationErrorTaskRepository()
    project_repo = InMemoryProjectRepository()
    project_repo._projects[project.id] = project  # 프로젝트를 직접 추가
    use_case = CreateTaskUseCase(task_repo, project_repo)

    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id=str(project.id),
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid task data" in result.error.message


def test_complete_task_rolls_back_on_validation_error():
    """ValidationError 발생 시 작업 상태가 롤백되는지 테스트한다."""
    # 작업 설정
    task = Task(title="Test Task", description="Test Description")

    class FailingTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            if task.status == TaskStatus.DONE:
                raise ValidationError("Cannot complete task")
            super().save(task)

    repo = FailingTaskRepository()
    notifications = NotificationRecorder()

    # 초기 상태 저장
    repo.save(task)

    use_case = CompleteTaskUseCase(repo, notifications)
    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    # 유스 케이스 실행 (실패해야 함)
    result = use_case.execute(request)

    # 실패 확인
    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR

    # 작업 상태가 롤백되었는지 확인
    saved_task = repo.get(task.id)
    assert saved_task.status == TaskStatus.TODO
    assert saved_task.completed_at is None
    assert saved_task.completion_notes is None

    # 알림이 전송되지 않았는지 확인
    assert not notifications.completed_tasks


def test_complete_task_rolls_back_on_business_rule_violation():
    """BusinessRuleViolation 발생 시 작업 상태가 롤백되는지 테스트한다."""
    # 작업 설정
    task = Task(title="Test Task", description="Test Description")

    class FailingTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            if task.status == TaskStatus.DONE:
                raise BusinessRuleViolation("Task completion limit reached")
            super().save(task)

    repo = FailingTaskRepository()
    notifications = NotificationRecorder()

    # 초기 상태 저장
    repo.save(task)

    use_case = CompleteTaskUseCase(repo, notifications)
    request = CompleteTaskRequest(task_id=str(task.id), completion_notes="Done!")

    # 유스 케이스 실행 (실패해야 함)
    result = use_case.execute(request)

    # 실패 확인
    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION

    # 작업 상태가 롤백되었는지 확인
    saved_task = repo.get(task.id)
    assert saved_task.status == TaskStatus.TODO
    assert saved_task.completed_at is None
    assert saved_task.completion_notes is None

    # 알림이 전송되지 않았는지 확인
    assert not notifications.completed_tasks


def test_complete_task_maintains_state_on_successful_completion():
    """완료가 성공했을 때 작업 상태 변경이 유지되는지 테스트한다."""
    task = Task(title="Test Task", description="Test Description")

    repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    # 초기 상태 저장
    repo.save(task)

    use_case = CompleteTaskUseCase(repo, notifications)
    completion_notes = "Done!"
    request = CompleteTaskRequest(task_id=str(task.id), completion_notes=completion_notes)

    # 유스 케이스 실행 (성공해야 함)
    result = use_case.execute(request)

    # 성공 확인
    assert result.is_success

    # 작업 상태가 업데이트되고 영속되었는지 확인
    saved_task = repo.get(task.id)
    assert saved_task.status == TaskStatus.DONE
    assert saved_task.completed_at is not None
    assert saved_task.completion_notes == completion_notes

    # 알림이 전송되었는지 확인 - 작업 ID를 직접 비교
    assert str(task.id) in [str(t_id) for t_id in notifications.completed_tasks]


def test_create_task_with_nonexistent_project():
    """작업 생성 중 존재하지 않는 프로젝트 ID 처리를 테스트한다."""
    task_repo = InMemoryTaskRepository()
    project_repo = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(task_repo, project_repo)

    # 유효한 UUID 형식이지만 존재하지 않는 프로젝트에 대한 것
    request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        project_id="123e4567-e89b-12d3-a456-426614174000",  # 존재하지 않는 유효한 UUID
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.NOT_FOUND
    assert "ID가 123e4567-e89b-12d3-a456-426614174000인 Project을(를) 찾을 수 없음" in result.error.message


def test_create_task_fails_with_malformed_project_id():
    # ValueError가 발생하는지 테스트
    with pytest.raises(ValueError, match="잘못된 프로젝트 ID 형식입니다"):
        _ = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            project_id="malformed project id",
        )


def test_set_task_priority_fails_with_malformed_task_id():
    # ValueError가 발생하는지 테스트
    with pytest.raises(ValueError, match="잘못된 작업 ID 형식입니다"):
        _ = SetTaskPriorityRequest(
            task_id="malformed project id",
            priority="HIGH",
        )


def test_set_task_priority_handles_validation_error():
    """우선순위 설정 중 ValidationError 처리를 테스트한다."""
    # 작업 생성
    task = Task(title="Test Task", description="Test Description")

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid priority state")

    repo = ValidationErrorTaskRepository()
    repo._tasks[task.id] = task  # 작업을 리포지토리에 직접 추가
    notifications = NotificationRecorder()

    use_case = SetTaskPriorityUseCase(repo, notifications)
    request = SetTaskPriorityRequest(task_id=str(task.id), priority="HIGH")

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid priority state" in result.error.message
    assert not notifications.high_priority_tasks
