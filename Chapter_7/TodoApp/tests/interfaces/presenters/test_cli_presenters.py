import dataclasses
from datetime import datetime, timezone
from uuid import UUID
import pytest

from todo_app.domain.value_objects import ProjectStatus, ProjectType
from todo_app.domain.value_objects import TaskStatus, Priority
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.interfaces.presenters.cli import CliTaskPresenter, CliProjectPresenter


@pytest.fixture
def task_presenter():
    return CliTaskPresenter()


@pytest.fixture
def project_presenter():
    return CliProjectPresenter()


@pytest.fixture
def sample_task_response():
    return TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Test Task",
        description="Test Description",
        status=TaskStatus.IN_PROGRESS,
        priority=Priority.HIGH,
        due_date=datetime(2024, 1, 21, tzinfo=timezone.utc),
        project_id="660e8400-e29b-41d4-a716-446655440000",
        completion_date=None,
        completion_notes=None,
    )


def test_cli_task_presenter_formats_task(task_presenter, sample_task_response):
    """작업 프레젠터가 CLI를 위해 작업 데이터를 올바르게 포맷하는지 테스트한다."""
    vm = task_presenter.present_task(sample_task_response)

    assert vm.id == "550e8400-e29b-41d4-a716-446655440000"
    assert vm.title == "Test Task"
    assert vm.status_display == "[IN_PROGRESS]"
    assert vm.priority_display == "높음"
    assert vm.due_date_display == "기한 초과 - 마감: 2024-01-21"
    assert vm.project_display == "Project: 660e8400-e29b-41d4-a716-446655440000"
    assert vm.completion_info == "미완료"


def test_cli_task_presenter_handles_completed_task(task_presenter):
    """프레젠터가 완료된 작업을 올바르게 포맷하는지 테스트한다."""
    completed_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    response = TaskResponse(
        id="123",
        project_id="456",
        title="Test Task",
        description="Test Description",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        completion_date=completed_date,
        completion_notes="All done",
    )

    vm = task_presenter.present_task(response)
    assert vm.status_display == "[DONE]"
    assert vm.completion_info == "2024-01-20 00:00에 완료 - All done"


@pytest.fixture
def sample_project_response(sample_task_response):
    return ProjectResponse(
        id="660e8400-e29b-41d4-a716-446655440000",
        name="Test Project",
        project_type=ProjectType.REGULAR,
        description="Test Description",
        status=ProjectStatus.ACTIVE,
        completion_date=None,
        tasks=[sample_task_response],
    )


def test_cli_project_presenter_formats_project(project_presenter, sample_project_response):
    """프로젝트 프레젠터가 CLI를 위해 프로젝트 데이터를 올바르게 포맷하는지 테스트한다."""
    vm = project_presenter.present_project(sample_project_response)

    assert vm.id == "660e8400-e29b-41d4-a716-446655440000"
    assert vm.name == "Test Project"
    assert vm.description == "Test Description"
    assert vm.status_display == "[ACTIVE]"
    assert vm.task_count == 1
    assert vm.completed_task_count == 0
    assert vm.completion_info == "미완료"


def test_cli_project_presenter_formats_completed_project(project_presenter):
    """프레젠터가 완료된 프로젝트를 올바르게 포맷하는지 테스트한다."""
    completed_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    response = ProjectResponse(
        id="123",
        name="Test Project",
        project_type=ProjectType.REGULAR,
        description="Description",
        status=ProjectStatus.COMPLETED,
        completion_date=completed_date,
        tasks=[],
    )

    vm = project_presenter.present_project(response)
    assert vm.status_display == "[COMPLETED]"
    assert vm.completion_info == "2024-01-20 00:00에 완료"


def test_cli_presenter_error_formatting(task_presenter, project_presenter):
    """프레젠터가 오류를 일관되게 포맷하는지 테스트한다."""
    task_error = task_presenter.present_error("Task error", "VALIDATION_ERROR")
    project_error = project_presenter.present_error("Project error", "NOT_FOUND")

    assert task_error.message == "Task error"
    assert task_error.code == "VALIDATION_ERROR"
    assert project_error.message == "Project error"
    assert project_error.code == "NOT_FOUND"


