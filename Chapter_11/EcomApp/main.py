# order_system/main.py - 주문 처리 시스템 진입점
# ──────────────────────────────────────────────────────────────
# 애플리케이션 부트스트랩 모듈
# Flask 앱 팩토리(create_app)를 호출하여 의존성 조립 후 서버 기동
# ──────────────────────────────────────────────────────────────
from order_system.web.app import create_app

# 팩토리 함수로 앱 인스턴스 생성 (의존성 주입 포함)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
