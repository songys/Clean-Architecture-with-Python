# CLI 프레젠터 테스트 - 도메인 응답이 CLI 출력용 뷰 모델로 올바르게 변환되는지 검증
# - 프레젠터의 형식화 로직(상태, 우선순위, 마감일, 완료 정보)을 독립적으로 테스트
import dataclasses
from datetime import datetime, timezone
import pytest

from todo_app.domain.value_objects import TaskStatus, Priority
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.presenters.cli import CliTaskPresenter


@pytest.fixture
def task_presenter():
    return CliTaskPresenter()


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
    """작업 프레젠터가 CLI용으로 작업 데이터를 올바르게 포맷하는지 테스트"""
    vm = task_presenter.present_task(sample_task_response)

    assert vm.id == "550e8400-e29b-41d4-a716-446655440000"
    assert vm.title == "Test Task"
    assert vm.status_display == "[IN_PROGRESS]"
    assert vm.priority_display == "High"
    assert vm.due_date_display == "OVERDUE - Due: 2024-01-21"
    assert vm.project_display == "Project: 660e8400-e29b-41d4-a716-446655440000"
    assert vm.completion_info == "Not completed"


def test_cli_task_presenter_handles_completed_task(task_presenter):
    """프레젠터가 완료된 작업을 올바르게 포맷하는지 테스트"""
    completed_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    response = TaskResponse(
        id="123",
        title="Test Task",
        description="Test Description",
        status=TaskStatus.DONE,
        priority=Priority.MEDIUM,
        completion_date=completed_date,
        completion_notes="All done",
    )

    vm = task_presenter.present_task(response)
    assert vm.status_display == "[DONE]"
    assert vm.completion_info == "Completed on 2024-01-20 00:00 - All done"


def test_cli_task_presenter_formats_high_priority_task(task_presenter, sample_task_response):
    """높은 우선순위 작업 포맷팅 테스트"""
    high_priority_task = dataclasses.replace(sample_task_response, priority=Priority.HIGH)
    vm = task_presenter.present_task(high_priority_task)
    assert vm.priority_display == "High"


def test_cli_task_presenter_formats_task_without_due_date(task_presenter, sample_task_response):
    """마감일이 없는 작업 포맷팅 테스트"""
    task = dataclasses.replace(sample_task_response, due_date=None)
    vm = task_presenter.present_task(task)
    assert vm.due_date_display == "No due date"


def test_cli_task_presenter_formats_completed_task_with_notes(task_presenter):
    """완료 메모가 있는 완료된 작업 포맷팅 테스트"""
    completion_date = datetime(2024, 1, 20, tzinfo=timezone.utc)
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
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


def test_cli_task_presenter_formats_overdue_task(task_presenter):
    """기한 초과 작업 포맷팅 테스트"""
    past_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Overdue Task",
        description="This task is overdue",
        status=TaskStatus.TODO,
        priority=Priority.HIGH,
        due_date=past_date,
    )

    vm = task_presenter.present_task(task_response)
    assert "OVERDUE" in vm.due_date_display


def test_presenter_error_validation_codes():
    """프레젠터가 모든 가능한 오류 코드를 일관되게 처리하는지 테스트"""
    error_codes = ["VALIDATION_ERROR", "NOT_FOUND", "BUSINESS_RULE_VIOLATION"]
    presenter = CliTaskPresenter()

    for code in error_codes:
        error_vm = presenter.present_error(f"Test error for {code}", code)
        assert error_vm.code == code
        assert error_vm.message.startswith("Test error for")


def test_presenters_handle_very_long_content(task_presenter):
    """프레젠터가 매우 긴 콘텐츠를 적절하게 처리하는지 테스트"""
    very_long_description = "A" * 1000
    task_response = TaskResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Test Task",
        description=very_long_description,
        status=TaskStatus.TODO,
        priority=Priority.MEDIUM,
    )

    vm = task_presenter.present_task(task_response)
    assert len(vm.description) == len(very_long_description)
