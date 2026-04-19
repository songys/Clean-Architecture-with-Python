# 애그리게이트(Aggregate) 패턴: Project가 Task를 관리하는 예시
from datetime import datetime

from todo_app.domain.entities.project import Project
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Deadline, Priority

# Project 엔티티 생성 - 여러 Task를 관리하는 애그리게이트 루트(Aggregate Root)
project = Project("Website Redesign")

# Task 엔티티 생성 - 각 작업은 고유 ID, 마감일, 우선순위 보유
task1 = Task(
    title="Design homepage",
    description="Create new homepage layout",
    due_date=Deadline(datetime(2023, 12, 31)),
    priority=Priority.HIGH,
)
task2 = Task(
    title="Implement login",
    description="Add user authentication",
    due_date=Deadline(datetime(2023, 11, 30)),
    priority=Priority.MEDIUM,
)

# 애그리게이트 루트를 통한 작업 추가 - 외부에서 직접 _tasks에 접근하지 않고 메서드 사용
project.add_task(task1)
project.add_task(task2)

# 프로젝트 정보 출력 - tasks 프로퍼티로 내부 딕셔너리를 리스트로 변환하여 반환
print(f"프로젝트: {project.name}")
print(f"작업 수: {len(project.tasks)}")
print(f"첫 번째 작업: {project.tasks[0].title}")
