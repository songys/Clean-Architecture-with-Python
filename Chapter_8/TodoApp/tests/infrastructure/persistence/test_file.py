from uuid import UUID
import pytest
from todo_app.application.dtos.task_dtos import CreateTaskRequest
from todo_app.application.use_cases.task_use_cases import CreateTaskUseCase
from todo_app.domain.value_objects import ProjectType
from todo_app.domain.entities.task import Task
from todo_app.domain.entities.project import Project
from todo_app.infrastructure.persistence.file import FileTaskRepository, FileProjectRepository


# === 통합 테스트: 실제 파일 저장소를 사용한 영속성 계층 검증 ===
# 단위 테스트(Mock)로는 확인할 수 없는 실제 파일 I/O 및 데이터 변환 동작 검증

# pytest 픽스처: 테스트 간 공유되는 저장소 인스턴스 제공
@pytest.fixture  # Pytest 픽스처는 재사용 가능한 테스트 의존성을 제공한다
def repository(tmp_path):  # tmp_path는 임시 디렉토리를 위한 pytest 내장 기능
    """임시 디렉토리를 사용하여 리포지토리를 생성한다."""
    return FileTaskRepository(data_dir=tmp_path)


# 프로젝트-작업 관계 통합 테스트: 저장 후 로드 시 관계가 유지되는지 검증
def test_repo_handles_project_task_relationships(tmp_path):
    """리포지토리가 엔터티 관계를 처리하는지 검증하는 통합 테스트."""
    # 준비 - 실제 파일 저장소 인스턴스 생성 및 연결
    task_repo = FileTaskRepository(tmp_path)
    project_repo = FileProjectRepository(tmp_path)
    project_repo.set_task_repository(task_repo)

    # 리포지토리를 통해 프로젝트와 작업을 생성
    project = Project(name="Test Project", description="Testing relationships")
    project_repo.save(project)

    task = Task(title="Test Task", description="Testing relationships", project_id=project.id)
    task_repo.save(task)

    # 실행 - 작업이 포함된 프로젝트를 로드
    loaded_project = project_repo.get(project.id)

    # 검증 - 프로젝트 로드 시 연관된 작업이 함께 복원되는지 확인
    assert len(loaded_project.tasks) == 1
    assert loaded_project.tasks[0].title == "Test Task"


# INBOX 자동 생성 및 영속성 검증: 저장소 재생성 시에도 동일한 INBOX 유지 확인
def test_repository_automatically_creates_inbox(tmp_path):
    """프로젝트 리포지토리가 인스턴스화 간에 inbox 프로젝트를 유지하는지 테스트한다."""
    # 준비 - 초기 리포지토리를 생성하고 Inbox 존재를 확인
    initial_repo = FileProjectRepository(tmp_path)
    initial_inbox = initial_repo.get_inbox()
    assert initial_inbox.name == "INBOX"
    assert initial_inbox.project_type == ProjectType.INBOX

    # 실행 - 동일한 디렉토리를 가리키는 새 리포지토리 인스턴스 생성
    new_repo = FileProjectRepository(tmp_path)

    # 검증 - 새 인스턴스가 동일한 Inbox를 유지 (중복 생성 없음)
    persisted_inbox = new_repo.get_inbox()
    assert persisted_inbox.id == initial_inbox.id
    assert persisted_inbox.project_type == ProjectType.INBOX


# 영속성 통합 테스트: 유스케이스를 통해 생성된 작업이 실제로 파일에 저장되는지 검증
def test_task_creation_with_persistence(tmp_path):
    """실제 영속성을 사용한 작업 생성 유스 케이스 테스트."""
    # 준비 - 실제 파일 저장소 구성
    task_repo = FileTaskRepository(tmp_path)
    project_repo = FileProjectRepository(tmp_path)
    project_repo.set_task_repository(task_repo)

    use_case = CreateTaskUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
    )

    # 실행
    result = use_case.execute(CreateTaskRequest(title="Test Task", description="Integration test"))

    # 검증 - 실제 저장소에서 작업을 다시 읽어 영속성 확인
    assert result.is_success
    created_task = task_repo.get(UUID(result.value.id))
    assert created_task.project_id == project_repo.get_inbox().id
