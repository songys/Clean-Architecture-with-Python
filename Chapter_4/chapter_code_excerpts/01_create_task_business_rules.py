# 비즈니스 규칙이 포함된 Task 엔티티의 상태 전이 예시
from datetime import datetime, timedelta

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Deadline, Priority

# 작업 생성 - 마감일(Deadline) 값 객체와 우선순위를 포함한 Task 엔티티 생성
task = Task(
    title="Complete project proposal",
    description="Draft and review the proposal for the new client project",
    due_date=Deadline(datetime.now() + timedelta(days=7)),  # 7일 후 마감
    priority=Priority.HIGH,
)

# 작업 시작 - TODO → IN_PROGRESS 상태 전이
# 비즈니스 규칙: TODO 상태에서만 시작 가능
task.start()
print(task.status)  # TaskStatus.IN_PROGRESS

# 작업 완료 - IN_PROGRESS → DONE 상태 전이
# 비즈니스 규칙: 이미 완료된 작업은 다시 완료 불가
task.complete()
print(task.status)  # TaskStatus.DONE

# 완료된 작업을 다시 시작하려고 시도 - 비즈니스 규칙 위반 시 예외 발생
try:
    task.start()  # ValueError가 발생함
except ValueError as e:
    print(str(e))  # "'TODO' 상태인 작업만 시작 가능"

# 작업이 기한을 넘겼는지 확인 - Deadline 값 객체의 도메인 로직 활용
print(task.is_overdue())  # False