def test_cli_task_presenter_formats_high_priority_task(task_presenter, sample_task_response):
    """높은 우선순위 작업의 포맷팅을 테스트한다."""
    high_priority_task = dataclasses.replace(sample_task_response, priority=Priority.HIGH)
    vm = task_presenter.present_task(high_priority_task)
    assert vm.priority_display == "높음"


def test_cli_task_presenter_formats_task_without_due_date(task_presenter, sample_task_response):
    """마감일이 없는 작업의 포맷팅을 테스트한다."""
    task = dataclasses.replace(sample_task_response, due_date=None)
    vm = task_presenter.present_task(task)
    assert vm.due_date_display == "마감일 없음"


def test_cli_task_presenter_formats_task_without_project(task_presenter, sample_task_response):
    """프로젝트가 없는 작업의 포맷팅을 테스트한다."""
    task = dataclasses.replace(sample_task_response, project_id=None)
    vm = task_presenter.present_task(task)
    assert vm.project_display == ""


def test_cli_project_presenter_formats_empty_project(project_presenter):
    """작업이 없는 프로젝트의 포맷팅을 테스트한다."""
    project = ProjectResponse(
        id="123e4567-e89b-12d3-a456-426614174000",
        name="Empty Project",
        project_type=ProjectType.REGULAR,
        description="No tasks",
        status=ProjectStatus.ACTIVE,
        completion_date=None,
        tasks=[],
    )

    vm = project_presenter.present_project(project)
    assert vm.task_count == 0
    assert vm.completed_task_count == 0


def test_cli_project_presenter_formats_project_with_mixed_tasks(project_presenter):
    """완료된 작업과 미완료 작업이 모두 있는 프로젝트의 포맷팅을 테스트한다."""
    completed_task = TaskResponse(
        id="123",
        project_id="456",
        title="Done Task",
        description="Done",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
    )

    in_progress_task = TaskResponse(
        id="456",
        project_id="456",
        title="In Progress Task",
        description="Working",
        status=TaskStatus.IN_PROGRESS,
        priority=Priority.MEDIUM,
    )

    project = ProjectResponse(
        id="123e4567-e89b-12d3-a456-426614174000",
        name="Mixed Project",
        project_type=ProjectType.REGULAR,
        description="Mixed tasks",
        status=ProjectStatus.ACTIVE,
        completion_date=None,
        tasks=[completed_task, in_progress_task],
    )

    vm = project_presenter.present_project(project)
    assert vm.task_count == 2
    assert vm.completed_task_count == 1


def test_cli_presenters_error_formatting_consistency(task_presenter, project_presenter):
    """두 프레젠터가 오류를 일관되게 포맷하는지 테스트한다."""
    error_message = "Test error"
    error_code = "TEST_ERROR"

    task_error = task_presenter.present_error(error_message, error_code)
    project_error = project_presenter.present_error(error_message, error_code)

    assert task_error.message == project_error.message == error_message
    assert task_error.code == project_error.code == error_code


def test_cli_project_presenter_handles_project_completion(project_presenter):
    """프로젝트 완료 정보 프레젠팅을 테스트한다."""
    completion_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    completion_response = CompleteProjectResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        status=ProjectStatus.COMPLETED,
        completion_date=completion_date,
        task_count=5,
        completion_notes="Project completed successfully",
    )

    vm = project_presenter.present_completion(completion_response)
    assert vm.project_id == "550e8400-e29b-41d4-a716-446655440000"
    assert vm.completion_notes == "Project completed successfully"


def test_cli_project_presenter_task_aggregation(project_presenter):
    """프레젠터가 완료된 작업과 전체 작업 수를 올바르게 계산하는지 테스트한다."""
    tasks = [
        TaskResponse(  # Completed task
            id="123",
            project_id="456",
            title="Done Task",
            description="Done",
            status=TaskStatus.DONE,
            priority=Priority.MEDIUM,
            completion_date=datetime.now(timezone.utc),
        ),
        TaskResponse(  # In progress task
            id="456",
            project_id="789",
            title="Active Task",
            description="Doing",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
        ),
        TaskResponse(  # Todo task
            id="789",
            project_id="012",
            title="Future Task",
            description="To do",
            status=TaskStatus.TODO,
            priority=Priority.LOW,
        ),
    ]

    project_response = ProjectResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Project",
        project_type=ProjectType.REGULAR,
        description="Testing task counts",
        status=ProjectStatus.ACTIVE,
        completion_date=None,
        tasks=tasks,
    )

    vm = project_presenter.present_project(project_response)
    assert vm.task_count == 3
    assert vm.completed_task_count == 1


