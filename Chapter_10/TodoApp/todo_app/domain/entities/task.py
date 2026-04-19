# 도메인 계층의 Task 엔터티
# - 비즈니스 규칙(상태 전이, 완료 처리)을 엔터티 내부에 캡슐화
# - 표준 logging 모듈만 사용하여 프레임워크 독립적 로깅 구현
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import (
    Deadline,
    Priority,
    TaskStatus,
)

import logging

# 모듈 단위 로거 생성 (로거 이름은 모듈 경로를 자동 반영)
logger = logging.getLogger(__name__)


@dataclass
class Task(Entity):
    """완료해야 할 작업.
    - Entity를 상속하여 고유 ID와 동일성 비교 기능 보유
    - 상태 전이 규칙을 도메인 로직으로 강제
    """

    title: str
    description: str
    project_id: UUID  # 소속 프로젝트 참조 (ID만 보관하여 느슨한 연결 유지)
    due_date: Optional[Deadline] = None  # 값 객체로 마감일 관리
    priority: Priority = Priority.MEDIUM  # 열거형 값 객체
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)  # 생성 시 항상 TODO
    completed_at: Optional[datetime] = field(default=None, init=False)
    completion_notes: Optional[str] = field(default=None, init=False)

    def start(self) -> None:
        """작업을 진행 중으로 표시한다."""
        if self.status != TaskStatus.TODO:
            logger.error(
                "Attempted to start task with invalid status",
                extra={
                    "context": {
                        "task_id": str(self.id),
                        "task_title": self.title,
                        "current_status": self.status.name,
                    }
                },
            )
            raise ValueError("'TODO' 상태의 작업만 시작할 수 있습니다")
            
        logger.info(
            "Starting task",
            extra={
                "context": {
                    "task_id": str(self.id),
                    "task_title": self.title,
                    "project_id": str(self.project_id),
                }
            },
        )
        self.status = TaskStatus.IN_PROGRESS

    def complete(self, notes: Optional[str] = None) -> None:
        """
        작업을 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모

        Raises:
            ValueError: 작업이 이미 완료된 경우
        """
        if self.status == TaskStatus.DONE:
            logger.error(
                "Attempted to complete already completed task",
                extra={
                    "context": {
                        "task_id": str(self.id),
                        "task_title": self.title,
                        "completed_at": str(self.completed_at),
                    }
                },
            )
            raise ValueError("작업이 이미 완료되었습니다")
            
        logger.info(
            "Completing task",
            extra={
                "context": {
                    "task_id": str(self.id),
                    "task_title": self.title,
                    "project_id": str(self.project_id),
                    "previous_status": self.status.name,
                }
            },
        )
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.completion_notes = notes

    def is_overdue(self) -> bool:
        """작업이 기한이 지났는지 확인한다."""
        is_overdue = self.due_date is not None and self.due_date.is_overdue()
        if is_overdue:
            logger.warning(
                "Task is overdue",
                extra={
                    "context": {
                        "task_id": str(self.id),
                        "task_title": self.title,
                        "due_date": str(self.due_date),
                        "days_overdue": self.due_date.days_overdue(),
                    }
                },
            )
        return is_overdue
