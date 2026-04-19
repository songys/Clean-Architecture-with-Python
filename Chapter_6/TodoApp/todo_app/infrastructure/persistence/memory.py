"""
인터페이스 어댑터 패턴을 설명하기 위한 인메모리 리포지토리 구현.

프레임워크 및 드라이버 계층의 사전 미리보기이다.

이 모듈은 실제 데이터베이스의 복잡성 없이 클린 아키텍처 원칙을
보여주기 위한 리포지토리 인터페이스의 기본 인메모리 구현을 제공한다.
다음을 보여준다:
- 애플리케이션 계층의 리포지토리 인터페이스가 어떻게 구현되는지
- 영속성 관심사가 비즈니스 로직과 어떻게 분리되는지
- 저장소 경계에서의 기본 오류 처리

이 구현은 7장에서 실제 데이터베이스 리포지토리로 대체되며,
클린 아키텍처가 핵심 기능을 유지하면서 저장 메커니즘을 교체하는
방법을 보여준다.
"""

from typing import Dict, Sequence
from uuid import UUID

from todo_app.domain.entities.task import Task
from todo_app.domain.entities.project import Project
from todo_app.domain.exceptions import TaskNotFoundError, ProjectNotFoundError
from todo_app.domain.value_objects import TaskStatus
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.repositories.project_repository import ProjectRepository


# TaskRepository 인터페이스의 인메모리 구현 (어댑터)
# - 딕셔너리를 사용한 간단한 저장소로 클린 아키텍처의 게이트웨이 패턴을 실증
# - 7장에서 실제 데이터베이스(SQLite 등) 구현으로 교체 예정
class InMemoryTaskRepository(TaskRepository):
    """
    인터페이스 어댑터 개념을 설명하기 위한 TaskRepository의 인메모리 구현.

    이 클래스는 클린 아키텍처에서 저장소 게이트웨이가 어떻게 작동하는지 보여준다:
    - 애플리케이션 계층에서 정의한 인터페이스를 구현한다
    - 저장소 세부 사항을 캡슐화한다 (이 경우 인메모리 딕셔너리)
    - 저장소와 비즈니스 로직 간의 분리를 유지한다
    - 저장소 관련 오류를 처리한다

    단순화되어 있지만, 이 구현은 실제 데이터베이스 구현에서
    사용될 패턴을 확립한다.
    """

    def __init__(self):
        self._tasks: Dict[UUID, Task] = {}  # UUID를 키로 하는 작업 저장소

    def get(self, task_id: UUID) -> Task:
        """ID로 작업을 조회하거나 TaskNotFoundError를 발생시킨다."""
        if task := self._tasks.get(task_id):
            return task
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        """작업을 저장하거나 업데이트한다."""
        self._tasks[task.id] = task

    def delete(self, task_id: UUID) -> None:
        """작업이 존재하면 삭제한다."""
        self._tasks.pop(task_id, None)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        """프로젝트에 속한 모든 작업을 조회한다."""
        return [
            task for task in self._tasks.values()
            if task.project_id == project_id
        ]

    def get_active_tasks(self) -> Sequence[Task]:
        """완료되지 않은 모든 작업을 가져온다."""
        return [
            task for task in self._tasks.values()
            if task.status != TaskStatus.DONE
        ]


# ProjectRepository 인터페이스의 인메모리 구현 (어댑터)
class InMemoryProjectRepository(ProjectRepository):
    """
    인터페이스 어댑터 개념을 설명하기 위한 ProjectRepository의 인메모리 구현.

    InMemoryTaskRepository와 유사하게, 이 클래스는 이후 장에서 실제 데이터베이스와
    함께 사용될 게이트웨이 구현 패턴을 보여준다.
    """

    def __init__(self):
        self._projects: Dict[UUID, Project] = {}  # UUID를 키로 하는 프로젝트 저장소

    def get(self, project_id: UUID) -> Project:
        """ID로 프로젝트를 조회하거나 ProjectNotFoundError를 발생시킨다."""
        if project := self._projects.get(project_id):
            return project
        raise ProjectNotFoundError(project_id)

    def save(self, project: Project) -> None:
        """프로젝트를 저장하거나 업데이트한다."""
        self._projects[project.id] = project

    def delete(self, project_id: UUID) -> None:
        """프로젝트가 존재하면 삭제한다."""
        self._projects.pop(project_id, None)