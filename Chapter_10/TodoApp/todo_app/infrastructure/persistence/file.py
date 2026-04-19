"""
JSON 파일 기반 리포지토리 구현 (인프라스트럭처 계층).
- 엔터티를 JSON 파일로 직렬화/역직렬화하여 영속성 제공
- 리포지토리 인터페이스(추상 클래스)를 구현하여 의존성 역전 원칙(DIP) 적용
- 인메모리 리포지토리와 교체 가능 (동일한 인터페이스 구현)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from todo_app.domain.entities.task import Task
from todo_app.domain.entities.project import Project
from todo_app.domain.exceptions import TaskNotFoundError, ProjectNotFoundError, InboxNotFoundError
from todo_app.domain.value_objects import ProjectType, TaskStatus, ProjectStatus, Priority, Deadline
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.application.repositories.project_repository import ProjectRepository


class JsonEncoder(json.JSONEncoder):
    """도메인 객체를 위한 커스텀 JSON 인코더."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, (TaskStatus, ProjectStatus, Priority)):
            return obj.name
        return super().default(obj)


class FileTaskRepository(TaskRepository):
    """TaskRepository의 JSON 파일 기반 구현."""

    def __init__(self, data_dir: Path):
        self.tasks_file = data_dir / "tasks.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """작업 파일이 존재하지 않으면 생성한다."""
        if not self.tasks_file.exists():
            self.tasks_file.write_text("[]")

    def _load_tasks(self) -> list[Dict[str, Any]]:
        """JSON 파일에서 모든 작업을 로드한다."""
        return json.loads(self.tasks_file.read_text())

    def _save_tasks(self, tasks: list[Dict[str, Any]]) -> None:
        """작업을 JSON 파일에 저장한다."""
        self.tasks_file.write_text(json.dumps(tasks, indent=2, cls=JsonEncoder))

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Task 엔터티를 JSON 저장용 딕셔너리로 변환한다."""
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "project_id": task.project_id,
            "due_date": task.due_date.due_date if task.due_date else None,
            "priority": task.priority.name,
            "status": task.status.name,
            "completed_at": task.completed_at,
            "completion_notes": task.completion_notes,
        }

    def _dict_to_task(self, data: Dict[str, Any]) -> Task:
        """딕셔너리를 Task 엔터티로 변환한다."""
        # 필수 속성으로 작업 생성
        task = Task(
            title=data["title"],
            description=data["description"],
            project_id=UUID(data["project_id"]),
            priority=Priority[data["priority"]],
        )

        # 추가 속성 설정
        if data["due_date"]:
            task.due_date = Deadline(datetime.fromisoformat(data["due_date"]))
        task.status = TaskStatus[data["status"]]
        if data["completed_at"]:
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        task.completion_notes = data["completion_notes"]

        # 일관성을 유지하기 위해 ID를 명시적으로 설정
        task.id = UUID(data["id"])

        return task

    def get(self, task_id: UUID) -> Task:
        """ID로 작업을 조회한다."""
        tasks = self._load_tasks()
        for task_data in tasks:
            if UUID(task_data["id"]) == task_id:
                return self._dict_to_task(task_data)
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        """작업을 저장한다."""
        tasks = self._load_tasks()

        # 기존 작업 업데이트 또는 새 작업 추가
        updated = False
        for i, task_data in enumerate(tasks):
            if UUID(task_data["id"]) == task.id:
                tasks[i] = self._task_to_dict(task)
                updated = True
                break

        if not updated:
            tasks.append(self._task_to_dict(task))

        self._save_tasks(tasks)

    def delete(self, task_id: UUID) -> None:
        """작업을 삭제한다."""
        tasks = self._load_tasks()
        tasks = [t for t in tasks if UUID(t["id"]) != task_id]
        self._save_tasks(tasks)

    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        """프로젝트의 모든 작업을 찾는다."""
        tasks = self._load_tasks()
        return [self._dict_to_task(t) for t in tasks if UUID(t["project_id"]) == project_id]

    def get_active_tasks(self) -> Sequence[Task]:
        """완료되지 않은 모든 작업을 가져온다."""
        tasks = self._load_tasks()
        return [self._dict_to_task(t) for t in tasks if t["status"] != TaskStatus.DONE.name]


