# order_system/app.py
# ──────────────────────────────────────────────────────────────
# 레거시 코드 예시: 비즈니스 로직·데이터 접근·외부 호출이 하나의 라우트 핸들러에
# 뒤섞인 전형적인 안티패턴. 11장에서 클린 아키텍처로 리팩토링할 출발점
# ──────────────────────────────────────────────────────────────
from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)


# SQLite 데이터베이스 연결을 반환하는 헬퍼 함수
# 문제점: 전역 함수로 정의되어 어디서든 직접 DB에 접근 가능
def get_db_connection():
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    return conn


# 주문 생성 API 엔드포인트
# 문제점: 하나의 함수가 입력 검증, DB 접근, 외부 API 호출, 응답 생성을 모두 담당
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    # 입력 검증과 비즈니스 로직이 혼합됨
    if not data or not "customer_id" in data or not "items" in data:
        return jsonify({"error": "필수 필드 누락"}), 400

    # 라우트 핸들러에서 데이터베이스에 직접 접근
    conn = get_db_connection()

    # 비즈니스 로직과 데이터 접근이 혼합됨
    total_price = 0
    for item in data["items"]:
        # 직접 데이터베이스 쿼리를 통한 재고 확인
        # 문제점: 도메인 로직(재고 확인)이 SQL 쿼리와 결합
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (item["product_id"],)
        ).fetchone()
        if not product or product["stock"] < item["quantity"]:
            conn.close()
            return jsonify({"error": f'제품 {item["product_id"]}의 재고가 없음'}), 400

        # 가격 계산과 HTTP 응답 준비가 혼합됨
        price = product["price"] * item["quantity"]
        total_price += price

    # 라우트 핸들러에서 외부 결제 서비스를 직접 호출
    # 문제점: 결제 게이트웨이 URL이 하드코딩되어 테스트·교체 불가
    payment_result = requests.post(
        "https://payment-gateway.example.com/process",
        json={"customer_id": data["customer_id"], "amount": total_price, "currency": "USD"},
    )

    if payment_result.status_code != 200:
        conn.close()
        return jsonify({"error": "결제 실패"}), 400

    # 라우트 핸들러에서 직접 주문 생성
    # 문제점: 영속성 로직이 컨트롤러에 직접 포함
    order_id = conn.execute(
        "INSERT INTO orders (customer_id, total_price, status) VALUES (?, ?, ?)",
        (data["customer_id"], total_price, "PAID"),
    ).lastrowid

    # 주문 항목 생성 및 재고 업데이트
    for item in data["items"]:
        conn.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            (order_id, item["product_id"], item["quantity"], price),
        )
        conn.execute(  # 재고 업데이트
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )
    conn.commit()
    conn.close()
    return jsonify({"order_id": order_id, "status": "success"}), 201
