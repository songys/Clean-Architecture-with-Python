# TaskViewModel의 생성과 불변성(frozen) 검증 테스트
import dataclasses
import pytest

from todo_app.interfaces.view_models.task_vm import TaskViewModel


def test_task_view_model_creation():
    """모든 필드를 포함한 TaskViewModel 생성 테스트"""
    vm = TaskViewModel(
        id="123",
        title="Test Task",
        description="Test Description",
        status_display="[IN_PROGRESS]",
        priority_display="HIGH",
        due_date_display="2024-01-21",
        project_display="Project: Test",
        completion_info="Not completed",
    )

    assert vm.id == "123"
    assert vm.title == "Test Task"
    assert vm.description == "Test Description"
    assert vm.status_display == "[IN_PROGRESS]"
    assert vm.priority_display == "HIGH"
    assert vm.due_date_display == "2024-01-21"
    assert vm.project_display == "Project: Test"
    assert vm.completion_info == "Not completed"


def test_task_view_model_immutability():
    """TaskViewModel의 불변성 테스트"""
    vm = TaskViewModel(
        id="123",
        title="Test Task",
        description="Test Description",
        status_display="[TODO]",
        priority_display="LOW",
        due_date_display="2024-01-21",
        project_display="Project: Test",
        completion_info="Not completed",
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        vm.title = "New Title"
