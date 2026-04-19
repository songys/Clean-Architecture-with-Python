"""
모든 구성 요소를 설정하고 연결하는 애플리케이션 컨테이너.

인프라스트럭처 계층의 컴포지션 루트 역할:
- 팩토리 함수(create_application)로 모든 의존성을 조립
- Application 데이터클래스로 유스 케이스와 컨트롤러를 자동 연결
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


def create_application(
    notification_service: NotificationPort,
    task_presenter: TaskPresenter,
    project_presenter: ProjectPresenter,
) -> "Application":
    """
    Application 컨테이너를 위한 팩토리 함수 — 모든 의존성 조립 담당.
    필요한 모든 의존성으로 애플리케이션 컨테이너를 생성하고 구성한다.

    Args:
        notification_service: 알림 전송을 위한 서비스
        task_presenter: 작업 관련 출력을 위한 프레젠터
        project_presenter: 프로젝트 관련 출력을 위한 프레젠터

    Returns:
        구성된 Application 인스턴스
    """
    # 구성(Config)에 따라 적절한 리포지토리 구현체 생성
    task_repository, project_repository = create_repositories()

    # 자동 폴백으로 알림 서비스 생성 — SendGrid 미설정 시 Recorder 사용
    notification_service = create_notification_service()

    return Application(
        task_repository=task_repository,
        project_repository=project_repository,
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
    )


@dataclass
class Application:
    """모든 구성 요소를 연결하는 의존성 주입(DI) 컨테이너."""

    # 외부에서 주입받는 핵심 의존성 (포트/인터페이스 타입으로 선언)
    task_repository: TaskRepository
    project_repository: ProjectRepository
    notification_service: NotificationPort
    task_presenter: TaskPresenter
    project_presenter: ProjectPresenter

    def __post_init__(self):
        """유스 케이스와 컨트롤러의 자동 조립 — dataclass 초기화 후 실행."""

        # --- 작업 유스 케이스 구성 ---
        self.create_task_use_case = CreateTaskUseCase(self.task_repository, self.project_repository)

        self.complete_task_use_case = CompleteTaskUseCase(
            self.task_repository, self.notification_service
        )

        self.get_task_use_case = GetTaskUseCase(self.task_repository)

        # --- 프로젝트 유스 케이스 구성 ---
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

        # --- 작업 컨트롤러 연결 — 유스 케이스와 프레젠터를 주입 ---
        self.task_controller = TaskController(
            create_use_case=self.create_task_use_case,
            complete_use_case=self.complete_task_use_case,
            update_use_case=self.update_task_use_case,
            delete_use_case=self.delete_task_use_case,
            get_use_case=self.get_task_use_case,
            presenter=self.task_presenter,
        )

        # --- 프로젝트 컨트롤러 연결 ---
        self.project_controller = ProjectController(
            create_use_case=self.create_project_use_case,
            complete_use_case=self.complete_project_use_case,
            get_use_case=self.get_project_use_case,
            list_use_case=self.list_projects_use_case,
            update_use_case=self.update_project_use_case,
            presenter=self.project_presenter,
        )
