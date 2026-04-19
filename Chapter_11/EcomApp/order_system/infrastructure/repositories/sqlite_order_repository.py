# order_system/infrastructure/repositories/sqlite_order_repository.py
# ──────────────────────────────────────────────────────────────
# 인프라 계층 - SQLite 기반 주문 저장소 구현체
# 도메인의 OrderRepository 인터페이스를 SQLite로 충족하는 어댑터
# 도메인 엔티티(Order) ↔ SQL 테이블 간의 매핑 담당
# ──────────────────────────────────────────────────────────────
import sqlite3
from typing import List, Optional
from uuid import UUID

from ...domain.entities.order import Order, OrderItem, OrderStatus
from ...domain.repositories.order_repository import OrderRepository


# 저장소 레벨의 사용자 정의 예외 클래스
class RepositoryError(Exception):
    pass


# OrderRepository 인터페이스의 SQLite 구현체
class SQLiteOrderRepository(OrderRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    # 필요한 테이블이 없으면 자동 생성하는 초기화 메서드
    def _ensure_tables(self) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            # 주문 테이블 생성
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    total_price REAL NOT NULL
                )
            """
            )
            # 주문 항목 테이블 생성 (orders 테이블과 외래키 관계)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id)
                )
            """
            )
            conn.commit()
        finally:
            conn.close()

    # 주문 존재 여부 확인 헬퍼 메서드
    def _order_exists(self, conn, order_id: UUID) -> bool:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM orders WHERE id = ?", (str(order_id),))
        return cursor.fetchone() is not None

    # 주문 저장 (신규 삽입 또는 기존 업데이트)
    # 트랜잭션으로 감싸 데이터 정합성 보장
    def save(self, order: Order) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            if self._order_exists(conn, order.id):
                # 기존 주문 업데이트
                conn.execute(
                    "UPDATE orders SET status = ?, updated_at = ?, total_price = ? WHERE id = ?",
                    (
                        order.status.value,
                        order.updated_at.isoformat() if order.updated_at else None,
                        order.total_price,
                        str(order.id),
                    ),
                )

                # 기존 항목 삭제 후 재삽입 (항목 변경에 대응)
                conn.execute("DELETE FROM order_items WHERE order_id = ?", (str(order.id),))
            else:
                # 새 주문 삽입
                conn.execute(
                    "INSERT INTO orders (id, customer_id, status, created_at, updated_at, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        str(order.id),
                        str(order.customer_id),
                        order.status.value,
                        order.created_at.isoformat(),
                        order.updated_at.isoformat() if order.updated_at else None,
                        order.total_price,
                    ),
                )

            # 주문 항목 삽입
            for item in order.items:
                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (str(order.id), str(item.product_id), item.quantity, item.price),
                )

            conn.commit()
        except Exception as e:
            # 오류 발생 시 롤백으로 데이터 무결성 보호
            conn.rollback()
            raise RepositoryError(f"주문 저장 실패: {str(e)}")
        finally:
            conn.close()

    # ID로 주문 조회 후 도메인 엔티티로 복원
    def get_by_id(self, order_id: UUID) -> Optional[Order]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            # 주문 조회
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (str(order_id),))
            order_data = cursor.fetchone()

            if not order_data:
                return None

            # 주문 항목 조회
            cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (str(order_id),))
            items_data = cursor.fetchall()

            # SQL 행 → 도메인 Order 엔티티로 변환 (역매핑)
            order = Order(customer_id=UUID(order_data["customer_id"]), id=UUID(order_data["id"]))

            # 주문 상태 설정
            order.status = OrderStatus(order_data["status"])

            # 항목 추가
            for item_data in items_data:
                item = OrderItem(
                    product_id=UUID(item_data["product_id"]),
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )
                order.add_item(item)

            return order
        except Exception as e:
            raise RepositoryError(f"주문 조회 실패: {str(e)}")
        finally:
            conn.close()

    # 특정 고객의 전체 주문 목록 조회
    def get_by_customer(self, customer_id: UUID) -> List[Order]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            # 고객의 주문 조회
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM orders WHERE customer_id = ?", (str(customer_id),))
            order_ids = cursor.fetchall()

            # 각 주문 ID로 get_by_id를 호출하여 전체 엔티티 복원
            orders = []
            for order_id in order_ids:
                order = self.get_by_id(UUID(order_id["id"]))
                if order:
                    orders.append(order)

            return orders
        except Exception as e:
            raise RepositoryError(f"고객의 주문 조회 실패: {str(e)}")
        finally:
            conn.close()
