# 새 작업 생성 - Task 엔티티의 기본 사용법 예시
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority

# Task 엔티티 생성: 제목, 설명, 우선순위를 지정하여 새 작업 인스턴스 생성
# 고유 ID(UUID)는 Entity 기본 클래스에서 자동 부여
task = Task(
    title="Complete project proposal",
    description="Draft and review the proposal for the new client project",
    priority=Priority.HIGH,  # 값 객체(Value Object)인 Priority 열거형으로 우선순위 지정
)

# 작업 속성 확인 - status는 생성 시 기본값 TaskStatus.TODO로 자동 설정
print(task.title)  # "Complete project proposal"
print(task.priority)  # Priority.HIGH
print(task.status)  # TaskStatus.TODO
