from datetime import datetime, timedelta
from uuid import UUID

import pytest

from todo_app.domain.entities.project import Project
from todo_app.application.dtos.task_dtos import CreateTaskRequest
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.infrastructure.persistence.file import FileProjectRepository
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority, ProjectType
from unittest.mock import Mock

from todo_app.application.use_cases.task_use_cases import (
    CompleteTaskRequest,
    CompleteTaskUseCase,
    CreateTaskUseCase,
)


# 도메인 엔터티 단위 테스트 - 인프라 의존성 없이 순수 비즈니스 로직 검증
def test_new_task_priority():
    """순수하게 도메인 로직에 집중한 깔끔한 테스트."""
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    assert task.priority == Priority.MEDIUM


def test_task_completion_captures_completion_time():
    """작업 완료가 완료 타임스탬프를 기록하는지 테스트한다."""
    # Arrange
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )

    # Act
    task.complete()

    # Assert
    assert task.completed_at is not None
    assert (datetime.now() - task.completed_at) < timedelta(seconds=1)


# 유스 케이스 테스트 - Mock으로 리포지토리/알림 서비스 대체
# 클린 아키텍처 덕분에 의존성 주입으로 쉽게 테스트 가능
def test_successful_task_completion():
    """목 의존성을 사용한 작업 완료 테스트."""
    # Arrange
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    task_repo = Mock()
    task_repo.get.return_value = task
    notification_service = Mock()

    use_case = CompleteTaskUseCase(
        task_repository=task_repo, notification_service=notification_service
    )
    request = CompleteTaskRequest(task_id=str(task.id))
    # Act
    result = use_case.execute(request)

    # Assert
    assert result.is_success
    task_repo.save.assert_called_once_with(task)
    notification_service.notify_task_completed.assert_called_once_with(task)


# 매개변수화된 테스트 - 다양한 입력 시나리오를 하나의 테스트로 검증
@pytest.mark.parametrize(
    "request_data,expected_behavior",
    [
        # 기본 우선순위 작업 생성
        (
            {"title": "Test Task", "description": "Basic creation"},
            {"project_type": ProjectType.INBOX, "priority": Priority.MEDIUM},
        ),
        # 높은 우선순위 작업
        (
            {"title": "Priority Task", "description": "High priority", "priority": "HIGH"},
            {"project_type": ProjectType.INBOX, "priority": Priority.HIGH},
        ),
    ],
    ids=["basic-task", "high-priority-task"],
)
def test_task_creation_scenarios(request_data, expected_behavior, tmp_path):
    """작업 생성 유스 케이스가 다양한 입력 시나리오를 올바르게 처리하는지 테스트한다."""
    # Arrange
    task_repo = Mock(spec=TaskRepository)
    project_repo = FileProjectRepository(tmp_path)  # Real project repo for INBOX

    use_case = CreateTaskUseCase(task_repository=task_repo, project_repository=project_repo)

    # Act - 실행
    result = use_case.execute(CreateTaskRequest(**request_data))

    # Assert - 검증
    assert result.is_success
    created_task = result.value
    assert UUID(created_task.project_id) == project_repo.get_inbox().id
    assert created_task.priority == expected_behavior["priority"]
