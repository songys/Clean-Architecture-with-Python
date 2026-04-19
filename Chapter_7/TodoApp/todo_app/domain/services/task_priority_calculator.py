# 도메인 서비스 — 마감일 기반 작업 우선순위 자동 계산
from datetime import timedelta

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Priority


class TaskPriorityCalculator:
    """마감일에 따른 작업 우선순위 계산 도메인 서비스."""

    @staticmethod
    def calculate_priority(task: Task) -> Priority:
        """
        마감일 임박 정도에 따라 작업 우선순위를 자동 결정.

        규칙:
        - 마감일 없음: 기존 우선순위 유지
        - 기한 초과 또는 12시간 이내: HIGH
        - 2일 이내: MEDIUM
        - 그 외: LOW
        """
        # 마감일이 없으면 조정 불필요 — 기존 우선순위 반환
        if task.due_date is None:
            return task.priority
        # 기한 초과 또는 12시간 이내이면 높음
        if task.is_overdue() or task.due_date.time_remaining() <= timedelta(
            hours=12
        ):
            return Priority.HIGH
        # 2일 이내이면 중간
        elif task.due_date and task.due_date.time_remaining() <= timedelta(
            days=2
        ):
            return Priority.MEDIUM
        # 2일 이상 남으면 낮음
        else:
            return Priority.LOW
