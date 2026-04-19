# === Click CLI 프레임워크 어댑터 ===
# Click 라이브러리를 활용한 CLI 인터페이스 — 프레임워크 및 드라이버 계층에 위치
# Application 객체를 주입받아 의존성 규칙 준수

class ClickCli:
    def __init__(self, app: Application):
        # 의존성 주입: Application 컨테이너를 생성자로 전달받음
        self.app = app
        self.current_projects = []  # 표시용 프로젝트 캐시 목록

    def run(self) -> int:
        """Click CLI 애플리케이션 실행 진입점"""
        try:
            # 메인 이벤트 루프 — 프로젝트 목록 표시 후 사용자 입력 처리
            while True:
                self._display_projects()
                self._handle_selection()
        except KeyboardInterrupt:
            click.echo("\n안녕히 가세요!", err=True)
            return 0

    def _display_task_menu(self, task_id: str) -> None:
        """작업 상세 정보 표시 — 컨트롤러를 통해 유스 케이스 실행"""
        result = self.app.task_controller.handle_get(task_id)
        if not result.is_success:
            click.secho(result.error.message, fg="red", err=True)
            return
        # 뷰 모델에서 사용자에게 보여줄 데이터 추출
        task = result.success
        click.clear()
        click.echo("\n작업 상세 정보")
        click.echo("=" * 40)
        click.echo(f"제목:       {task.title}")
        click.echo(f"설명:       {task.description}")
        click.echo(f"상태:       {task.status_display}")
        click.echo(f"우선순위:   {task.priority_display}")

    def _handle_selection(self) -> None:
        """프로젝트/작업 선택 라우팅 — 사용자 입력에 따라 적절한 핸들러로 분기"""
        selection = (
            click.prompt(
                "\n프로젝트 또는 작업을 선택하세요 (예: '1' 또는 '1.a')", type=str, show_default=False
            )
            .strip()
            .lower()
        )
        if selection == "np":
            self._create_new_project()
            return
        try:
            if "." in selection:
                # "1.a" 형식: 프로젝트 번호와 작업 문자를 분리하여 작업 선택 처리
                project_num, task_letter = selection.split(".")
                self._handle_task_selection(int(project_num), task_letter)
            else:  # 프로젝트 선택
                self._handle_project_selection(int(selection))
        except (ValueError, IndexError):
            click.secho(
                "잘못 선택했습니다. 프로젝트는 '1', 작업은 '1.a'를 사용하세요.",
                fg="red",
                err=True,
            )

    def _create_new_project(self) -> None:
        """새 프로젝트 생성 — CLI 입력을 컨트롤러에 전달"""
        name = click.prompt("프로젝트 이름", type=str)
        description = click.prompt("설명 (선택사항)", type=str, default="")
        # 컨트롤러가 DTO 변환 및 유스 케이스 실행을 담당
        result = self.app.project_controller.handle_create(name, description)
        if not result.is_success:
            click.secho(result.error.message, fg="red", err=True)

    # ... 추가 메서드
