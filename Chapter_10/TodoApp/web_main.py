"""
할 일 앱의 웹 인터페이스 진입점.
- 웹 인터페이스의 컴포지션 루트
- CLI와 동일한 핵심 애플리케이션을 웹 프레젠터/프레임워크와 연결
"""

from todo_app.infrastructure.configuration.container import create_application
from todo_app.infrastructure.web.app import create_web_app
from todo_app.infrastructure.notifications.factory import create_notification_service
from todo_app.interfaces.presenters.web import WebProjectPresenter, WebTaskPresenter
# 로깅 설정 모듈 (인프라스트럭처 계층)
from todo_app.infrastructure.logging.config import configure_logging


def main():
    """플라스크 웹 애플리케이션을 생성하고 실행한다."""
    # WEB 컨텍스트로 로깅 초기화 (JSON 콘솔 + 파일 로그)
    configure_logging(app_context="WEB")
    """웹 인터페이스를 실행한다."""
    notification_service = create_notification_service()
    task_presenter = WebTaskPresenter()
    project_presenter = WebProjectPresenter()

    app_container = create_application(
        notification_service=notification_service,
        task_presenter=task_presenter,
        project_presenter=project_presenter,
        app_context="WEB",
    )
    web_app = create_web_app(app_container)
    web_app.run(debug=True)


if __name__ == "__main__":
    main()
