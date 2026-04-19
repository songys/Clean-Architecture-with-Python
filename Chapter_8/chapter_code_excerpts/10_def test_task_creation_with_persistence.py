from uuid import UUID
from unittest.mock import Mock


# 통합 테스트: 실제 파일 저장소와 유스케이스를 조합한 영속성 검증
# 핵심 관심사(저장)에 실제 구현체 사용, 부수 관심사(알림)에는 Mock 사용하는 혼합 전략
def test_task_creation_with_persistence(tmp_path):
    """실제 저장소를 사용한 작업 생성 유스 케이스 테스트"""
    # 준비 - 실제 파일 저장소 구성
    task_repo = FileTaskRepository(tmp_path)
    project_repo = FileProjectRepository(tmp_path)
    project_repo.set_task_repository(task_repo)

    use_case = CreateTaskUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        notification_service=Mock(),  # 저장과 무관한 부분은 여전히 모의 객체로 대체
    )

    # 실행
    result = use_case.execute(CreateTaskRequest(title="Test Task", description="Integration test"))

    # 검증 - 실제 저장소에서 작업을 다시 읽어 영속성 확인
    assert result.is_success
    created_task = task_repo.get(UUID(result.value.id))
    # 프로젝트 미지정 시 자동으로 INBOX에 할당되는지 확인
    assert created_task.project_id == project_repo.get_inbox().id
