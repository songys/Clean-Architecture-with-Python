# === 애플리케이션 부트스트래핑 (컴포지션 루트) ===
# 모든 구성 요소를 인스턴스화하고 조립하는 유일한 장소
# 의존성 주입을 통해 각 계층의 구현체를 연결

# --- DI 컨테이너: 의존성 관계를 정의하는 Application 클래스 ---
@dataclass
class Application:
    """모든 구성 요소를 연결하는 의존성 주입 컨테이너"""

    # 외부에서 주입받는 핵심 의존성 (리포지토리, 알림, 프레젠터)
    task_repository: TaskRepository
    project_repository: ProjectRepository
    notification_service: NotificationPort
    task_presenter: TaskPresenter
    project_presenter: ProjectPresenter

    def __post_init__(self):
        """유스 케이스와 컨트롤러의 자동 조립 — dataclass 초기화 후 실행"""
        # 작업 유스 케이스 구성 — 각각 필요한 의존성만 주입
        self.create_task_use_case = CreateTaskUseCase(self.task_repository, self.project_repository)
        self.complete_task_use_case = CompleteTaskUseCase(
            self.task_repository, self.notification_service
        )
        self.get_task_use_case = GetTaskUseCase(self.task_repository)
        self.delete_task_use_case = DeleteTaskUseCase(self.task_repository)
        self.update_task_use_case = UpdateTaskUseCase(
            self.task_repository, self.notification_service
        )
        # 작업 컨트롤러 연결 — 유스 케이스와 프레젠터를 주입
        self.task_controller = TaskController(
            create_use_case=self.create_task_use_case,
            complete_use_case=self.complete_task_use_case,
            update_use_case=self.update_task_use_case,
            delete_use_case=self.delete_task_use_case,
            get_use_case=self.get_task_use_case,
            presenter=self.task_presenter,
        )
        # ... 프로젝트 유스 케이스와 컨트롤러 생성


# --- 팩토리 함수: Application 인스턴스를 구성하여 생성 ---
# Application 클래스는 구성 요소 간 관계의 구조를 정의하지만,
# Application 컨테이너 클래스에 주입할 인스턴스를 적절히 구성해
# 생성하는 방법이 여전히 필요하다. 이는 create_application 팩토리 메서드에서 처리된다:


def create_application(
    notification_service: NotificationPort,
    task_presenter: TaskPresenter,
    project_presenter: ProjectPresenter,
) -> "Application":
    """Application 컨테이너를 위한 팩토리 함수 — 모든 의존성 조립"""
    # 구성(Config)에 따라 적절한 리포지토리 구현체 생성
    task_repository, project_repository = create_repositories()
    # 알림 서비스 팩토리 — SendGrid 또는 Recorder 자동 선택
    notification_service = create_notification_service()
    return Application(
        task_repository=task_repository,
        project_repository=project_repository,
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
    )


# --- 컴포지션 루트: main.py 진입점 ---
# 마지막으로, main.py 스크립트는 컴포지션 루트의 최상위 역할을 하며,
# 애플리케이션 시작 시 모든 구성 요소가 인스턴스화되고 연결되는 유일한 장소다:
def main() -> int:
    """CLI 애플리케이션의 메인 진입점 — 컴포지션 루트"""
    try:
        # 구체적 구현체를 선택하여 애플리케이션 생성
        app = create_application(
            notification_service=NotificationRecorder(),  # 개발용: 알림 기록기
            task_presenter=CliTaskPresenter(),             # CLI용 작업 프레젠터
            project_presenter=CliProjectPresenter(),       # CLI용 프로젝트 프레젠터
        )

        # CLI 프레임워크 어댑터 생성 및 실행
        cli = ClickCli(app)
        return cli.run()

    except KeyboardInterrupt:
        print("\n안녕히 가세요!")
        return 0
    except Exception as e:
        print(f"오류: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
