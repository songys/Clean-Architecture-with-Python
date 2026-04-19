# 값 객체(Value Object) 사용의 중요성 비교: 문자열 vs 열거형(Enum)
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import TaskStatus

# --- 안티 패턴: 문자열 직접 사용 (타입 안전성 부재) ---
task = Task("Complete project", "The important project")
task.status = "Finished"  # 허용되지만 유효하지 않음 - 어떤 문자열이든 할당 가능
print(task.status == "done")  # False, 대소문자 구분 문제 발생

# --- 권장 패턴: TaskStatus 열거형 사용 (타입 안전성 보장) ---
task = Task("Complete project", "The important project")
task.status = TaskStatus.DONE  # 타입 안전 - 정해진 값만 사용 가능
print(task.status == TaskStatus.DONE)  # True, 대소문자 문제 없음
