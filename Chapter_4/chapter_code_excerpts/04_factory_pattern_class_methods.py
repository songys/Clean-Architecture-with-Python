# 팩토리 패턴 - 클래스 메서드(@classmethod)를 활용한 엔티티 생성
from dataclasses import dataclass

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import Priority, Deadline


@dataclass
class Task(Entity):
    # ... 기존 속성들 ...

    # 클래스 메서드 팩토리: 긴급 작업 전용 생성 메서드
    # 우선순위를 항상 HIGH로 설정하여 반복적인 코드 제거
    @classmethod
    def create_urgent_task(cls, title: str, description: str, due_date: Deadline):
        return cls(title, description, due_date, Priority.HIGH)
