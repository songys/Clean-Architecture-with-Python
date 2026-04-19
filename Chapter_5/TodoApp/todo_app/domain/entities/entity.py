# 도메인 엔터티의 기본 클래스(Base Entity)
# - 모든 도메인 엔터티가 상속하는 기반 클래스
# - 고유 식별자(UUID)를 자동 생성하고, ID 기반 동등성 비교를 제공

from dataclasses import dataclass, field
from uuid import UUID, uuid4


# 도메인 엔터티 기반 클래스 - ID 기반 식별과 동등성 비교 제공
@dataclass
class Entity:
    # 'id' 필드에 고유한 UUID를 자동 생성함;
    #   __init__ 메서드에서 제외됨
    id: UUID = field(default_factory=uuid4, init=False)

    # 같은 타입의 엔터티끼리 ID로 동등성 비교
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    # ID 기반 해시값 - 집합(set)이나 딕셔너리 키로 사용 가능
    def __hash__(self) -> int:
        return hash(self.id)
