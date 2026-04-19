# todo_app/infrastructure/configuration/container.py

# 클린 아키텍처의 컴포지션 루트(Composition Root) 역할을 하는 애플리케이션 컨테이너
# 모든 계층의 구성 요소를 한곳에서 조립하여 의존성 역전 원칙(DIP)을 실현하는 구조
@dataclass
class Application:
    """모든 구성 요소를 연결하는 컨테이너."""

    # 인프라스트럭처 계층: 데이터 영속성을 위한 리포지토리 (추상 인터페이스 타입)
    task_repository: TaskRepository
    project_repository: ProjectRepository
    # 외부 서비스 포트: 알림 전송을 위한 서비스 인터페이스
    notification_service: NotificationPort
    # 인터페이스 어댑터 계층: CLI/웹 등 인터페이스별 출력 포맷 담당 프레젠터
    task_presenter: TaskPresenter
    project_presenter: ProjectPresenter
