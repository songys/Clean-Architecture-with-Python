# todo_app/infrastructure/web/app.py

# Flask 웹 애플리케이션 팩토리 메서드
# 클린 아키텍처의 Application 컨테이너를 Flask 설정에 주입하는 통합 지점
def create_web_app(app_container: Application) -> Flask:
    """플라스크 애플리케이션을 생성하고 구성."""
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "dev"  # 프로덕션에서는 이 값을 변경할 것
    # Application 컨테이너를 Flask config에 저장하여 라우트에서 접근 가능하게 설정
    flask_app.config["APP_CONTAINER"] = app_container  # 컨테이너를 config에 저장

    # Flask 블루프린트 등록 - 라우트를 모듈별로 분리하는 Flask 패턴
    from . import routes

    flask_app.register_blueprint(routes.bp)

    return flask_app
