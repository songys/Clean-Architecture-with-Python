"""
할일 앱을 위한 플라스크 웹 애플리케이션 설정.
Flask 웹 앱 생성 팩토리 - 클린 아키텍처의 Application 컨테이너를 Flask에 통합
"""

# [수정] flask 미설치 시에도 동작하도록 보호
try:
    from flask import Flask
except ImportError:
    Flask = None  # type: ignore
from todo_app.infrastructure.configuration.container import Application


# Flask 애플리케이션 팩토리 메서드
# Application 컨테이너를 Flask 설정에 주입하여 라우트에서 접근 가능하게 설정
def create_web_app(app_container: Application) -> Flask:
    """플라스크 애플리케이션을 생성하고 구성한다."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"  # 프로덕션에서는 변경할 것
    # Application 컨테이너를 Flask config에 저장 - 라우트에서 current_app.config으로 접근
    flask_app.config["APP_CONTAINER"] = app_container  # 컨테이너를 설정에 저장

    # Flask 블루프린트 등록 - URL 라우팅 규칙을 모듈별로 분리
    from . import routes

    flask_app.register_blueprint(routes.bp)

    return flask_app