class FileProjectRepository(ProjectRepository):
    """ProjectRepository의 JSON 파일 기반 구현."""

    def __init__(self, data_dir: Path):
        self.projects_file = data_dir / "projects.json"
        self._ensure_file_exists()
        self._task_repo = None

        """
        INBOX가 존재하지 않으면 초기화한다.
        핵심은 INBOX의 존재는 인프라스트럭처에서 보장하지만,
        그 동작과 규칙은 도메인 계층에 남아 있다는 것이다.
        """
        inbox = self._fetch_inbox()
        if not inbox:
            inbox = Project.create_inbox()
            self.save(inbox)

    def set_task_repository(self, task_repo: TaskRepository) -> None:
        self._task_repo = task_repo

    def _ensure_file_exists(self) -> None:
        """프로젝트 파일이 존재하지 않으면 생성한다."""
        if not self.projects_file.exists():
            self.projects_file.write_text("[]")

    def _load_projects(self) -> list[Dict[str, Any]]:
        """JSON 파일에서 모든 프로젝트를 로드한다."""
        return json.loads(self.projects_file.read_text())

    def _save_projects(self, projects: list[Dict[str, Any]]) -> None:
        """프로젝트를 JSON 파일에 저장한다."""
        self.projects_file.write_text(json.dumps(projects, indent=2, cls=JsonEncoder))

    def _project_to_dict(self, project: Project) -> Dict[str, Any]:
        """Project 엔터티를 JSON 저장용 딕셔너리로 변환한다."""
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "project_type": project.project_type.name,
            "status": project.status.name,
            "completed_at": project.completed_at,
            "completion_notes": project.completion_notes,
        }

    def _dict_to_project(self, data: Dict[str, Any]) -> Project:
        """딕셔너리를 Project 엔터티로 변환한다."""
        # INBOX 프로젝트를 특별히 처리
        if data.get("project_type") == ProjectType.INBOX.name:
            project = Project.create_inbox()
        else:
            project = Project(name=data["name"], description=data["description"])

        # 추가 속성 설정
        project.status = ProjectStatus[data["status"]]
        if data["completed_at"]:
            project.completed_at = datetime.fromisoformat(data["completed_at"])
        project.completion_notes = data["completion_notes"]

        # 일관성을 유지하기 위해 ID를 명시적으로 설정
        project.id = UUID(data["id"])

        return project

    def get(self, project_id: UUID) -> Project:
        """ID로 프로젝트를 조회한다."""
        projects = self._load_projects()
        for project_data in projects:
            if UUID(project_data["id"]) == project_id:
                project = self._dict_to_project(project_data)
                # 작업 리포지토리가 설정된 경우에만 작업 로드
                if self._task_repo:
                    self._load_project_tasks(project)
                return project
        raise ProjectNotFoundError(project_id)

    def get_all(self) -> List[Project]:
        """작업이 로드된 모든 프로젝트를 가져온다."""
        projects = [self._dict_to_project(p) for p in self._load_projects()]
        # 모든 프로젝트가 로드되고 작업 리포지토리가 설정된 후 작업 로드
        if self._task_repo:
            for project in projects:
                self._load_project_tasks(project)
        return projects

    def save(self, project: Project) -> None:
        """프로젝트와 관련 작업을 저장한다."""
        projects = self._load_projects()

        # 기존 프로젝트 업데이트 또는 새 프로젝트 추가
        updated = False
        for i, project_data in enumerate(projects):
            if UUID(project_data["id"]) == project.id:
                projects[i] = self._project_to_dict(project)
                updated = True
                break

        if not updated:
            projects.append(self._project_to_dict(project))

        self._save_projects(projects)

        # 관련 작업 저장
        for task in project.tasks:
            self._task_repo.save(task)

    def delete(self, project_id: UUID) -> None:
        """프로젝트와 관련 작업을 삭제한다."""
        # 먼저 관련 작업 삭제
        for task in self._task_repo.find_by_project(project_id):
            self._task_repo.delete(task.id)

        # 그 후 프로젝트 삭제
        projects = self._load_projects()
        projects = [p for p in projects if UUID(p["id"]) != project_id]
        self._save_projects(projects)

    def _fetch_inbox(self) -> Optional[Project]:
        """INBOX 프로젝트를 찾는다."""
        projects = self._load_projects()
        for project_data in projects:
            if project_data.get("project_type") == ProjectType.INBOX.name:
                return self._dict_to_project(project_data)
        return None

    def get_inbox(self) -> Project:
        """INBOX 프로젝트를 가져온다."""
        inbox = self._fetch_inbox()
        if not inbox:
            raise InboxNotFoundError("Inbox 프로젝트를 찾을 수 없습니다")
        return inbox

    def _load_project_tasks(self, project: Project) -> None:
        """프로젝트의 작업을 로드한다."""
        try:
            # 기존 작업 초기화
            project._tasks.clear()

            # 작업 리포지토리에서 작업 로드
            tasks = self._task_repo.find_by_project(project.id)

            # 작업을 프로젝트에 연결
            for task in tasks:
                project._tasks[task.id] = task
        except Exception as e:
            # 오류를 기록하되 충돌하지 않음 - 빈 작업 목록이 프로젝트 없음보다 나음
            print(f"프로젝트 {project.id}의 작업 로드 중 오류: {str(e)}")
