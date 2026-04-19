# todo_app/infrastructure/configuration/container.py

# 컴포지션 루트 패턴을 구현하는 팩토리 함수
# 인터페이스별 구성 요소(프레젠터)는 외부에서 주입받고,
# 핵심 인프라(리포지토리)는 내부에서 생성하여 의존성 역전 원칙 실현
def create_application(
    notification_service: NotificationPort,
    task_presenter: TaskPresenter,
    project_presenter: ProjectPresenter,
) -> "Application":
    """Application 컨테이너를 위한 팩토리 함수."""
    # 리포지토리는 구성(환경 변수)에 따라 메모리/파일 구현체 자동 선택
    task_repository, project_repository = create_repositories()

    # 모든 의존성을 조립하여 완성된 Application 컨테이너 반환
    return Application(
        task_repository=task_repository,
        project_repository=project_repository,
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
    )
