"""
할 일 앱을 위한 Flask 웹 애플리케이션 설정.
- Flask 앱 팩토리 패턴: 애플리케이션 생성과 설정을 함수로 캡슐화
- 트레이스 미들웨어 통합으로 모든 요청에 추적 ID 자동 부여
"""

# [수정] flask 미설치 시에도 동작하도록 보호
try:
    from flask import Flask
except ImportError:
    Flask = None  # type: ignore
from todo_app.infrastructure.configuration.container import Application
from todo_app.infrastructure.web.middleware import trace_requests


def create_web_app(app_container: Application) -> Flask:
    """Flask 애플리케이션을 생성하고 설정한다."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"  # 운영 환경에서는 변경 필요
    # 클린 아키텍처의 Application 컨테이너를 Flask 설정에 저장
    # - 라우트에서 current_app.config["APP_CONTAINER"]로 접근 가능
    flask_app.config["APP_CONTAINER"] = app_container

    # 추적 ID 미들웨어 추가 (요청별 트레이스 ID 자동 생성/전파)
    trace_requests(flask_app)

    # 블루프린트 등록 (라우트 분리)
    from . import routes

    flask_app.register_blueprint(routes.bp)

    return flask_app
