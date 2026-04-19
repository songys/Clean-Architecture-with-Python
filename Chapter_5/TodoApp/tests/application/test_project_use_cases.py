# todo_app/tests/application/test_project_use_cases.py
"""프로젝트 관련 유스 케이스 테스트."""
# 프로젝트 생성, 완료 유스케이스의 성공/실패 시나리오 및 롤백 동작 검증

from uuid import uuid4

import pytest

from tests.application.conftest import (
    InMemoryProjectRepository,
    InMemoryTaskRepository,
    NotificationRecorder,
)
from todo_app.application.common.result import ErrorCode
from todo_app.application.dtos.project_dtos import (
    CreateProjectRequest,
    CompleteProjectRequest,
)
from todo_app.application.use_cases.project_use_cases import (
    CreateProjectUseCase,
    CompleteProjectUseCase,
)
from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    BusinessRuleViolation,
    ValidationError,
)
from todo_app.domain.value_objects import (
    ProjectStatus,
    TaskStatus,
)


def test_create_project():
    """기본 정보로 프로젝트 생성을 테스트한다."""
    # 준비
    repo = InMemoryProjectRepository()
    use_case = CreateProjectUseCase(repo)

    request = CreateProjectRequest(
        name="Test Project", description="Test Description"
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.name == "Test Project"
    assert result.value.description == "Test Description"
    assert result.value.status == ProjectStatus.ACTIVE


def test_complete_project_without_tasks():
    """작업이 없는 프로젝트 완료를 테스트한다."""
    # 준비
    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    # 프로젝트 생성 및 저장
    project = Project(name="Test Project")
    project_repo.save(project)

    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="All done!"
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.status == ProjectStatus.COMPLETED
    assert result.value.completion_notes == "All done!"
    assert result.value.task_count == 0


def test_complete_project_with_incomplete_tasks():
    """미완료 작업이 있는 프로젝트 완료를 테스트한다. 모든 작업이 완료로 표시되어야 한다."""
    # 준비
    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    # 작업이 포함된 프로젝트 생성
    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)
    project_repo.save(project)

    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert task.status == TaskStatus.DONE


def test_complete_project_with_completed_tasks():
    """모든 작업이 완료된 프로젝트의 완료를 테스트한다."""
    # 준비
    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    # 완료된 작업이 포함된 프로젝트 생성
    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    task.complete()  # 작업 완료
    project.add_task(task)
    project_repo.save(project)

    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="All done!"
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert result.is_success
    assert result.value.status == ProjectStatus.COMPLETED
    assert result.value.task_count == 1


def test_complete_nonexistent_project():
    """존재하지 않는 프로젝트 완료를 테스트한다."""
    # 준비
    project_repo = InMemoryProjectRepository()
    task_repo = InMemoryTaskRepository()
    notify_port = NotificationRecorder()
    use_case = CompleteProjectUseCase(project_repo, task_repo, notify_port)

    request = CompleteProjectRequest(
        project_id=str(uuid4()), completion_notes="Done!"
    )

    # 실행
    result = use_case.execute(request)

    # 검증
    assert not result.is_success
    assert result.error.code.value == "NOT_FOUND"


def test_create_project_handles_validation_error():
    """프로젝트 생성 중 ValidationError 처리를 테스트한다."""

    class ValidationErrorProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise ValidationError("Invalid project data")

    repo = ValidationErrorProjectRepository()
    use_case = CreateProjectUseCase(repo)
    request = CreateProjectRequest(
        name="Test Project", description="Test Description"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid project data" in result.error.message


def test_create_project_handles_business_rule_violation():
    """프로젝트 생성 중 BusinessRuleViolation 처리를 테스트한다."""

    class BusinessRuleProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise BusinessRuleViolation("Project limit exceeded")

    repo = BusinessRuleProjectRepository()
    use_case = CreateProjectUseCase(repo)
    request = CreateProjectRequest(
        name="Test Project", description="Test Description"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Project limit exceeded" in result.error.message


def test_complete_project_handles_validation_error():
    """프로젝트 완료 중 ValidationError 처리를 테스트한다."""
    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)

    class ValidationErrorProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise ValidationError("Invalid completion state")

    project_repo = ValidationErrorProjectRepository()
    project_repo._projects[project.id] = project  # 프로젝트를 직접 추가
    task_repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid completion state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_project_fails_with_malformed_project_id():
    """작업 생성 중 존재하지 않는 프로젝트 ID 처리를 테스트한다."""
    project_repo = InMemoryProjectRepository()

    # ValueError가 발생하는지 테스트
    with pytest.raises(ValueError, match="잘못된 프로젝트 ID 형식입니다"):
        _ = CompleteProjectRequest(
            project_id="malformed project id",
        )


def test_complete_project_handles_business_rule_violation():
    """프로젝트 완료 중 BusinessRuleViolation 처리를 테스트한다."""
    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)

    class BusinessRuleProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            raise BusinessRuleViolation(
                "Cannot complete project in current state"
            )

    project_repo = BusinessRuleProjectRepository()
    project_repo._projects[project.id] = project  # 프로젝트를 직접 추가
    task_repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION
    assert "Cannot complete project in current state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_project_handles_validation_error_from_task():
    """프로젝트 완료 중 작업 연산에서 발생하는 ValidationError 처리를 테스트한다."""
    project = Project(name="Test Project")
    task = Task(title="Test Task", description="Test")
    project.add_task(task)

    class ValidationErrorTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            raise ValidationError("Invalid task completion state")

    project_repo = InMemoryProjectRepository()
    project_repo._projects[project.id] = project  # 프로젝트를 직접 추가
    task_repo = ValidationErrorTaskRepository()
    notifications = NotificationRecorder()

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    result = use_case.execute(request)

    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR
    assert "Invalid task completion state" in result.error.message
    assert not notifications.completed_tasks


