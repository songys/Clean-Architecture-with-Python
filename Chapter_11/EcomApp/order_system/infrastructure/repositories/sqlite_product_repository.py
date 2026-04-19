# order_system/infrastructure/repositories/sqlite_product_repository.py
# ──────────────────────────────────────────────────────────────
# 인프라 계층 - SQLite 기반 제품 저장소 구현체
# 도메인의 ProductRepository 인터페이스를 SQLite로 충족하는 어댑터
# 초기화 시 테이블 자동 생성 및 샘플 데이터 투입 포함
# ──────────────────────────────────────────────────────────────
import sqlite3
from typing import List, Optional
from uuid import UUID

from ...domain.entities.product import Product
from ...domain.repositories.product_repository import ProductRepository


# ProductRepository 인터페이스의 SQLite 구현체
class SQLiteProductRepository(ProductRepository):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    # 제품 테이블 자동 생성 및 샘플 데이터 투입
    def _ensure_tables(self) -> None:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            """
            )
            conn.commit()

            # 테이블이 비어 있으면 샘플 제품 추가 (데모용 초기 데이터)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]

            if count == 0:
                sample_products = [
                    (str(UUID("eeb9e5e6-7585-4809-abb5-548f46ca93ea")), "Laptop", 999.99, 10),
                    (str(UUID("1c9e3f9a-9cf8-4df0-8426-7bd241592cef")), "Smartphone", 499.99, 20),
                    (str(UUID("d8cf7035-7cb1-4dd5-8a9b-3d9a618dbf10")), "Headphones", 99.99, 30),
                    (str(UUID("f6c843d5-907b-462c-8513-82e19638a735")), "Tablet", 349.99, 15),
                ]
                conn.executemany(
                    "INSERT INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
                    sample_products,
                )
                conn.commit()
        finally:
            conn.close()

    # ID로 제품 조회 후 도메인 엔티티로 복원
    def get_by_id(self, product_id: UUID) -> Optional[Product]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (str(product_id),))
            data = cursor.fetchone()

            if not data:
                return None

            # SQL 행 → Product 도메인 엔티티 변환
            return Product(
                id=UUID(data["id"]), name=data["name"], price=data["price"], stock=data["stock"]
            )
        finally:
            conn.close()

    # 새 제품 저장
    def save(self, product: Product) -> None:
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute(
                "INSERT INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
                (str(product.id), product.name, product.price, product.stock),
            )
            conn.commit()
        finally:
            conn.close()

    # 기존 제품 정보 업데이트 (재고 차감 후 호출)
    def update(self, product: Product) -> None:
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute(
                "UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?",
                (product.name, product.price, product.stock, str(product.id)),
            )
            conn.commit()
        finally:
            conn.close()

    # 전체 제품 목록 조회
    def get_all(self) -> List[Product]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            products_data = cursor.fetchall()

            products = []
            for data in products_data:
                product = Product(
                    id=UUID(data["id"]), name=data["name"], price=data["price"], stock=data["stock"]
                )
                products.append(product)

            return products
        finally:
            conn.close()
