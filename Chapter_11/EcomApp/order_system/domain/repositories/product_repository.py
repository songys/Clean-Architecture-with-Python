# order_system/domain/repositories/product_repository.py
# ──────────────────────────────────────────────────────────────
# 도메인 계층 - ProductRepository 인터페이스 (추상 클래스)
# 제품 데이터의 CRUD 작업을 정의하는 추상화
# 실제 DB 구현(SQLiteProductRepository)은 인프라 계층에 위치
# ──────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.product import Product


# 제품 저장소 인터페이스 (도메인 계층에 위치)
class ProductRepository(ABC):
    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """ID로 제품을 조회"""
        pass

    @abstractmethod
    def save(self, product: Product) -> None:
        """제품을 리포지토리에 저장"""
        pass

    @abstractmethod
    def get_all(self) -> List[Product]:
        """모든 제품을 조회"""
        pass

    @abstractmethod
    def update(self, product: Product) -> None:
        """제품을 업데이트"""
        pass