def test_complete_project_rolls_back_on_validation_error():
    """ValidationError 발생 시 프로젝트와 작업 상태가 롤백되는지 테스트한다."""
    # 작업이 포함된 프로젝트 설정
    project = Project(name="Test Project")
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    project.add_task(task1)
    project.add_task(task2)

    # 프로젝트 저장 시 실패하지만 작업 저장은 허용하는 리포지토리
    class FailingProjectRepository(InMemoryProjectRepository):
        def save(self, project):
            if project.status == ProjectStatus.COMPLETED:
                raise ValidationError("Cannot complete project")
            super().save(project)

    project_repo = FailingProjectRepository()
    task_repo = InMemoryTaskRepository()
    notifications = NotificationRecorder()

    # 초기 상태 저장
    project_repo.save(project)
    task_repo.save(task1)
    task_repo.save(task2)

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    # 유스 케이스 실행 (실패해야 함)
    result = use_case.execute(request)

    # 실패 확인
    assert not result.is_success
    assert result.error.code == ErrorCode.VALIDATION_ERROR

    # 프로젝트 상태가 롤백되었는지 확인
    saved_project = project_repo.get(project.id)
    assert saved_project.status == ProjectStatus.ACTIVE

    # 작업 상태가 롤백되었는지 확인
    for task in [task1, task2]:
        saved_task = task_repo.get(task.id)
        assert saved_task.status == TaskStatus.TODO
        assert saved_task.completed_at is None
        assert saved_task.completion_notes is None


def test_complete_project_rolls_back_on_business_rule_violation():
    """BusinessRuleViolation 발생 시 프로젝트와 작업 상태가 롤백되는지 테스트한다."""
    # 작업이 포함된 프로젝트 설정
    project = Project(name="Test Project")
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    project.add_task(task1)
    project.add_task(task2)

    # 마지막 작업 저장 시 실패하는 리포지토리
    class FailingTaskRepository(InMemoryTaskRepository):
        def save(self, task):
            if (
                task.status == TaskStatus.DONE and task.title == "Task 2"
            ):  # 두 번째 작업에서 실패
                raise BusinessRuleViolation("Task limit reached")
            super().save(task)

    project_repo = InMemoryProjectRepository()
    task_repo = FailingTaskRepository()
    notifications = NotificationRecorder()

    # 초기 상태 저장
    project_repo.save(project)
    task_repo.save(task1)
    task_repo.save(task2)

    use_case = CompleteProjectUseCase(project_repo, task_repo, notifications)
    request = CompleteProjectRequest(
        project_id=str(project.id), completion_notes="Done!"
    )

    # 유스 케이스 실행 (실패해야 함)
    result = use_case.execute(request)

    # 실패 확인
    assert not result.is_success
    assert result.error.code == ErrorCode.BUSINESS_RULE_VIOLATION

    # 프로젝트 상태가 롤백되었는지 확인
    saved_project = project_repo.get(project.id)
    assert saved_project.status == ProjectStatus.ACTIVE

    # 모든 작업 상태가 롤백되었는지 확인
    for task in [task1, task2]:
        saved_task = task_repo.get(task.id)
        assert saved_task.status == TaskStatus.TODO
        assert saved_task.completed_at is None
        assert saved_task.completion_notes is None

    # 알림이 유지되지 않았는지 확인
    assert not notifications.completed_tasks
