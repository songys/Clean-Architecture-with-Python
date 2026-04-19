#!/usr/bin/env python
"""
Todo 애플리케이션의 명령 줄 인터페이스 진입점.

이 모듈은 CLI 인터페이스의 컴포지션 루트 역할을 하며,
클린 아키텍처가 동일한 핵심 애플리케이션에 대해
다양한 인터페이스를 허용하는 방식을 보여 준다.

컴포지션 루트: 모든 구성 요소가 인스턴스화되고 연결되는 유일한 장소.
"""
import sys

# --- 인프라스트럭처 계층 의존성 ---
from todo_app.infrastructure.cli.click_cli_app import ClickCli
from todo_app.infrastructure.configuration.container import create_application
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
# --- 인터페이스 어댑터 계층 의존성 ---
from todo_app.interfaces.presenters.cli import CliTaskPresenter, CliProjectPresenter

import logging
import os
from datetime import datetime

# 로그 디렉터리가 존재하는지 확인
os.makedirs("logs", exist_ok=True)

# 파일에 로그를 기록하도록 로깅 구성 — 날짜별 로그 파일 생성
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(f'logs/todo_app_{datetime.now().strftime("%Y%m%d")}.log')],
)


def main() -> int:
    """
    CLI 애플리케이션의 메인 진입점 — 컴포지션 루트.
    구체적 구현체를 선택하여 애플리케이션을 조립하고 실행.

    Returns:
        종료 코드 (성공 시 0, 오류 시 0이 아닌 값)
    """
    try:
        # 의존성과 함께 애플리케이션 생성 — 구체적 구현체를 여기서 결정
        app = create_application(
            notification_service=NotificationRecorder(),  # 개발용 알림 기록기
            task_presenter=CliTaskPresenter(),             # CLI 전용 작업 프레젠터
            project_presenter=CliProjectPresenter(),       # CLI 전용 프로젝트 프레젠터
        )

        # CLI 프레임워크 어댑터 생성 및 실행
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
