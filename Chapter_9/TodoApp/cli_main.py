#!/usr/bin/env python
"""
Todo 애플리케이션의 명령 줄 인터페이스 진입점.

이 모듈은 CLI 인터페이스의 컴포지션 루트 역할을 하며,
클린 아키텍처가 동일한 핵심 애플리케이션에 대해 서로 다른 인터페이스를
어떻게 허용하는지 보여준다.
"""
import sys

# CLI 전용 의존성 import
from todo_app.infrastructure.cli.click_cli_app import ClickCli
from todo_app.infrastructure.configuration.container import create_application
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
from todo_app.interfaces.presenters.cli import CliTaskPresenter, CliProjectPresenter

import logging
import os
from datetime import datetime

# logs 디렉터리가 존재하는지 확인
os.makedirs("logs", exist_ok=True)

# 파일에 로그를 기록하도록 로깅 구성
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(f'logs/todo_app_{datetime.now().strftime("%Y%m%d")}.log')],
)


# CLI 인터페이스의 컴포지션 루트 - web_main.py와 비교하면
# 프레젠터만 CLI 전용으로 교체되고, 나머지 핵심 로직은 동일
def main() -> int:
    """
    CLI 애플리케이션의 메인 진입점.

    Returns:
        종료 코드 (성공 시 0, 오류 시 0이 아닌 값)
    """
    try:
        # CLI 전용 프레젠터를 주입하여 애플리케이션 컨테이너 생성
        app = create_application(
            notification_service=NotificationRecorder(),
            task_presenter=CliTaskPresenter(),
            project_presenter=CliProjectPresenter(),
        )

        # Click 프레임워크 기반 CLI 실행기에 컨테이너 전달
        cli = ClickCli(app)
        return cli.run()
    except KeyboardInterrupt:
        print("\n안녕히 가세요!")
        return 0
    except Exception as e:
        print(f"오류: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
