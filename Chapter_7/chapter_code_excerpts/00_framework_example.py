# === 프레임워크 vs 드라이버: 인프라스트럭처 계층의 두 가지 유형 비교 ===

# 프레임워크 예제 - 컨트롤러, 프레젠터 등 여러 어댑터 구성 요소 필요
@app.route("/tasks", methods=["POST"])
def create_task():
    """프레임워크는 전체 인터페이스 어댑터 스택이 필요"""
    # 컨트롤러를 통해 요청 데이터를 유스 케이스 형식으로 변환
    result = task_controller.handle_create(  # 6장의 컨트롤러
        title=request.json["title"], description=request.json["description"]
    )
    # 프레젠터를 통해 결과를 HTTP 응답 형식으로 변환
    return task_presenter.present(result)  # 6장의 프레젠터


# 드라이버 예제 - 포트 인터페이스와 그 구현체만 필요
class SQLiteTaskRepository(TaskRepository):  # 5장에서 정의한 리포지토리 인터페이스 구현
    """드라이버는 기본적인 인터페이스만 구현 — 프레임워크보다 단순한 구조"""

    def save(self, task: Task) -> None:
        # SQL을 사용한 실제 데이터 저장 — 인프라스트럭처 세부 구현
        self.connection.execute(
            "INSERT INTO tasks (id, title) VALUES (?, ?)", (str(task.id), task.title)
        )
