# order_system/domain/entities/product.py
# ──────────────────────────────────────────────────────────────
# 도메인 계층 - Product 엔티티
# 재고 관리 규칙(음수 방지, 초과 출고 방지)을 엔티티 내부에 캡슐화
# "묻지 말고 시켜라(Tell, Don't Ask)" 원칙의 적용 사례
# ──────────────────────────────────────────────────────────────
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4


# 제품 엔티티
# 외부에서 stock 값을 직접 조작하지 않고, decrease_stock()을 통해서만 변경
@dataclass
class Product:
    name: str
    price: float
    stock: int
    id: UUID = field(default_factory=uuid4)

    # 재고 차감 도메인 메서드
    # 비즈니스 규칙: 양수 수량만 허용, 가용 재고 초과 시 예외 발생
    def decrease_stock(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("수량은 양수여야 합니다")
        if quantity > self.stock:
            raise ValueError(f"재고가 부족합니다: 요청 수량 {quantity}, 가용 수량 {self.stock}")
        self.stock -= quantity
