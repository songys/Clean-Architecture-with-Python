# todo_app/infrastructure/web/app.py
# Flask 앱 팩토리 함수 - 트레이스 미들웨어 통합 예시
# - 애플리케이션 컨테이너를 Flask 설정에 저장하여 라우트에서 접근 가능
# - trace_requests 미들웨어로 모든 웹 요청에 트레이스 ID 자동 부여
def create_web_app(app_container: Application) -> Flask:
    """플라스크 애플리케이션 생성 및 구성."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"  # 프로덕션에서는 변경할 것
    # 클린 아키텍처의 Application 컨테이너를 Flask 설정에 저장
    flask_app.config["APP_CONTAINER"] = app_container

    # 추적 ID 미들웨어 추가 (요청별 트레이스 ID 자동 생성/전파)
    trace_requests(flask_app)

    # ...
