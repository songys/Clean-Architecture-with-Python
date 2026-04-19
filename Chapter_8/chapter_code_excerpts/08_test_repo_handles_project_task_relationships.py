import pytest


# pytest.fixture: 테스트 간 공유되는 재사용 가능한 테스트 설정
# tmp_path는 pytest 내장 픽스처로, 테스트마다 격리된 임시 디렉토리 제공
@pytest.fixture
def repository(tmp_path):  # tmp_path는 임시 디렉토리를 위한 pytest 내장 기능
    """임시 디렉토리를 사용하여 리포지토리를 생성"""
    return FileTaskRepository(data_dir=tmp_path)

# 통합 테스트: 실제 파일 저장소를 사용한 프로젝트-작업 관계 검증
# 단위 테스트(Mock)로는 확인할 수 없는 실제 영속성 동작 검증
def test_repo_handles_project_task_relationships(tmp_path):
    # 준비 - 실제 파일 저장소 인스턴스 생성 및 연결
    task_repo = FileTaskRepository(tmp_path)
    project_repo = FileProjectRepository(tmp_path)
    project_repo.set_task_repository(task_repo)  # 저장소 간 연결 설정

    # 리포지토리를 통해 프로젝트와 작업 생성
    project = Project(name="Test Project",
                      description="Testing relationships")
    project_repo.save(project)

    task = Task(title="Test Task",
                description="Testing relationships",
                project_id=project.id)  # 작업을 프로젝트에 연결
    task_repo.save(task)
    # 실행 - 프로젝트와 해당 작업들을 로드
    loaded_project = project_repo.get(project.id)

    # 검증 - 프로젝트 로드 시 연관된 작업이 함께 로드되는지 확인
    assert len(loaded_project.tasks) == 1
    assert loaded_project.tasks[0].title == "Test Task"

