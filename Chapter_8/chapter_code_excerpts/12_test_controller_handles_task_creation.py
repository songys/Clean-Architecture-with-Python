import pytest


# === conftest.py 계층별 픽스처 구성 ===
# 클린 아키텍처의 계층 구조를 따르는 테스트 픽스처 조직 방식
# 각 conftest.py는 해당 계층의 테스트에서만 사용하는 공유 설정 제공

# tests/conftest.py - 모든 테스트에서 사용 가능한 루트 픽스처
@pytest.fixture
def sample_task_data():
    """테스트를 위한 기본 작업 속성 제공"""
    return {
        "title": "Test Task",
        "description": "Sample task for testing",
        "project_id": UUID("12345678-1234-5678-1234-567812345678"),
    }


# tests/domain/conftest.py - 도메인 계층 픽스처
# 상위 conftest의 sample_task_data를 의존성으로 사용하는 계층적 구조
@pytest.fixture
def domain_task(sample_task_data):
    """도메인 테스트를 위한 순수 Task 엔터티 제공"""
    return Task(**sample_task_data)


# tests/application/conftest.py - 애플리케이션 계층 픽스처
# 도메인 계층의 domain_task 픽스처를 받아 Mock 저장소를 구성
@pytest.fixture
def mock_task_repository(domain_task):
    """미리 구성된 모의 리포지토리 제공"""
    repo = Mock(spec=TaskRepository)
    repo.get.return_value = domain_task
    return repo


# tests/interfaces/conftest.py - 인터페이스 계층 픽스처
# 애플리케이션 계층의 Mock 저장소를 의존성으로 받아 컨트롤러 구성
@pytest.fixture
def task_controller(mock_task_repository, mock_notification_port):
    """올바르게 구성된 TaskController 제공"""
    return TaskController(
        create_use_case=CreateTaskUseCase(
            task_repository=mock_task_repository,
            project_repository=Mock(spec=ProjectRepository),
            notification_service=mock_notification_port,
        ),
        presenter=Mock(spec=TaskPresenter),
    )


# 클라이언트에서 전달되는 형태의 원시(raw) JSON 데이터
@pytest.fixture
def task_request_json():
    """클라이언트에서 전송되는 형태의 샘플 요청 데이터 제공"""
    return {"title": "Test Task", "description": "Testing task creation", "priority": "HIGH"}


# 전체 흐름 테스트: 컨트롤러 -> 유스케이스 -> 저장소까지의 통합 검증
def test_controller_handles_task_creation(task_controller, task_request_json, mock_task_repository):
    """컨트롤러 계층을 통한 작업 생성 테스트"""
    result = task_controller.handle_create(**task_request_json)

    assert result.is_success
    mock_task_repository.save.assert_called_once()  # 저장소에 1회 저장 확인
