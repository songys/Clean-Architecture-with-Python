# ──────────────────────────────────────────────────────────────
# 1단계: 도메인 계층 - Order 엔티티
# 레거시 코드에 흩어져 있던 주문 관련 비즈니스 규칙을
# 하나의 엔티티로 캡슐화한 결과물
# ──────────────────────────────────────────────────────────────
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


# 주문 상태를 나타내는 열거형
# 레거시에서 문자열 상수("PAID", "SHIPPED" 등)로 흩어져 있던 것을 Enum으로 통합
class OrderStatus(Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    FULFILLING = "FULFILLING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


# 주문 항목 값 객체 (Value Object)
# 주문과 제품 사이의 관계를 표현하는 불변 개념
@dataclass
class OrderItem:
    product_id: UUID
    quantity: int
    price: float

    # 항목별 소계 (단가 x 수량)
    @property
    def total_price(self) -> float:
        return self.price * self.quantity


# 주문 엔티티 (Aggregate Root)
# 주문 도메인의 핵심 비즈니스 규칙을 캡슐화한 풍부한 도메인 모델
@dataclass
class Order:
    customer_id: UUID
    items: List[OrderItem] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now())
    updated_at: Optional[datetime] = None

    # 전체 주문 금액 (모든 항목의 소계 합산)
    @property
    def total_price(self) -> float:
        return sum(item.total_price for item in self.items)

    # 주문에 항목을 추가하는 도메인 메서드
    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)
        self.updated_at = datetime.now()

    # 결제 완료 상태로 전환하는 도메인 메서드
    # 비즈니스 규칙: CREATED 상태에서만 PAID로 전환 가능
    def mark_as_paid(self) -> None:
        if self.status != OrderStatus.CREATED:
            raise ValueError(f"결제 완료로 표시할 수 없음: 주문 상태가 {self.status.value}")
        self.status = OrderStatus.PAID
        self.updated_at = datetime.now()
