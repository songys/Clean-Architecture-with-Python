# 통합 테스트: INBOX 프로젝트의 자동 생성 및 영속성 검증
# INBOX는 할당되지 않은 작업을 위한 기본 프로젝트로,
# 인프라 계층에서 존재를 보장하고 도메인 계층에서 규칙을 관리하는 구조
def test_repository_automatically_creates_inbox(tmp_path):
    """프로젝트 리포지토리가 인스턴스 생성 간에 inbox 프로젝트를 유지하는지 테스트"""
    # 준비 - 초기 리포지토리를 생성하고 Inbox 존재 여부 확인
    initial_repo = FileProjectRepository(tmp_path)
    initial_inbox = initial_repo.get_inbox()
    assert initial_inbox.name == "INBOX"
    assert initial_inbox.project_type == ProjectType.INBOX

    # 실행 - 동일한 디렉토리를 가리키는 새 리포지토리 인스턴스 생성
    new_repo = FileProjectRepository(tmp_path)

    # 검증 - 새 인스턴스가 기존 Inbox를 그대로 유지하는지 확인 (중복 생성 방지)
    persisted_inbox = new_repo.get_inbox()
    assert persisted_inbox.id == initial_inbox.id  # 동일한 ID 유지
    assert persisted_inbox.project_type == ProjectType.INBOX
