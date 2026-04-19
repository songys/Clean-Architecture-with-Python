"""
모든 구성 요소를 설정하고 연결하는 애플리케이션 컨테이너.
- 컴포지션 루트: 유스 케이스, 컨트롤러, 리포지토리 등 모든 의존성을 조립
- 의존성 주입(DI)을 통해 계층 간 느슨한 결합 유지
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


import logging

logger = logging.getLogger(__name__)


def create_application(
    notification_service: NotificationPort,
    task_presenter: TaskPresenter,
    project_presenter: ProjectPresenter,
    app_context: str,
) -> "Application":
    """
    Application 컨테이너의 팩토리 함수.
    필요한 모든 의존성으로 애플리케이션 컨테이너를 생성하고 구성한다.

    Args:
        notification_service: 알림 전송 서비스
        task_presenter: 작업 관련 출력 프레젠터
        project_presenter: 프로젝트 관련 출력 프레젠터

    Returns:
        구성된 Application 인스턴스
    """
    task_repository, project_repository = create_repositories()

    # 자동 폴백으로 알림 서비스 생성
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
    """모든 구성 요소를 연결하는 애플리케이션 컨테이너.
    - 리포지토리, 알림 서비스, 프레젠터를 주입받아 유스 케이스와 컨트롤러 조립
    - CLI, 웹 등 다양한 인터페이스에서 동일한 핵심 로직 재사용 가능
    """

    task_repository: TaskRepository
    project_repository: ProjectRepository
    notification_service: NotificationPort
    task_presenter: TaskPresenter
    project_presenter: ProjectPresenter

    def __post_init__(self):
        """유스 케이스와 컨트롤러를 연결한다.
        - 의존성 주입: 외부에서 제공된 리포지토리/서비스를 유스 케이스에 전달
        """

        # 작업 유스 케이스 구성
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

        # 작업 컨트롤러 연결
        self.task_controller = TaskController(
            create_use_case=self.create_task_use_case,
            complete_use_case=self.complete_task_use_case,
            update_use_case=self.update_task_use_case,
            delete_use_case=self.delete_task_use_case,
            get_use_case=self.get_task_use_case,
            presenter=self.task_presenter,
        )

        # 프로젝트 컨트롤러 연결
        self.project_controller = ProjectController(
            create_use_case=self.create_project_use_case,
            complete_use_case=self.complete_project_use_case,
            get_use_case=self.get_project_use_case,
            list_use_case=self.list_projects_use_case,
            update_use_case=self.update_project_use_case,
            presenter=self.project_presenter,
        )
