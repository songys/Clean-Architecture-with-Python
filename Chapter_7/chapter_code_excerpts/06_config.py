# === 구성 관리와 팩토리 패턴 ===
# 환경 변수를 통해 리포지토리 유형(메모리/파일)을 선택하는 구성 클래스와
# 적절한 구현체를 생성하는 팩토리 함수

# 환경 변수에서 리포지토리 유형을 읽어오는 구성 클래스
class Config:
    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """환경 변수 TODO_REPOSITORY_TYPE에서 리포지토리 유형 조회"""
        repo_type_str = os.getenv("TODO_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"잘못된 리포지토리 타입: {repo_type_str}")


# 구성에 따라 적절한 리포지토리 구현체를 생성하는 팩토리 함수
def create_repositories() -> Tuple[TaskRepository, ProjectRepository]:
    """리포지토리 팩토리 — Config 설정에 따라 FILE 또는 MEMORY 구현체 반환"""
    repo_type = Config.get_repository_type()
    if repo_type == RepositoryType.FILE:
        # 파일 기반 영속성 — JSON 파일에 데이터 저장
        data_dir = Config.get_data_directory()
        task_repo = FileTaskRepository(data_dir)
        project_repo = FileProjectRepository(data_dir)
        # 프로젝트 리포지토리에 작업 리포지토리 참조 설정 (작업 로딩용)
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    elif repo_type == RepositoryType.MEMORY:
        # 인메모리 저장소 — 빠르고 가벼운 개발/테스트 환경용
        task_repo = InMemoryTaskRepository()
        project_repo = InMemoryProjectRepository()
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    else:
        raise ValueError(f"잘못된 리포지토리 타입: {repo_type}")
