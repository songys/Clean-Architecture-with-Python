from dataclasses import dataclass, field
from uuid import UUID, uuid4


# 모든 도메인 엔터티의 기반 클래스 - 고유 식별자와 동등성 비교 로직 제공
# - 엔터티는 고유 ID로 식별되며, 속성 값이 같아도 ID가 다르면 다른 엔터티로 취급
@dataclass
class Entity:
    # 'id' 필드에 대해 고유한 UUID를 자동 생성;
    #   __init__ 메서드에서 제외
    id: UUID = field(default_factory=uuid4, init=False)

    # ID 기반 동등성 비교 - 엔터티 패턴의 핵심 개념
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    # ID 기반 해시 - set이나 dict에서 사용 가능하게 하는 메서드
    def __hash__(self) -> int:
        return hash(self.id)