def test_cli_project_presenter_formats_long_description(project_presenter):
    """프레젠터가 긴 프로젝트 설명을 적절히 처리하는지 테스트한다."""
    long_description = "This is a very long description " * 10  # Creates a long string

    project_response = ProjectResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Project",
        project_type=ProjectType.REGULAR,
        description=long_description,
        status=ProjectStatus.ACTIVE,
        completion_date=None,
        tasks=[],
    )

    vm = project_presenter.present_project(project_response)
    assert vm.description == long_description  # Verify description is preserved


def test_cli_project_presenter_formats_special_characters(project_presenter):
    """프레젠터가 프로젝트 필드의 특수 문자를 처리하는지 테스트한다."""
    project_response = ProjectResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test & Project!",
        project_type=ProjectType.REGULAR,
        description="Testing @ special # characters!",
        status=ProjectStatus.ACTIVE,
        completion_date=None,
        tasks=[],
    )

    vm = project_presenter.present_project(project_response)
    assert vm.name == "Test & Project!"
    assert vm.description == "Testing @ special # characters!"


def test_cli_task_presenter_formats_completed_task_with_notes(task_presenter):
    """완료 메모가 있는 완료된 작업의 포맷팅을 테스트한다."""
    completion_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        project_id="660e8400-e29b-41d4-a716-446655440000",
        title="Test Task",
        description="Test Description",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        completion_date=completion_date,
        completion_notes="Task completed with additional notes",
    )

    vm = task_presenter.present_task(task_response)
    assert vm.status_display == "[DONE]"
    assert "Task completed with additional notes" in vm.completion_info


def test_cli_project_presenter_handles_empty_completion_notes(project_presenter):
    """메모 없는 프로젝트 완료 프레젠팅을 테스트한다."""
    completion_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    completion_response = CompleteProjectResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        status=ProjectStatus.COMPLETED,
        completion_date=completion_date,
        task_count=5,
        completion_notes=None,
    )

    vm = project_presenter.present_completion(completion_response)
    assert vm.completion_notes is None


def test_cli_task_presenter_formats_overdue_task(task_presenter):
    """기한 초과 작업의 포맷팅을 테스트한다."""
    past_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        project_id="660e8400-e29b-41d4-a716-446655440000",
        title="Overdue Task",
        description="This task is overdue",
        status=TaskStatus.TODO,
        priority=Priority.HIGH,
        due_date=past_date,
    )

    vm = task_presenter.present_task(task_response)
    assert "기한 초과" in vm.due_date_display


def test_presenter_error_validation_codes():
    """프레젠터가 모든 가능한 오류 코드를 일관되게 처리하는지 테스트한다."""
    error_codes = ["VALIDATION_ERROR", "NOT_FOUND", "BUSINESS_RULE_VIOLATION"]
    presenter = CliTaskPresenter()

    for code in error_codes:
        error_vm = presenter.present_error(f"Test error for {code}", code)
        assert error_vm.code == code
        assert error_vm.message.startswith("Test error for")


def test_presenters_handle_empty_strings(task_presenter, project_presenter):
    """프레젠터가 다양한 필드의 빈 문자열을 처리하는지 테스트한다."""
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        project_id="660e8400-e29b-41d4-a716-446655440000",
        title="",  # Empty title
        description="",  # Empty description
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
    )

    vm = task_presenter.present_task(task_response)
    assert vm.title == ""
    assert vm.description == ""


def test_presenters_handle_very_long_content(task_presenter):
    """프레젠터가 매우 긴 콘텐츠를 적절히 처리하는지 테스트한다."""
    very_long_description = "A" * 1000
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        project_id="660e8400-e29b-41d4-a716-446655440000",
        title="Test Task",
        description=very_long_description,
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
    )

    vm = task_presenter.present_task(task_response)
    assert len(vm.description) == len(very_long_description)
