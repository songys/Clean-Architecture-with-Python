#!/usr/bin/env python
"""
할 일 애플리케이션의 명령줄 인터페이스 진입점.

이 모듈은 CLI 인터페이스의 컴포지션 루트 역할을 하며,
클린 아키텍처가 동일한 핵심 애플리케이션에 대해
다양한 인터페이스를 허용하는 방법을 보여준다.
"""
import sys


from todo_app.infrastructure.cli.click_cli_app import ClickCli
from todo_app.infrastructure.configuration.container import create_application
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
from todo_app.interfaces.presenters.cli import CliTaskPresenter, CliProjectPresenter
# 로깅 설정 모듈 (인프라스트럭처 계층)
from todo_app.infrastructure.logging.config import configure_logging


def main() -> int:
    """
    CLI 애플리케이션의 메인 진입점.
    - 컴포지션 루트: 모든 의존성을 조립하고 애플리케이션을 시작하는 곳
    - 로깅 초기화를 가장 먼저 수행하여 이후 모든 코드에서 로깅 사용 가능

    Returns:
        종료 코드 (성공 시 0, 오류 시 0이 아닌 값)
    """
    try:
        # CLI 컨텍스트로 로깅 초기화 (파일 로그만 기록, 콘솔은 CLI 출력 전용)
        configure_logging(app_context="CLI")
        # 의존성과 함께 애플리케이션 생성
        app = create_application(
            notification_service=NotificationRecorder(),
            task_presenter=CliTaskPresenter(),
            project_presenter=CliProjectPresenter(),
            app_context="CLI",
        )

        # 적절한 CLI 구현 생성 및 실행
        cli = ClickCli(app)
        return cli.run()
    except KeyboardInterrupt:
        print("\n종료합니다!")
        return 0
    except Exception as e:
        print(f"오류: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
