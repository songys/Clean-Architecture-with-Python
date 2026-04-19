# EcomApp/order_system/web/app.py
"""
11장의 피처 플래그 변환 패턴을 보여주는 간소화된 Flask 앱.
스트랭글러 피그(Strangler Fig) 패턴으로 레거시 → 클린 아키텍처 점진적 전환 시연.
"""
# ──────────────────────────────────────────────────────────────
# 웹/프레임워크 계층 - Flask 앱 팩토리
# 의존성 조립(Composition Root) 역할을 겸하며,
# 피처 플래그로 레거시 경로와 클린 아키텍처 경로를 전환
# ──────────────────────────────────────────────────────────────
import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from uuid import UUID, uuid4

from ..config import Config

# 클린 아키텍처 구성 요소 임포트
from ..application.use_cases.create_order import CreateOrderRequest, CreateOrderUseCase
from ..infrastructure.repositories.sqlite_order_repository import SQLiteOrderRepository
from ..infrastructure.repositories.sqlite_product_repository import SQLiteProductRepository
from ..infrastructure.services.dummy_payment_service import DummyPaymentService
from ..interfaces.controllers.order_controller import OrderController


# 앱 팩토리 함수 (Composition Root)
# 모든 의존성을 조립하고 Flask 앱 인스턴스를 반환
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 피처 플래그 설정 - 환경 변수로 재정의 가능
    # True → 클린 아키텍처 경로, False → 레거시 경로
    app.config["USE_CLEAN_ARCHITECTURE"] = os.getenv("USE_CLEAN_ARCHITECTURE", "True").lower() in (
        "true",
        "1",
        "yes",
    )

    print(f"주문 처리 시스템 시작")
    print(f"피처 플래그: USE_CLEAN_ARCHITECTURE = {app.config['USE_CLEAN_ARCHITECTURE']}")
    print(f"데이터베이스: {app.config['DB_PATH']}")

    # 레거시 경로에서 사용하는 직접 DB 연결 헬퍼
    def get_db_connection():
        conn = sqlite3.connect(app.config["DB_PATH"])
        conn.row_factory = sqlite3.Row
        return conn

    # 클린 아키텍처 구성 요소를 조립하는 팩토리 함수
    # 저장소 → 서비스 → 유스케이스 → 컨트롤러 순서로 의존성 주입
    def get_order_controller():
        """클린 아키텍처 구성 요소를 생성하는 팩토리"""
        db_path = app.config["DB_PATH"]

        # 인프라 계층: 저장소 구현체 생성
        order_repository = SQLiteOrderRepository(db_path)
        product_repository = SQLiteProductRepository(db_path)

        # 인프라 계층: 결제 서비스 구현체 생성
        payment_service = DummyPaymentService()

        # 애플리케이션 계층: 유스케이스 생성 (저장소·서비스 주입)
        create_use_case = CreateOrderUseCase(
            order_repository=order_repository,
            product_repository=product_repository,
            payment_service=payment_service,
        )

        # 인터페이스 어댑터 계층: 컨트롤러 생성 (유스케이스 주입)
        return OrderController(create_use_case=create_use_case)

    # 클린 아키텍처 경로를 위한 컨트롤러 초기화
    order_controller = get_order_controller()

    class ValidationError(Exception):
        pass

    @app.route("/")
    def index():
        """현재 피처 플래그 상태와 주문 폼을 보여주는 홈 페이지"""
        db_path = app.config["DB_PATH"]
        product_repository = SQLiteProductRepository(db_path)
        products = product_repository.get_all()

        # 표시할 최근 주문 조회
        orders = get_recent_orders()

        return render_template(
            "index.html",
            use_clean_arch=app.config["USE_CLEAN_ARCHITECTURE"],
            products=products,
            orders=orders,
        )

    @app.route("/orders", methods=["GET"])
    def get_orders():
        """최근 주문을 가져오는 API 엔드포인트"""
        orders = get_recent_orders()
        return jsonify(orders)

    # ──────────────────────────────────────────────────────────
    # 스트랭글러 피그 패턴의 핵심: 단일 진입점에서 피처 플래그로 분기
    # ──────────────────────────────────────────────────────────
    @app.route("/orders", methods=["POST"])
    def create_order():
        """
        11장에서 설명한 정확한 패턴.
        피처 플래그를 사용하여 레거시 구현과 클린 아키텍처 구현 중
        선택하는 단일 라우트 핸들러.
        """
        data = request.get_json()

        # 기본 입력 검증은 라우트 핸들러에 유지 (인터페이스 계층의 책임)
        if not data or not "customer_id" in data or not "items" in data:
            return jsonify({"error": "필수 필드가 누락되었습니다"}), 400

        try:
            # 어떤 구현이 요청을 처리할지 제어하는 피처 플래그
            if app.config.get("USE_CLEAN_ARCHITECTURE", False):
                # 클린 경로: 컨트롤러 → 유스케이스 → 도메인 엔티티 흐름
                result = order_controller.handle_create_order(data)
                result["implementation"] = "클린 아키텍처"
                return jsonify(result), 201
            else:
                # 레거시 경로: 모든 로직이 하나의 함수에 집중
                result = create_order_legacy(data)
                if "error" not in result[0].get_json():
                    result_data = result[0].get_json()
                    result_data["implementation"] = "레거시"
                    return jsonify(result_data), 201
                return result
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "내부 서버 오류"}), 500

    # 최근 주문 조회 헬퍼 (화면 표시용)
    def get_recent_orders():
        """표시할 최근 10개 주문을 조회"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT o.id, o.customer_id, o.status, o.created_at, o.total_price,
                       COUNT(oi.id) as item_count
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                GROUP BY o.id, o.customer_id, o.status, o.created_at, o.total_price
                ORDER BY o.created_at DESC
                LIMIT 10
            """
            )
            orders = []
            for row in cursor.fetchall():
                orders.append(
                    {
                        "id": row["id"],
                        "customer_id": row["customer_id"],
                        "status": row["status"],
                        "created_at": row["created_at"],
                        "total_price": row["total_price"],
                        "item_count": row["item_count"],
                    }
                )
            return orders
        finally:
            conn.close()

    # ──────────────────────────────────────────────────────────
    # 레거시 구현 (피처 플래그 False 시 사용)
    # 모든 아키텍처 문제(결합도, 테스트 불가 등)를 포함하는 "이전" 상태
    # ──────────────────────────────────────────────────────────
    def create_order_legacy(data):
        """
        11장에서 설명한 모든 아키텍처 문제를 포함하는 레거시 구현.
        변환 과정에서 '이전' 상태를 나타냄.
        """
        # 라우트 핸들러에서 데이터베이스에 직접 접근
        conn = get_db_connection()

        try:
            # 비즈니스 로직과 데이터 접근이 혼합됨
            total_price = 0
            for item in data["items"]:
                # 직접 데이터베이스 쿼리를 통한 재고 확인
                product = conn.execute(
                    "SELECT * FROM products WHERE id = ?", (item["product_id"],)
                ).fetchone()
                if not product or product["stock"] < item["quantity"]:
                    return jsonify({"error": f'제품 {item["product_id"]}의 재고가 없음'}), 400

                # 가격 계산
                price = product["price"] * item["quantity"]
                total_price += price

            # 라우트 핸들러에서 외부 결제 서비스를 직접 호출
            # 데모 목적으로 결제 처리를 시뮬레이션
            payment_success = True

            if not payment_success:
                return jsonify({"error": "결제 실패"}), 400

            # 라우트 핸들러에서 직접 주문 생성
            order_id = str(uuid4())
            conn.execute(
                "INSERT INTO orders (id, customer_id, status, created_at, total_price) VALUES (?, ?, ?, datetime(), ?)",
                (order_id, data["customer_id"], "PAID", total_price),
            )

            # 주문 항목 생성 및 재고 업데이트
            for item in data["items"]:
                product = conn.execute(
                    "SELECT price FROM products WHERE id = ?", (item["product_id"],)
                ).fetchone()

                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (order_id, item["product_id"], item["quantity"], product["price"]),
                )

                conn.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (item["quantity"], item["product_id"]),
                )

            conn.commit()
            return (
                jsonify({"order_id": order_id, "status": "success", "total_price": total_price}),
                201,
            )

        finally:
            conn.close()

    return app
