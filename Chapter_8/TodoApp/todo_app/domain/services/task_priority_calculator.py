from datetime import timedelta

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority


# 도메인 서비스: 특정 엔티티에 속하지 않는 도메인 로직을 담당
# 마감일 기반으로 작업 우선순위를 동적으로 계산하는 서비스
class TaskPriorityCalculator:
    @staticmethod
    def calculate_priority(task: Task) -> Priority:
        """
        임박한 마감일에 기반하여 작업 우선순위를 고려한다

        """
        # 마감일이 없으면 조정 불필요
        if task.due_date is None:
            return task.priority
        # 기한 초과이거나 12시간 이내 마감이면 높음
        if task.is_overdue() or task.due_date.time_remaining() <= timedelta(
            hours=12
        ):
            return Priority.HIGH
        # 2일 이내 마감이면 중간
        elif task.due_date and task.due_date.time_remaining() <= timedelta(
            days=2
        ):
            return Priority.MEDIUM
        else:
            return Priority.LOW
