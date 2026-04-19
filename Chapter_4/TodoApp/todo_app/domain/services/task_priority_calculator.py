# 도메인 서비스: 마감일 기반 작업 우선순위 자동 계산
# 특정 엔티티에 속하지 않는 상태 없는(stateless) 도메인 로직의 캡슐화
from datetime import timedelta

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority


class TaskPriorityCalculator:
    # 정적 메서드: 인스턴스 상태 없이 순수 로직만 수행 (상태 없는 도메인 서비스의 특성)
    @staticmethod
    def calculate_priority(task: Task) -> Priority:
        # 마감일 초과 작업 → 최고 우선순위(HIGH)
        if task.is_overdue():
            return Priority.HIGH
        # 마감일 2일 이내 작업 → 중간 우선순위(MEDIUM)
        elif task.due_date and task.due_date.time_remaining() <= timedelta(days=2):
            return Priority.MEDIUM
        # 그 외 → 낮은 우선순위(LOW)
        else:
            return Priority.LOW
