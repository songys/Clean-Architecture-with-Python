# 모든 엔티티의 기본 클래스 - 고유 식별자(UUID)와 동등성 비교 제공
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    # 고유 식별자: 엔티티 생성 시 UUID를 자동 부여
    # init=False로 설정하여 생성자에서 직접 전달하지 않아도 자동 생성
    id: UUID = field(default_factory=uuid4, init=False)

    # 동등성 비교: 속성이 같아도 ID가 다르면 다른 엔티티로 판단
    # 값 객체(Value Object)와 구별되는 엔티티의 핵심 특성
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    # 해시 함수: ID 기반 해싱으로 set, dict 등 해시 컬렉션에서 사용 가능
    def __hash__(self) -> int:
        return hash(self.id)
