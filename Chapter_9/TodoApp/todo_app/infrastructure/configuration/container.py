"""
모든 구성 요소를 구성하고 연결하는 애플리케이션 컨테이너.
클린 아키텍처의 컴포지션 루트(Composition Root) 패턴 구현 -
모든 계층의 구성 요소를 한곳에서 조립하는 단일 지점
"""

from dataclasses import dataclass

from todo_app.infrastructure.notifications.factory import create_notification_service
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.interfaces.presenters.base import ProjectPresenter, TaskPresenter
from todo_app.application.use_cases.project_use_cases import (
    CompleteProjectUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
)
from todo_app.application.use_cases.task_use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    DeleteTaskUseCase,
    GetTaskUseCase,
    UpdateTaskUseCase,
)
from todo_app.interfaces.controllers.project_controller import ProjectController
from todo_app.interfaces.controllers.task_controller import TaskController
from todo_app.infrastructure.repository_factory import create_repositories


# 컴포지션 루트 패턴 - 인터페이스별 구성 요소(프레젠터)는 외부에서 주입,
# 핵심 인프라(리포지토리)는 내부에서 생성하여 의존성 역전 원칙 실현
def create_application(
    notification_service: NotificationPort,
    task_presenter: TaskPresenter,
    project_presenter: ProjectPresenter,
) -> "Application":
    """
    Application 컨테이너를 위한 팩토리 함수.
    필요한 모든 의존성과 함께 애플리케이션 컨테이너를 생성하고 구성한다.

    Args:
        notification_service: 알림 전송을 위한 서비스
        task_presenter: 작업 관련 출력을 위한 프레젠터
        project_presenter: 프로젝트 관련 출력을 위한 프레젠터

    Returns:
        구성된 Application 인스턴스
    """
    # 리포지토리는 구성(환경 변수)에 따라 메모리/파일 구현체 자동 선택
    task_repository, project_repository = create_repositories()

    # 자동 폴백으로 알림 서비스 생성 (SendGrid 미설정 시 Recorder로 대체)
    notification_service = create_notification_service()

    return Application(
        task_repository=task_repository,
        project_repository=project_repository,
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
    )


# 애플리케이션의 모든 구성 요소를 조립하는 컨테이너
# 추상 인터페이스 타입으로 의존성을 선언하여 다양한 구현체 교체 가능
@dataclass
class Application:
    """모든 구성 요소를 연결하는 애플리케이션 컨테이너."""

    # 데이터 영속성을 위한 리포지토리 (추상 인터페이스)
    task_repository: TaskRepository
    project_repository: ProjectRepository
    # 외부 알림 서비스 (추상 포트)
    notification_service: NotificationPort
    # 인터페이스별 출력 포맷 담당 프레젠터 (CLI/웹 등 교체 가능)
    task_presenter: TaskPresenter
    project_presenter: ProjectPresenter

    def __post_init__(self):
        """유스 케이스와 컨트롤러를 연결한다."""

        # 작업 유스 케이스 구성 - 각 유스 케이스에 필요한 의존성만 주입
        self.create_task_use_case = CreateTaskUseCase(self.task_repository, self.project_repository)

        self.complete_task_use_case = CompleteTaskUseCase(
            self.task_repository, self.notification_service
        )

        self.get_task_use_case = GetTaskUseCase(self.task_repository)

        # 프로젝트 유스 케이스 구성
        self.create_project_use_case = CreateProjectUseCase(self.project_repository)

        self.complete_project_use_case = CompleteProjectUseCase(
            self.project_repository, self.task_repository, self.notification_service
        )

        self.get_project_use_case = GetProjectUseCase(self.project_repository)

        self.list_projects_use_case = ListProjectsUseCase(self.project_repository)

        self.delete_task_use_case = DeleteTaskUseCase(self.task_repository)
        self.update_task_use_case = UpdateTaskUseCase(
            self.task_repository, self.notification_service
        )

        self.update_project_use_case = UpdateProjectUseCase(self.project_repository)

        # 작업 컨트롤러 - 유스 케이스와 프레젠터를 연결하는 인터페이스 어댑터
        self.task_controller = TaskController(
            create_use_case=self.create_task_use_case,
            complete_use_case=self.complete_task_use_case,
            update_use_case=self.update_task_use_case,
            delete_use_case=self.delete_task_use_case,
            get_use_case=self.get_task_use_case,
            presenter=self.task_presenter,
        )

        # 프로젝트 컨트롤러 - 동일한 패턴으로 프로젝트 관련 유스 케이스 연결
        self.project_controller = ProjectController(
            create_use_case=self.create_project_use_case,
            complete_use_case=self.complete_project_use_case,
            get_use_case=self.get_project_use_case,
            list_use_case=self.list_projects_use_case,
            update_use_case=self.update_project_use_case,
            presenter=self.project_presenter,
        )
