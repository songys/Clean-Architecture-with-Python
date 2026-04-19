# order_system/application/use_cases/create_order.py
# ──────────────────────────────────────────────────────────────
# 2단계: 애플리케이션 계층 - 주문 생성 유스케이스
# 레거시 라우트 핸들러에 뒤섞여 있던 비즈니스 워크플로를
# 독립된 유스케이스 클래스로 추출한 결과물
# 저장소·서비스 인터페이스에만 의존하므로 테스트 용이
# ──────────────────────────────────────────────────────────────
from dataclasses import dataclass
from typing import List, Dict, Any
from uuid import UUID


# 유스케이스 입력 데이터를 담는 요청 DTO (Data Transfer Object)
# 웹 계층의 HTTP 요청과 도메인 사이의 변환 경계 역할
@dataclass
class CreateOrderRequest:
    customer_id: UUID
    items: List[Dict[str, Any]]


# 주문 생성 유스케이스
# 저장소와 서비스 인터페이스를 주입받아 비즈니스 워크플로 조율
@dataclass
class CreateOrderUseCase:
    order_repository: OrderRepository        # 주문 저장소 인터페이스
    product_repository: ProductRepository    # 제품 저장소 인터페이스
    payment_service: PaymentService          # 결제 서비스 인터페이스

    # 주문 생성 워크플로 실행
    # 순서: 주문 생성 → 재고 확인·차감 → 결제 처리 → 상태 변경·저장
    def execute(self, request: CreateOrderRequest) -> Order:
        # 기본 정보로 주문 엔터티 생성
        order = Order(customer_id=request.customer_id)

        # 주문에 항목 추가, 재고 확인
        for item_data in request.items:
            product_id = UUID(item_data["product_id"])
            quantity = item_data["quantity"]

            # ... 재고 검증 로직 ...

            # 재고 업데이트 (Product 엔티티의 도메인 메서드 활용)
            product.decrease_stock(quantity)
            self.product_repository.update(product)

        # 결제 처리 (추상 PaymentService를 통해 외부 의존성 격리)
        payment_result = self.payment_service.process_payment(order)
        if not payment_result.success:
            raise ValueError(f"결제에 실패했습니다: {payment_result.error_message}")

        # 주문을 결제 완료로 표시하고 저장
        order.mark_as_paid()
        self.order_repository.save(order)

        return order
