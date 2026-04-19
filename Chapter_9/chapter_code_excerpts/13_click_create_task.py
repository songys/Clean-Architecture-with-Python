# todo_app/infrastructure/cli/click_cli_app.py

# CLI 작업 생성 핸들러 - Click 프레임워크를 통해 사용자 입력을 수집
# 웹 라우트(14번 파일)와 비교하면, 입력 수집 방식만 다르고
# 컨트롤러 호출 방식은 동일 (동일한 handle_create 메서드 사용)
def _create_task(self):
    """CLI 작업 생성."""
    # Click의 prompt로 터미널에서 대화형 입력 수집
    title = click.prompt("작업 제목", type=str)
    description = click.prompt("설명", type=str)
    # 동일한 컨트롤러의 handle_create에 기본 타입(str)으로 전달
    result = self.app.task_controller.handle_create(title=title, description=description)
