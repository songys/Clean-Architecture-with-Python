from datetime import timedelta

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority


# 마감일 기반 작업 우선순위 자동 계산을 담당하는 도메인 서비스
# - 엔터티에 속하지 않는 도메인 로직을 별도 서비스로 분리
class TaskPriorityCalculator:
    # 마감일까지 남은 시간에 따라 우선순위를 자동 산출하는 정적 메서드
    @staticmethod
    def calculate_priority(task: Task) -> Priority:
        """
        다가오는 마감일을 기반으로 작업 우선순위를 계산한다.

        """
        # 마감일이 없으면 조정 불필요
        if task.due_date is None:
            return task.priority
        # 기한 초과이거나 12시간 이내이면 높음
        if task.is_overdue() or task.due_date.time_remaining() <= timedelta(
            hours=12
        ):
            return Priority.HIGH
        # 2일 이내이면 보통
        elif task.due_date and task.due_date.time_remaining() <= timedelta(
            days=2
        ):
            return Priority.MEDIUM
        else:
            return Priority.LOW
