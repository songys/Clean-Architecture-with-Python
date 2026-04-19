# order_system/config.py
# ──────────────────────────────────────────────────────────────
# 애플리케이션 설정 모듈
# 환경 변수로 재정의 가능한 설정값 모음
# ──────────────────────────────────────────────────────────────
import os


class Config:
    # 애플리케이션 이름
    APP_NAME = "주문 처리 시스템"

    # SQLite 데이터베이스 파일 경로 (환경 변수 DB_PATH로 재정의 가능)
    DB_PATH = os.getenv("DB_PATH", "order_system.db")

    # 피처 플래그: 클린 아키텍처 사용 여부
    # True → 클린 아키텍처 경로, False → 레거시 경로
    # 스트랭글러 피그 패턴의 핵심 스위치
    USE_CLEAN_ARCHITECTURE = os.getenv("USE_CLEAN_ARCHITECTURE", "True").lower() in (
        "true",
        "1",
        "yes",
    )
