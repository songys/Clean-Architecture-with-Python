from typing import Dict, Optional, Sequence
from uuid import UUID
from logging import getLogger

from todo_app.domain.entities.project import Project
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import TaskStatus, ProjectType
from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.domain.exceptions import InboxNotFoundError, ProjectNotFoundError, TaskNotFoundError

logger = getLogger(__name__)


# 메모리 기반 TaskRepository 구현체 - 딕셔너리로 데이터 저장
# 테스트 및 개발 환경에서 사용, 애플리케이션 종료 시 데이터 소멸
class InMemoryTaskRepository(TaskRepository):
    """TaskRepository의 인메모리 구현."""

    def __init__(self) -> None:
        self._tasks: Dict[UUID, Task] = {}

    def get(self, task_id: UUID) -> Task:
        """
        ID로 작업을 조회한다.

        Args:
            task_id: 작업의 고유 식별자

        Returns:
            요청된 작업

        Raises:
            TaskNotFoundError: 해당 ID의 작업이 존재하지 않는 경우
        """
        if task := self._tasks.get(task_id):
            return task
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        """
        작업을 저장한다.

        Args:
            task: 저장할 작업
        """
        logger.debug(f"Saving task {task.id} for project {task.project_id}")
        self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:
        """
        작업을 삭제한다.

        Args:
            task_id: 삭제할 작업의 고유 식별자
        """
        self._tasks.pop(task_id, None)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        """
        프로젝트에 속한 모든 작업을 찾는다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            프로젝트에 속한 작업 시퀀스
        """
        return [task for task in self._tasks.values() if task.project_id == project_id]

    def get_active_tasks(self) -> Sequence[Task]:
        """
        완료되지 않은 모든 작업을 가져온다.

        Returns:
            모든 활성 작업의 시퀀스
        """
        return [task for task in self._tasks.values() if task.status != TaskStatus.DONE]


# 메모리 기반 ProjectRepository 구현체
# 초기화 시 INBOX 프로젝트를 자동 생성하는 인프라 책임 포함
class InMemoryProjectRepository(ProjectRepository):
    """ProjectRepository의 인메모리 구현."""

    def __init__(self) -> None:
        self._projects: Dict[UUID, Project] = {}
        self._task_repo: Optional[TaskRepository] = None
        self._initialize_inbox()

    def _initialize_inbox(self) -> None:
        """
        INBOX 프로젝트가 존재하지 않으면 초기화한다.
        핵심은 INBOX의 존재는 인프라스트럭처가 보장하지만,
        그 동작과 규칙은 도메인 계층에 남아 있다는 것이다.
        """
        inbox = self._fetch_inbox()
        if not inbox:
            inbox = Project.create_inbox()
            self.save(inbox)

    def _fetch_inbox(self) -> Optional[Project]:
        """
        리포지토리에서 INBOX 프로젝트를 찾는다.

        Returns:
            INBOX 프로젝트가 존재하면 반환, 그렇지 않으면 None
        """
        return next(
            (p for p in self._projects.values() if p.project_type == ProjectType.INBOX), None
        )

    def set_task_repository(self, task_repo: TaskRepository) -> None:
        """
        작업 리포지토리 참조를 설정한다.

        Args:
            task_repo: 작업 리포지토리 인스턴스
        """
        self._task_repo = task_repo

    def _load_project_tasks(self, project: Project) -> None:
        """
        프로젝트의 작업을 로드한다.

        Args:
            project: 작업을 로드할 프로젝트
        """
        if not self._task_repo:
            return

        project._tasks.clear()
        for task in self._task_repo.find_by_project(project.id):
            project._tasks[task.id] = task

    def get(self, project_id: UUID) -> Project:
        """
        ID로 프로젝트를 조회한다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            요청된 프로젝트

        Raises:
            ProjectNotFoundError: 해당 ID의 프로젝트가 존재하지 않는 경우
        """
        if project := self._projects.get(project_id):
            self._load_project_tasks(project)
            return project
        raise ProjectNotFoundError(project_id)

    def get_all(self) -> list[Project]:
        """
        모든 프로젝트를 조회한다.

        Returns:
            작업이 로드된 모든 프로젝트의 리스트
        """
        projects = list(self._projects.values())
        for project in projects:
            self._load_project_tasks(project)
        return projects

    def save(self, project: Project) -> None:
        """
        프로젝트를 저장한다.

        Args:
            project: 저장할 프로젝트
        """
        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:
        """
        프로젝트를 삭제한다.

        Args:
            project_id: 삭제할 프로젝트의 고유 식별자
        """
        self._projects.pop(project_id, None)

    def get_inbox(self) -> Project:
        """
        INBOX 프로젝트를 가져온다.

        Returns:
            INBOX 프로젝트

        Raises:
            InboxNotFoundError: INBOX 프로젝트가 존재하지 않는 경우
        """
        inbox = self._fetch_inbox()
        if not inbox:
            raise InboxNotFoundError("Inbox 프로젝트를 찾을 수 없습니다")
        return inbox
