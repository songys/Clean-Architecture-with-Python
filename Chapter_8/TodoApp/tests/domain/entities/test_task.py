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


# === 도메인 엔티티 단위 테스트 ===
# 외부 의존성 없이 순수 도메인 객체만으로 비즈니스 규칙 검증

# 엔티티 기본값 검증: 새 Task의 기본 우선순위가 MEDIUM인지 확인
def test_new_task_priority():
    """순수하게 도메인 로직에 집중하는 깨끗한 테스트."""
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    assert task.priority == Priority.MEDIUM


# 엔티티 상태 전이 검증: complete() 호출 시 완료 타임스탬프 기록 확인
def test_task_completion_captures_completion_time():
    """작업 완료 시 완료 타임스탬프가 기록되는지 테스트한다."""
    # 준비
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )

    # 실행
    task.complete()

    # 검증
    assert task.completed_at is not None
    assert (datetime.now() - task.completed_at) < timedelta(seconds=1)


# === 유스케이스 단위 테스트 ===
# Mock 저장소와 Mock 알림 서비스를 사용하여 비즈니스 오케스트레이션 검증

# 작업 완료 유스케이스: 저장과 알림이 올바르게 호출되는지 검증
def test_successful_task_completion():
    """모의 의존성을 사용한 작업 완료 테스트."""
    # 준비 - Mock으로 외부 의존성 대체
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
    # 실행
    result = use_case.execute(request)

    # 검증 - 유스케이스 성공 여부와 Mock 호출 횟수 확인
    assert result.is_success
    task_repo.save.assert_called_once_with(task)
    notification_service.notify_task_completed.assert_called_once_with(task)


# parametrize: 하나의 테스트 함수로 여러 시나리오를 반복 검증
# 기본 작업과 높은 우선순위 작업 생성 시나리오를 각각 독립 실행
@pytest.mark.parametrize(
    "request_data,expected_behavior",
    [
        # 시나리오 1: 기본 우선순위 작업 생성
        (
            {"title": "Test Task", "description": "Basic creation"},
            {"project_type": ProjectType.INBOX, "priority": Priority.MEDIUM},
        ),
        # 시나리오 2: 높은 우선순위 작업
        (
            {"title": "Priority Task", "description": "High priority", "priority": "HIGH"},
            {"project_type": ProjectType.INBOX, "priority": Priority.HIGH},
        ),
    ],
    ids=["basic-task", "high-priority-task"],
)
def test_task_creation_scenarios(request_data, expected_behavior, tmp_path):
    """작업 생성 유스 케이스가 다양한 입력 시나리오를 올바르게 처리하는지 테스트한다."""
    # 준비 - Mock 작업 저장소 + 실제 프로젝트 저장소(INBOX 필요) 혼합 전략
    task_repo = Mock(spec=TaskRepository)
    project_repo = FileProjectRepository(tmp_path)  # Real project repo for INBOX

    use_case = CreateTaskUseCase(task_repository=task_repo, project_repository=project_repo)

    # 실행
    result = use_case.execute(CreateTaskRequest(**request_data))

    # 검증 - INBOX 자동 할당 및 우선순위 설정 확인
    assert result.is_success
    created_task = result.value
    assert UUID(created_task.project_id) == project_repo.get_inbox().id
    assert created_task.priority == expected_behavior["priority"]
