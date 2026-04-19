"""
할일 앱의 웹 인터페이스 진입점.
웹 인터페이스의 컴포지션 루트 역할 - cli_main.py와 대칭 구조
"""

# 웹 전용 의존성 import
from todo_app.infrastructure.configuration.container import create_application
from todo_app.infrastructure.web.app import create_web_app
from todo_app.infrastructure.notifications.factory import create_notification_service
from todo_app.interfaces.presenters.web import WebProjectPresenter, WebTaskPresenter


# 웹 인터페이스의 컴포지션 루트 - CLI와 동일한 핵심 로직에 웹 전용 프레젠터 주입
def main():
    """플라스크 웹 애플리케이션을 생성하고 실행한다."""

    # 웹 전용 프레젠터를 주입하여 Application 컨테이너 생성
    app_container = create_application(
        notification_service=create_notification_service(),
        task_presenter=WebTaskPresenter(),
        project_presenter=WebProjectPresenter(),
    )
    # Flask 웹 앱 생성 및 개발 모드로 실행
    web_app = create_web_app(app_container)
    web_app.run(debug=True)


if __name__ == "__main__":
    main()
