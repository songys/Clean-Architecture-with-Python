# order_system/application/use_cases/create_order.py
# ──────────────────────────────────────────────────────────────
# 애플리케이션 계층 - 주문 생성 유스케이스
# 레거시 라우트 핸들러에서 추출한 비즈니스 워크플로
# 저장소·서비스 인터페이스에만 의존하므로 단위 테스트 용이
# 순서: 주문 생성 → 재고 확인·차감 → 결제 처리 → 상태 변경·저장
# ──────────────────────────────────────────────────────────────
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from ...domain.entities.order import Order, OrderItem
from ...domain.repositories.order_repository import OrderRepository
from ...domain.repositories.product_repository import ProductRepository
from ...domain.services.payment_service import PaymentService, PaymentResult


# 유스케이스 입력 DTO (Data Transfer Object)
# 웹 계층의 HTTP 요청과 도메인 사이의 변환 경계 역할
@dataclass
class CreateOrderRequest:
    customer_id: UUID
    items: List[Dict[str, Any]]


# 주문 생성 유스케이스
# 의존성 주입으로 저장소와 서비스 인터페이스를 받아 비즈니스 워크플로 조율
@dataclass
class CreateOrderUseCase:
    order_repository: OrderRepository        # 주문 저장소 인터페이스
    product_repository: ProductRepository    # 제품 저장소 인터페이스
    payment_service: PaymentService          # 결제 서비스 인터페이스

    # 주문 생성 워크플로 실행 메서드
    def execute(self, request: CreateOrderRequest) -> Order:
        # 기본 정보로 주문 엔터티 생성
        order = Order(customer_id=request.customer_id)

        # 각 주문 항목에 대해 재고 확인 및 차감
        for item_data in request.items:
            product_id = UUID(item_data["product_id"])
            quantity = item_data["quantity"]

            # 제품 조회 및 재고 확인
            product = self.product_repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"ID가 {product_id}인 제품을 찾을 수 없습니다")

            # 재고 업데이트 (Product 엔티티의 도메인 메서드 활용)
            product.decrease_stock(quantity)
            self.product_repository.update(product)

            # 주문에 항목 추가
            order_item = OrderItem(product_id=product_id, quantity=quantity, price=product.price)
            order.add_item(order_item)

        # 결제 처리 (추상 PaymentService를 통해 외부 의존성 격리)
        payment_result = self.payment_service.process_payment(order)
        if not payment_result.success:
            raise ValueError(f"결제에 실패했습니다: {payment_result.error_message}")

        # 결제 완료 상태로 전환 후 저장소에 영속화
        order.mark_as_paid()
        self.order_repository.save(order)

        return order
