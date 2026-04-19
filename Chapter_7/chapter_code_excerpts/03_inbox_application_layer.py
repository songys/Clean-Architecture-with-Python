# === 애플리케이션 계층: Inbox 패턴을 반영한 리포지토리 인터페이스 및 유스 케이스 ===

# 2. 애플리케이션 계층: 리포지토리 인터페이스와 유스 케이스 업데이트

# 프로젝트 리포지토리 포트(인터페이스) — INBOX 조회 기능 추가
class ProjectRepository(ABC):
    @abstractmethod
    def get_inbox(self) -> Project:
        """INBOX 프로젝트 조회 — 할당되지 않은 작업을 위한 기본 프로젝트 반환"""
        pass

# 작업 생성 유스 케이스 — Inbox 자동 할당 로직 포함
@dataclass
class CreateTaskUseCase:
    task_repository: TaskRepository
    project_repository: ProjectRepository  # Inbox 조회를 위해 프로젝트 리포지토리도 의존

    def execute(self, request: CreateTaskRequest) -> Result:
        try:
            params = request.to_execution_params()
            project_id = params.get("project_id")
            if not project_id:
                # 프로젝트가 지정되지 않으면 INBOX에 자동 할당
                project_id = self.project_repository.get_inbox().id
            # ... 나머지 구현