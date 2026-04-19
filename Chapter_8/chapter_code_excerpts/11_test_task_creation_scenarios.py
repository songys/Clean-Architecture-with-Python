from uuid import UUID
import pytest
from unittest.mock import Mock


# pytest.mark.parametrize: 하나의 테스트 함수로 여러 입력 시나리오를 검증
# 각 파라미터 조합마다 독립적인 테스트가 실행되어 다양한 경우를 효율적으로 커버
@pytest.mark.parametrize(
    "request_data,expected_behavior",
    [
        # 시나리오 1: 기본 작업 생성 - 프로젝트 미지정 시 INBOX에 자동 할당
        (
            {"title": "Test Task", "description": "Basic creation"},
            {"project_type": ProjectType.INBOX, "priority": Priority.MEDIUM}
        ),
        # 시나리오 2: 명시적 프로젝트 할당
        (
            {
                "title": "Project Task",
                "description": "With project",
                "project_id": "project-uuid"
            },
            {"project_type": ProjectType.REGULAR, "priority": Priority.MEDIUM}
        ),
        # 시나리오 3: 높은 우선순위 작업
        # ... 작업 데이터
    ],
    ids=["basic-task", "project-task", "priority-task"]  # 각 시나리오의 식별 이름
)
def test_task_creation_scenarios(request_data, expected_behavior):
    """작업 생성 유스 케이스가 다양한 입력 시나리오를 올바르게 처리하는지 테스트한다."""
    # 준비 - Mock 작업 저장소 + 실제 프로젝트 저장소(INBOX 필요) 혼합 전략
    task_repo = Mock(spec=TaskRepository)
    project_repo = FileProjectRepository(tmp_path)  # INBOX를 위한 실제 프로젝트 리포지토리

    use_case = CreateTaskUseCase(
        task_repository=task_repo,
        project_repository=project_repo
    )

    # 실행
    result = use_case.execute(CreateTaskRequest(**request_data))

    # 검증 - 시나리오별 기대 동작 확인
    assert result.is_success
    created_task = result.value
    if expected_behavior["project_type"] == ProjectType.INBOX:
        assert UUID(created_task.project_id) == project_repo.get_inbox().id
    assert created_task.priority == expected_behavior["priority"]

