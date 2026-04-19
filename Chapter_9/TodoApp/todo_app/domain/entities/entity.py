from dataclasses import dataclass, field
from uuid import UUID, uuid4


# 모든 도메인 엔터티의 기본 클래스
# UUID 기반 식별자와 동등성 비교를 제공하는 엔터티 기본 구조
@dataclass
class Entity:
    # 'id' 필드에 대해 고유한 UUID를 자동 생성하며,
    #   __init__ 메서드에서는 제외됨
    id: UUID = field(default_factory=uuid4, init=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
