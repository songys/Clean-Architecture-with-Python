from uuid import UUID
import pytest
from todo_app.application.dtos.task_dtos import CreateTaskRequest
from todo_app.application.use_cases.task_use_cases import CreateTaskUseCase
from todo_app.domain.value_objects import ProjectType
from todo_app.domain.entities.task import Task
from todo_app.domain.entities.project import Project
from todo_app.infrastructure.persistence.file import FileTaskRepository, FileProjectRepository


# 파일 기반 리포지토리 통합 테스트 - 실제 JSON 파일 영속화 검증
@pytest.fixture  # Pytest 픽스처는 재사용 가능한 테스트 의존성을 제공
def repository(tmp_path):  # tmp_path는 임시 디렉터리를 위한 pytest 내장 기능
    """임시 디렉터리를 사용하여 리포지토리를 생성한다."""
    return FileTaskRepository(data_dir=tmp_path)


def test_repository_handles_project_task_relationships(tmp_path):
    """리포지토리가 엔터티 관계를 처리하는지 검증하는 통합 테스트."""
    # Arrange
    task_repo = FileTaskRepository(tmp_path)
    project_repo = FileProjectRepository(tmp_path)
    project_repo.set_task_repository(task_repo)

    # 리포지토리를 통해 프로젝트와 작업 생성
    project = Project(name="Test Project", description="Testing relationships")
    project_repo.save(project)

    task = Task(title="Test Task", description="Testing relationships", project_id=project.id)
    task_repo.save(task)

    # Act - 프로젝트와 작업을 함께 로드
    loaded_project = project_repo.get(project.id)

    # Assert
    assert len(loaded_project.tasks) == 1
    assert loaded_project.tasks[0].title == "Test Task"


def test_repository_automatically_creates_inbox(tmp_path):
    """프로젝트 리포지토리가 인스턴스화 간에 inbox 프로젝트를 유지하는지 테스트한다."""
    # Arrange - 초기 리포지토리 생성 및 Inbox 존재 확인
    initial_repo = FileProjectRepository(tmp_path)
    initial_inbox = initial_repo.get_inbox()
    assert initial_inbox.name == "INBOX"
    assert initial_inbox.project_type == ProjectType.INBOX

    # Act - 동일한 디렉터리를 가리키는 새 리포지토리 인스턴스 생성
    new_repo = FileProjectRepository(tmp_path)

    # Assert - 새 인스턴스가 동일한 Inbox를 유지
    persisted_inbox = new_repo.get_inbox()
    assert persisted_inbox.id == initial_inbox.id
    assert persisted_inbox.project_type == ProjectType.INBOX


def test_task_creation_with_persistence(tmp_path):
    """실제 영속성을 사용한 작업 생성 유스 케이스 테스트."""
    # Arrange
    task_repo = FileTaskRepository(tmp_path)
    project_repo = FileProjectRepository(tmp_path)
    project_repo.set_task_repository(task_repo)

    use_case = CreateTaskUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
    )

    # Act
    result = use_case.execute(CreateTaskRequest(title="Test Task", description="Integration test"))

    # Assert - 작업이 영속화되었는지 확인
    assert result.is_success
    created_task = task_repo.get(UUID(result.value.id))
    assert created_task.project_id == project_repo.get_inbox().id
