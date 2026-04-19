# todo_app/tests/application/test_dtos.py
"""DTO 유효성 검사 로직에 대한 테스트."""

from datetime import datetime, timedelta

import pytest

from todo_app.application.dtos.project_dtos import (
    CompleteProjectRequest,
    CreateProjectRequest,
)
from todo_app.application.dtos.task_dtos import (
    CompleteTaskRequest,
    CreateTaskRequest,
    SetTaskPriorityRequest,
)


class TestCompleteTaskRequest:
    def test_valid_request(self):
        """유효한 데이터로 요청 생성을 테스트한다."""
        request = CompleteTaskRequest(
            task_id="123e4567-e89b-12d3-a456-426614174000",
            completion_notes="Task completed successfully",
        )
        assert request.task_id == "123e4567-e89b-12d3-a456-426614174000"
        assert request.completion_notes == "Task completed successfully"

    def test_empty_task_id(self):
        """빈 task_id의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Task ID is required"):
            CompleteTaskRequest(task_id="   ", completion_notes="Done")

    def test_completion_notes_too_long(self):
        """완료 메모 길이의 유효성 검사를 테스트한다."""
        with pytest.raises(
            ValueError, match="Completion notes cannot exceed 1000 characters"
        ):
            CompleteTaskRequest(
                task_id="123e4567-e89b-12d3-a456-426614174000",
                completion_notes="x" * 1001,
            )


class TestCreateTaskRequest:
    def test_valid_request(self):
        """유효한 데이터로 요청 생성을 테스트한다."""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            due_date=(datetime.now() + timedelta(days=1)).isoformat(),
            priority="HIGH",
            project_id="123e4567-e89b-12d3-a456-426614174000",
        )
        assert request.title == "Test Task"
        assert request.description == "Test Description"

    def test_empty_title(self):
        """빈 제목의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Title is required"):
            CreateTaskRequest(title="   ", description="Test")

    def test_title_too_long(self):
        """제목 길이의 유효성 검사를 테스트한다."""
        with pytest.raises(
            ValueError, match="Title cannot exceed 200 characters"
        ):
            CreateTaskRequest(title="x" * 201, description="Test")

    def test_description_too_long(self):
        """설명 길이의 유효성 검사를 테스트한다."""
        with pytest.raises(
            ValueError, match="Description cannot exceed 2000 characters"
        ):
            CreateTaskRequest(title="Test", description="x" * 2001)


class TestSetTaskPriorityRequest:
    def test_valid_request(self):
        """유효한 데이터로 요청 생성을 테스트한다."""
        request = SetTaskPriorityRequest(
            task_id="123e4567-e89b-12d3-a456-426614174000", priority="HIGH"
        )
        assert request.task_id == "123e4567-e89b-12d3-a456-426614174000"
        assert request.priority == "HIGH"

    def test_empty_task_id(self):
        """빈 task_id의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Task ID is required"):
            SetTaskPriorityRequest(task_id="   ", priority="HIGH")

    def test_invalid_priority(self):
        """잘못된 우선순위의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Priority must be one of:"):
            SetTaskPriorityRequest(
                task_id="123e4567-e89b-12d3-a456-426614174000",
                priority="INVALID",
            )

    def test_empty_priority(self):
        """빈 우선순위의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Priority must be one of:"):
            SetTaskPriorityRequest(
                task_id="123e4567-e89b-12d3-a456-426614174000", priority="   "
            )


class TestCreateProjectRequest:
    def test_valid_request(self):
        """유효한 데이터로 요청 생성을 테스트한다."""
        request = CreateProjectRequest(
            name="Test Project", description="Test Description"
        )
        assert request.name == "Test Project"
        assert request.description == "Test Description"

    def test_empty_name(self):
        """빈 이름의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Project name is required"):
            CreateProjectRequest(name="   ", description="Test")

    def test_name_too_long(self):
        """이름 길이의 유효성 검사를 테스트한다."""
        with pytest.raises(
            ValueError, match="Project name cannot exceed 100 characters"
        ):
            CreateProjectRequest(name="x" * 101, description="Test")

    def test_description_too_long(self):
        """설명 길이의 유효성 검사를 테스트한다."""
        with pytest.raises(
            ValueError, match="Description cannot exceed 2000 characters"
        ):
            CreateProjectRequest(name="Test", description="x" * 2001)


class TestCompleteProjectRequest:
    def test_valid_request(self):
        """유효한 데이터로 요청 생성을 테스트한다."""
        request = CompleteProjectRequest(
            project_id="123e4567-e89b-12d3-a456-426614174000",
            completion_notes="Project completed successfully",
        )
        assert request.project_id == "123e4567-e89b-12d3-a456-426614174000"
        assert request.completion_notes == "Project completed successfully"

    def test_empty_project_id(self):
        """빈 project_id의 유효성 검사를 테스트한다."""
        with pytest.raises(ValueError, match="Project ID is required"):
            CompleteProjectRequest(project_id="   ", completion_notes="Done")

    def test_completion_notes_too_long(self):
        """완료 메모 길이의 유효성 검사를 테스트한다."""
        with pytest.raises(
            ValueError, match="Completion notes cannot exceed 1000 characters"
        ):
            CompleteProjectRequest(
                project_id="123e4567-e89b-12d3-a456-426614174000",
                completion_notes="x" * 1001,
            )


def test_execution_params_conversion():
    """DTO에서 실행 매개변수로의 변환을 테스트한다."""
    # Test CreateTaskRequest conversion
    task_request = CreateTaskRequest(
        title="Test Task",
        description="Test Description",
        due_date=(datetime.now() + timedelta(days=1)).isoformat(),
        priority="HIGH",
        project_id="123e4567-e89b-12d3-a456-426614174000",
    )
    task_params = task_request.to_execution_params()
    assert task_params["title"] == "Test Task"
    assert task_params["description"] == "Test Description"
    assert "deadline" in task_params
    assert "priority" in task_params
    assert "project_id" in task_params

    # Test CreateProjectRequest conversion
    project_request = CreateProjectRequest(
        name="Test Project", description="Test Description"
    )
    project_params = project_request.to_execution_params()
    assert project_params["name"] == "Test Project"
    assert project_params["description"] == "Test Description"
