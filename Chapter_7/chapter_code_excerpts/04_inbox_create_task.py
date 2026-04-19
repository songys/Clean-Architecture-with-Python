# === Inbox 패턴 적용 후 간소화된 CLI 작업 생성 메서드 ===
# 프로젝트를 선택하지 않으면 유스 케이스가 자동으로 INBOX에 할당

def _create_task(self) -> None:
    """작업 생성 명령 처리 — ClickCli 클래스의 메서드 발췌"""
    title = click.prompt("작업 제목", type=str)
    description = click.prompt("설명", type=str)

    # 사용자가 특정 프로젝트를 선택할 수 있음 — 기본값은 Inbox
    if click.confirm("특정 프로젝트에 할당하시겠습니까?", default=False):
        project_id = self._select_project()

    # 컨트롤러를 통해 유스 케이스 실행 — Inbox 자동 할당은 유스 케이스에서 처리
    result = self.app.task_controller.handle_create(
        title=title, description=description, project_id=project_id
    )
