# order_system/infrastructure/repositories/sqlite_order_repository.py
# ──────────────────────────────────────────────────────────────
# 2단계: 인프라 계층 - SQLite 기반 주문 저장소 구현체
# 도메인의 OrderRepository 인터페이스를 SQLite로 충족하는 어댑터
# 기존 DB 스키마를 유지하면서 클린 도메인 모델과 연결하는 다리 역할
# ──────────────────────────────────────────────────────────────

# OrderRepository 인터페이스의 SQLite 구현체
# 도메인 엔티티(Order)를 SQL로 변환하여 영속화
class SQLiteOrderRepository(OrderRepository):

    # ... 구현 생략

    # 주문 저장 (신규 삽입 또는 기존 업데이트)
    # 트랜잭션으로 감싸 데이터 정합성 보장
    def save(self, order: Order) -> None:
        conn = sqlite3.connect(self.db_path)

        try:
            cursor = conn.cursor()
            # 주문이 존재하는지 확인하고 삽입 또는 업데이트 수행
            if self._order_exists(conn, order.id):
                # ... SQL 업데이트 작업 ...
            else:
                # ... SQL 삽입 작업 ...

                # ... 주문 항목에 대한 SQL 작업 ...
            conn.commit()
        except Exception as e:
            # 오류 발생 시 롤백으로 데이터 무결성 보호
            conn.rollback()
            raise RepositoryError(f"주문 저장 실패: {str(e)}")
        finally:
            conn.close()