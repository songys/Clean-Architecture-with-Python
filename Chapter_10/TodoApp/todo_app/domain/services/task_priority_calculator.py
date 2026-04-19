# 도메인 서비스: 마감일 기반 작업 우선순위 자동 계산
# - 특정 엔터티에 속하지 않는 도메인 로직을 서비스로 분리
# - 마감일까지 남은 시간에 따라 우선순위를 동적으로 조정
from datetime import timedelta

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority


class TaskPriorityCalculator:
    @staticmethod
    def calculate_priority(task: Task) -> Priority:
        """
        다가오는 마감일에 따른 작업 우선순위를 고려한다.
        - 마감일 없음: 기존 우선순위 유지
        - 기한 초과 또는 12시간 이내: HIGH
        - 2일 이내: MEDIUM
        - 그 외: LOW
        """
        # 마감일이 없으면 조정 불필요
        if task.due_date is None:
            return task.priority
        # 기한이 지났거나 12시간 이내이면 높음
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
