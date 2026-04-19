# test_order_creation.py
# ──────────────────────────────────────────────────────────────
# 2단계: 회귀 테스트 구축
# 리팩토링 전에 기존 동작을 보호하는 안전망 역할의 테스트
# 레거시 코드의 현재 동작을 그대로 검증하여,
# 클린 아키텍처로 전환 후에도 동일한 결과를 보장
# ──────────────────────────────────────────────────────────────

# 주문 생성 성공 시나리오 테스트
def test_create_order_success():
    # 테스트 데이터 및 예상 결과 설정
    response = client.post(
        "/orders", json={"customer_id": "12345", "items": [{"product_id": "789", "quantity": 2}]}
    )

    # 상태 코드와 응답 구조 검증
    assert response.status_code == 201
    assert "order_id" in response.json

    # 데이터베이스 상태 검증 - 주문이 올바른 값으로 생성되었는지 확인
    # 참고: 리팩토링 후에도 이 테스트가 통과해야 기존 동작 보존 확인 가능
    conn = get_db_connection()
    order = conn.execute(
        "SELECT * FROM orders WHERE id = ?", (response.json["order_id"],)
    ).fetchone()
    assert order["status"] == "PAID"


# 추가 주문 생성 테스트 시나리오 ...
