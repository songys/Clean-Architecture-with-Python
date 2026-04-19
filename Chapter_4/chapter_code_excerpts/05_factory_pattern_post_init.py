# 팩토리 패턴 - __post_init__을 활용한 엔티티 생성 시 유효성 검증
from dataclasses import dataclass

from todo_app.domain.entities.entity import Entity


@dataclass
class Task(Entity):
    # ... 기존 속성들 ...

    # __post_init__: dataclass 생성자 호출 직후 자동 실행되는 검증 메서드
    # 엔티티의 불변 조건(invariant)을 보장하는 역할
    def __post_init__(self):
        # 비즈니스 규칙: 작업 제목은 반드시 존재해야 함
        if not self.title.strip():
            raise ValueError("비어 있는 작업 제목 사용 불가능")
        # 비즈니스 규칙: 작업 설명의 최대 길이 제한
        if len(self.description) > 500:
            raise ValueError(
                "작업 설명 500자 초과 불가")
