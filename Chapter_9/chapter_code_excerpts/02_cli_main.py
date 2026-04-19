# cli_main.py

# CLI 인터페이스의 컴포지션 루트 (진입점)
# 동일한 핵심 애플리케이션에 CLI 전용 프레젠터를 주입하여 CLI 앱 구성
def main() -> int:
    """CLI 애플리케이션의 메인 진입점."""
    # CLI 전용 의존성을 주입하여 Application 컨테이너 생성
    # NotificationRecorder: 알림을 콘솔에 기록하는 간단한 구현체
    # CliTaskPresenter/CliProjectPresenter: 터미널 출력에 적합한 포맷 담당
    app = create_application(
        notification_service=NotificationRecorder(),
        task_presenter=CliTaskPresenter(),
        project_presenter=CliProjectPresenter(),
    )
    # Click 프레임워크 기반 CLI 실행기에 애플리케이션 컨테이너 전달
    cli = ClickCli(app)
    return cli.run()
