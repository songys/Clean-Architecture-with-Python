# order_system/interfaces/controllers/order_controller.py
# ──────────────────────────────────────────────────────────────
# 2단계: 인터페이스 어댑터 계층 - 주문 컨트롤러
# 웹 요청(Dict) ↔ 도메인 요청(CreateOrderRequest) 사이의 변환 담당
# Flask 등 특정 웹 프레임워크에 의존하지 않는 순수 Python 클래스
# ──────────────────────────────────────────────────────────────
from dataclasses import dataclass
from typing import Dict, Any
from uuid import UUID

# 주문 컨트롤러
# 유스케이스를 주입받아 웹 계층과 애플리케이션 계층 사이의 중재자 역할
@dataclass
class OrderController:
    create_use_case: CreateOrderUseCase

    # 주문 생성 요청 처리 메서드
    def handle_create_order(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 웹 요청을 도메인 요청 형식으로 변환 (입력 어댑터 역할)
            customer_id = UUID(request_data['customer_id'])
            items = request_data['items']

            request = CreateOrderRequest(
                customer_id=customer_id,
                items=items
            )

            # 유스 케이스 실행 (비즈니스 워크플로 위임)
            order = self.create_use_case.execute(request)

            # 도메인 응답을 웹 응답 형식으로 변환 (출력 어댑터 역할)
            return {
                'order_id': str(order.id),
                'status': order.status.value
            }
        except ValueError as e:
            # ... 예외 처리 로직