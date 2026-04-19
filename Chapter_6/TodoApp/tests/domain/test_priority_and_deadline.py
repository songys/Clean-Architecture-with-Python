# todo_app/tests/domain/test_priority_and_deadline.py
"""작업 우선순위 계산과 마감일 값 객체 테스트"""

from datetime import datetime, timedelta, timezone

import pytest
from freezegun import freeze_time

from todo_app.domain.entities.task import Task
from todo_app.domain.services.task_priority_calculator import (
    TaskPriorityCalculator,
)
from todo_app.domain.value_objects import Deadline, Priority


class TestDeadline:
    def test_create_valid_future_deadline(self):
        """미래 마감일 생성 테스트"""
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        deadline = Deadline(future_date)
        assert deadline.due_date == future_date

    def test_reject_past_deadline(self):
        """과거 마감일 생성 시 오류 발생 테스트"""
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        with pytest.raises(ValueError, match="마감일은 과거일 수 없다"):
            Deadline(past_date)

    @freeze_time("2024-01-01 12:00:00+00:00")  # freeze_time에 UTC 사용
    def test_is_overdue(self):
        """마감일 초과 여부 확인 테스트"""
        # 지금부터 1일 후의 마감일 생성 (고정된 UTC 시간 기준)
        future_date = datetime.now(timezone.utc) + timedelta(days=1)
        deadline = Deadline(future_date)
        assert not deadline.is_overdue()

        # 마감일 이후로 시간 이동 (여전히 UTC)
        with freeze_time("2024-01-03 12:00:00+00:00"):
            assert deadline.is_overdue()

    @freeze_time("2024-01-01 12:00:00+00:00")  # freeze_time에 UTC 사용
    def test_time_remaining(self):
        """마감일까지 남은 시간 계산 테스트"""
        # 지금부터 정확히 2일 후의 마감일 생성 (고정된 UTC 시간 기준)
        due_date = datetime.now(timezone.utc) + timedelta(days=2)
        deadline = Deadline(due_date)

        remaining = deadline.time_remaining()
        # 마이크로초 차이 가능성으로 인해 근사 동등성 확인
        assert abs(remaining - timedelta(days=2)) < timedelta(seconds=1)

        # 마감일 1일 전으로 시간 이동 (여전히 UTC)
        with freeze_time("2024-01-02 12:00:00+00:00"):
            remaining = deadline.time_remaining()
            assert abs(remaining - timedelta(days=1)) < timedelta(seconds=1)

        # 마감일 이후로 시간 이동 (여전히 UTC)
        with freeze_time("2024-01-04 12:00:00+00:00"):
            remaining = deadline.time_remaining()
            assert remaining == timedelta(0)  # 기한 초과 시 0을 반환해야 함

    @freeze_time("2024-01-01 12:00:00+00:00")  # freeze_time에 UTC 사용
    def test_is_approaching(self):
        """마감일 임박 감지 테스트"""
        # 다양한 거리의 마감일 생성 (고정된 UTC 시간 기준)
        base_time = datetime.now(timezone.utc)
        far_date = base_time + timedelta(days=5)
        near_date = base_time + timedelta(hours=12)
        very_near_date = base_time + timedelta(hours=1)

        far_deadline = Deadline(far_date)
        near_deadline = Deadline(near_date)
        very_near_deadline = Deadline(very_near_date)

        # 기본 1일 경고 임계값으로 테스트
        assert not far_deadline.is_approaching()
        assert near_deadline.is_approaching()
        assert very_near_deadline.is_approaching()

        # 사용자 정의 경고 임계값으로 테스트
        custom_threshold = timedelta(hours=2)
        assert not near_deadline.is_approaching(custom_threshold)
        assert very_near_deadline.is_approaching(custom_threshold)


class TestTaskPriorityCalculator:
    @freeze_time("2024-01-01 12:00:00+00:00")  # UTC 사용
    def test_calculate_priority_overdue(self):
        """기한 초과 작업의 우선순위 계산 테스트"""
        # 기한이 초과될 작업 생성
        due_date = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )

        # 마감일 이후로 시간 이동 (여전히 UTC)
        with freeze_time("2024-01-03 12:00:00+00:00"):
            priority = TaskPriorityCalculator.calculate_priority(task)
            assert priority == Priority.HIGH

    @freeze_time("2024-01-01 12:00:00+00:00")  # UTC 사용
    def test_calculate_priority_approaching_deadline(self):
        """마감일이 임박한 작업의 우선순위 계산 테스트"""
        # 2일 후 마감인 작업 생성
        due_date = datetime.now(timezone.utc) + timedelta(days=2)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )

        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == Priority.MEDIUM

    @freeze_time("2024-01-01 12:00:00+00:00")  # UTC 사용
    def test_calculate_priority_far_deadline(self):
        """먼 마감일의 작업 우선순위 계산 테스트"""
        # 5일 후 마감인 작업 생성
        due_date = datetime.now(timezone.utc) + timedelta(days=5)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )

        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == Priority.LOW

    def test_calculate_priority_no_deadline(self):
        """마감일이 없는 작업의 우선순위 계산 테스트"""
        task = Task(title="Test Task", description="Test Description")
        expected_priority = task.priority
        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == expected_priority

    @pytest.mark.parametrize(
        "days_until_due,expected_priority",
        [
            (0.5, Priority.HIGH),  # 마감 12시간 전
            (1, Priority.MEDIUM),  # 마감 1일 전
            (2, Priority.MEDIUM),  # 마감 2일 전
            (3, Priority.LOW),  # 마감 3일 전
            (7, Priority.LOW),  # 마감 1주일 전
        ],
    )
    @freeze_time("2024-01-01 12:00:00+00:00")  # UTC 사용
    def test_priority_thresholds(self, days_until_due, expected_priority):
        """다양한 마감일 임계값과 그에 따른 우선순위 테스트"""
        due_date = datetime.now(timezone.utc) + timedelta(days=days_until_due)
        task = Task(
            title="Test Task",
            description="Test Description",
            due_date=Deadline(due_date),
        )
        priority = TaskPriorityCalculator.calculate_priority(task)
        assert priority == expected_priority
