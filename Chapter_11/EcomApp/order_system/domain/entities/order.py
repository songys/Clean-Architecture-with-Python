# order_system/domain/entities/order.py
# ──────────────────────────────────────────────────────────────
# 도메인 계층 - Order 엔티티 (핵심 비즈니스 모델)
# 외부 프레임워크·DB에 의존하지 않는 순수 Python 클래스
# 주문의 상태 전환, 금액 계산 등 비즈니스 규칙을 캡슐화
# ──────────────────────────────────────────────────────────────
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


# 주문 상태 열거형 (문자열 상수 대신 타입 안전한 Enum 사용)
class OrderStatus(Enum):
    CREATED = "CREATED"       # 주문 생성 직후 초기 상태
    PAID = "PAID"             # 결제 완료 상태
    FULFILLING = "FULFILLING" # 이행(포장/준비) 중 상태
    SHIPPED = "SHIPPED"       # 배송 중 상태
    DELIVERED = "DELIVERED"   # 배송 완료 상태
    CANCELED = "CANCELED"     # 취소 상태


# 주문 항목 값 객체 (Value Object)
# 개별 상품의 주문 수량과 단가 정보를 보관
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
# 주문 도메인의 비즈니스 규칙(상태 전환, 항목 추가 등)을 캡슐화
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

    # 주문에 항목 추가 후 수정 시각 갱신
    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)
        self.updated_at = datetime.now()

    # 결제 완료 상태로 전환
    # 비즈니스 규칙: CREATED 상태에서만 PAID로 전환 가능
    def mark_as_paid(self) -> None:
        if self.status != OrderStatus.CREATED:
            raise ValueError(f"결제 완료로 표시할 수 없음: 주문 상태가 {self.status.value}")
        self.status = OrderStatus.PAID
        self.updated_at = datetime.now()
