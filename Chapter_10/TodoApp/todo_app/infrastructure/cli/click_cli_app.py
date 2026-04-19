"""
프로젝트 기능이 강화된 Click 기반 CLI 구현.
- Click 라이브러리를 사용한 대화형 CLI 인터페이스
- Application 컨테이너의 컨트롤러를 호출하여 비즈니스 로직 실행
- CLI 세션 시작 시 트레이스 ID를 설정하여 세션 단위 로그 추적 가능
"""

from typing import Optional
import click

from todo_app.interfaces.view_models.task_vm import TaskViewModel
from todo_app.interfaces.view_models.project_vm import ProjectViewModel
from todo_app.infrastructure.configuration.container import Application
from todo_app.domain.value_objects import Priority
# 트레이스 ID 관리 모듈 (횡단 관심사)
from todo_app.infrastructure.logging.trace import set_trace_id, get_trace_id


class ClickCli:
    def __init__(self, app: Application):
        self.app = app
        self.current_projects = []  # 표시를 위해 캐시된 프로젝트 목록

    def run(self) -> int:
        """Click CLI 애플리케이션 실행 진입점"""
        try:
            # CLI 세션에 대한 추적 ID 설정 (이 세션의 모든 로그에 동일 ID 포함)
            set_trace_id()

            while True:
                self._display_projects()
                self._handle_selection()
        except KeyboardInterrupt:
            click.echo("\n종료합니다!", err=True)
            return 0

    def _display_projects(self) -> None:
        """모든 프로젝트와 작업을 표시한다."""
        click.clear()
        click.echo("\n프로젝트: ['np'를 입력하여 새 프로젝트 생성]")

        result = self.app.project_controller.handle_list()
        if not result.is_success:
            click.secho(result.error.message, fg="red", err=True)
            return

        self.current_projects = result.success
        for i, project in enumerate(self.current_projects, 1):
            click.echo(f"[{i}] 프로젝트: {project.name}")
            for j, task in enumerate(project.tasks):
                task_letter = chr(97 + j)
                click.echo(
                    f"  [{task_letter}] {task.title} {task.status_display} {task.priority_display}"
                )

    def _handle_project_menu(self, project: ProjectViewModel) -> None:
        """프로젝트 메뉴 기능을 처리한다."""
        while True:
            # 최신 프로젝트 데이터 가져오기
            result = self.app.project_controller.handle_get(project.id)
            if not result.is_success:
                click.secho(result.error.message, fg="red", err=True)
                return
            project = result.success

            click.clear()
            click.echo(f"\n프로젝트: {project.name}")
            click.echo(f"상태: {project.status_display}")
            click.echo(f"설명: {project.description}")
            click.echo(
                f"\n작업: 총 {project.task_count}개, {project.completed_task_count}개 완료"
            )

            click.echo("\n기능:")
            # INBOX가 아닌 프로젝트에만 편집 옵션 표시
            if project.project_type != "INBOX":
                click.echo("[1] 프로젝트 편집")
                click.echo("[2] 프로젝트에 작업 추가")
                click.echo("[3] 메인 메뉴로 돌아가기")
            else:
                click.echo("[1] 프로젝트에 작업 추가")
                click.echo("[2] 메인 메뉴로 돌아가기")

            if project.project_type != "INBOX":
                choice = click.prompt("기능 선택", type=str, default="3")
                if choice == "1":
                    self._edit_project(project)
                elif choice == "2":
                    self._add_task_to_project(project)
                elif choice == "3":
                    break
            else:
                choice = click.prompt("기능 선택", type=str, default="2")
                if choice == "1":
                    self._add_task_to_project(project)
                elif choice == "2":
                    break

    def _create_task(self, project_id: str) -> Optional[TaskViewModel]:
        """새 작업을 생성한다."""
        click.echo("\n새 작업 추가")
        title = click.prompt("작업 제목", type=str)
        description = click.prompt("설명", type=str, default="")
        priority = self._get_task_priority()

        # 작업 생성
        result = self.app.task_controller.handle_create(
            title=title,
            description=description,
            project_id=project_id,
            priority=priority,
        )

        if not result.is_success:
            click.secho(result.error.message, fg="red", err=True)
            return

        click.echo("작업이 성공적으로 생성되었습니다!")
        return result.success

    def _add_task_to_project(self, project: ProjectViewModel) -> None:
        """프로젝트에 새 작업을 추가한다."""
        task = self._create_task(project.id)
        if task:
            # 프로젝트 목록 새로고침
            refresh_result = self.app.project_controller.handle_list()
            if refresh_result.is_success:
                self.current_projects = refresh_result.success
        click.pause()

    def _get_task_priority(self) -> str:
        """사용자 입력으로부터 작업 우선순위를 가져온다."""
        click.echo("\n우선순위:")
        click.echo("[1] 낮음")
        click.echo("[2] 보통")
        click.echo("[3] 높음")
        priority_choice = click.prompt("우선순위 선택", type=str, default="2")

        priority_map = {"1": "LOW", "2": "MEDIUM", "3": "HIGH"}
        return priority_map.get(priority_choice, "MEDIUM")

    def _edit_project(self, project: ProjectViewModel) -> None:
        """프로젝트 상세 정보를 편집한다."""
        click.echo("\n프로젝트 편집")
        click.echo("현재 값을 유지하려면 비워 두세요")

        current_name = project.name
        current_description = project.description

        # 현재 값 표시 및 새 값 입력받기
        click.echo(f"\n현재 이름: {current_name}")
        new_name = click.prompt("새 이름", type=str, default="", show_default=False)

        click.echo(f"\n현재 설명: {current_description}")
        new_description = click.prompt("새 설명", type=str, default="", show_default=False)

        # 새 값이 제공된 경우에만 업데이트
        result = self.app.project_controller.handle_update(
            project_id=project.id,
            name=new_name if new_name else None,
            description=new_description if new_description else None,
        )

        if result.is_success:
            click.echo("프로젝트가 성공적으로 업데이트되었습니다!")
        else:
            click.secho(result.error.message, fg="red", err=True)

        click.pause()

    def _handle_selection(self) -> None:
        """프로젝트/작업 선택을 처리한다."""
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
            if "." in selection:  # 작업 선택 (예: "1.a")
                project_num, task_letter = selection.split(".")
                self._handle_task_selection(int(project_num), task_letter)
            else:  # 프로젝트 선택
                self._handle_project_selection(int(selection))
        except (ValueError, IndexError):
            click.secho(
                "잘못된 선택 형식입니다. 프로젝트는 '1', 작업은 '1.a'를 사용하세요.",
                fg="red",
                err=True,
            )

    def _handle_project_selection(self, project_num: int) -> None:
        """프로젝트 선택을 처리한다."""
        if not 1 <= project_num <= len(self.current_projects):
            click.secho("잘못된 프로젝트 번호입니다.", fg="red", err=True)
            return

        project = self.current_projects[project_num - 1]
        self._handle_project_menu(project)

    def _handle_task_selection(self, project_num: int, task_letter: str) -> None:
        """작업 선택을 처리한다."""
        if not 1 <= project_num <= len(self.current_projects):
            click.secho("잘못된 프로젝트 번호입니다.", fg="red", err=True)
            return

        project = self.current_projects[project_num - 1]
        task_index = ord(task_letter) - ord("a")

        if not 0 <= task_index < len(project.tasks):
            click.secho("잘못된 작업 문자입니다.", fg="red", err=True)
            return

        task = project.tasks[task_index]
        self._display_task_menu(task.id)

    def _create_new_project(self) -> None:
        """새 프로젝트를 생성한다."""
        name = click.prompt("프로젝트 이름", type=str)
        description = click.prompt("설명 (선택 사항)", type=str, default="")

        result = self.app.project_controller.handle_create(name, description)
        if not result.is_success:
            click.secho(result.error.message, fg="red", err=True)

    def _display_task_menu(self, task_id: str) -> None:
        """작업 메뉴를 표시하고 처리한다."""
        while True:
            result = self.app.task_controller.handle_get(task_id)
            if not result.is_success:
                click.secho(result.error.message, fg="red", err=True)
                return

            task = result.success
            click.clear()
            # 작업 상세 정보를 명확한 형식으로 표시
            click.echo("\n작업 상세")
            click.echo("=" * 40)
            click.echo(f"제목:       {task.title}")
            click.echo(f"설명:       {task.description}")
            click.echo(f"상태:       {task.status_display}")
            click.echo(f"우선순위:   {task.priority_display}")
            if task.completion_info:
                click.echo(f"완료:       {task.completion_info}")
            click.echo("=" * 40)

            # 간소화된 기능 메뉴 표시
            click.echo("\n기능:")
            click.echo("[1] 제목 편집")
            click.echo("[2] 설명 편집")
            click.echo("[3] 우선순위 편집")
            click.echo("[4] 작업 완료")
            click.echo("[5] 작업 삭제")
            click.echo("[Enter] 메인 메뉴로 돌아가기")

            choice = click.prompt("기능 선택", type=str, default="")

            if choice == "1":  # 제목 편집
                new_title = click.prompt("새 제목", type=str)
                result = self.app.task_controller.handle_update(task_id, title=new_title)
                if not result.is_success:
                    click.secho(result.error.message, fg="red", err=True)
                    click.pause()
            elif choice == "2":  # 설명 편집
                new_description = click.prompt("새 설명", type=str)
                result = self.app.task_controller.handle_update(
                    task_id, description=new_description
                )
                if not result.is_success:
                    click.secho(result.error.message, fg="red", err=True)
                    click.pause()
            elif choice == "3":  # 우선순위 편집
                self._update_task_priority(task_id)
                break
            elif choice == "4":  # 작업 완료
                self._complete_task(task_id)
            elif choice == "5":  # 작업 삭제
                if click.confirm("이 작업을 삭제하시겠습니까?"):
                    result = self.app.task_controller.handle_delete(task_id)
                    if result.is_success:
                        click.echo("작업이 성공적으로 삭제되었습니다")
                        break
                    else:
                        click.secho(result.error.message, fg="red", err=True)
                        click.pause()
            elif choice == "":  # 프로젝트 목록으로 돌아가기
                break

    def _update_task_priority(self, task_id: str) -> None:
        """작업 우선순위를 업데이트한다."""
        priorities = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}

        click.echo("\n우선순위:")
        for key, priority in priorities.items():
            click.echo(f"[{key}] {priority.name}")

        choice = click.prompt("우선순위 선택", type=str)
        if choice in priorities:
            result = self.app.task_controller.handle_update(
                task_id=str(task_id), priority=priorities[choice].name
            )
            if not result.is_success:
                click.secho(result.error.message, fg="red", err=True)

    def _complete_task(self, task_id: str) -> None:
        """작업을 완료한다."""
        notes = click.prompt("완료 메모 (선택 사항)", type=str, default="")
        result = self.app.task_controller.handle_complete(
            task_id=str(task_id), notes=notes if notes else None
        )
        if not result.is_success:
            click.secho(result.error.message, fg="red", err=True)
