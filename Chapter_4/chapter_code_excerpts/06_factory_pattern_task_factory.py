# 독립 팩토리 클래스: 복잡한 엔티티 생성 로직의 캡슐화
from uuid import UUID

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority


# TaskFactory: 외부 서비스(user_service, project_repository)와 협력하여
# 컨텍스트에 맞는 Task 엔티티를 생성하는 팩토리 클래스
class TaskFactory:
    def __init__(self, user_service, project_repository):
        self.user_service = user_service  # 사용자 정보 조회 서비스
        self.project_repository = project_repository  # 프로젝트 저장소

    # 프로젝트 내 작업 생성 메서드
    # 단순 생성자 호출이 아닌, 비즈니스 규칙에 따른 복잡한 생성 로직 포함
    def create_task_in_project(
        self, title: str, description: str, project_id: UUID, assignee_id: UUID
    ):
        # 저장소/서비스를 통해 관련 엔티티 조회
        project = self.project_repository.get_by_id(project_id)
        assignee = self.user_service.get_user(assignee_id)

        # 기본 Task 엔티티 생성 후 연관 관계 설정
        task = Task(title, description)
        task.project = project
        task.assignee = assignee

        # 비즈니스 규칙: 고우선순위 프로젝트의 매니저 담당 작업은 자동으로 HIGH 설정
        if project.is_high_priority() and assignee.is_manager():
            task.priority = Priority.HIGH

        # 애그리게이트 루트(Project)를 통한 작업 추가
        project.add_task(task)
        return task
