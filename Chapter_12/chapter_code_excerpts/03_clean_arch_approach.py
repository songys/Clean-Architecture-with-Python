# === 순수 클린 아키텍처 접근법: Pydantic 모델의 내부 침투 방지 ===
# 프레임워크(FastAPI/Pydantic)에 속하는 모델이 도메인 내부로 침투하지 않도록
# API 경계에서 내부 도메인 모델로 변환하는 패턴

# FastAPI를 사용한 순수 클린 아키텍처 접근법
@app.post("/tasks/")
def create_task(
    task_data: CreateTaskRequest,
):  # 여기서 Pydantic은 프레임워크 계층에 있음
    # 핵심 원칙: 프레임워크 의존성(Pydantic 모델)이 내부 계층으로 전파되지 않도록 차단
    # Pydantic 모델 → 순수 Python 내부 모델로 변환하는 경계 지점
    # 이 변환 덕분에 컨트롤러와 유스 케이스는 FastAPI/Pydantic을 전혀 알 필요가 없는 구조
    request = InternalCreateTaskRequest(
        title=task_data.title.strip(), description=task_data.description.strip()
    )

    # 내부 모델을 컨트롤러에 전달
    # 컨트롤러는 프레임워크에 독립적인 순수 도메인 객체만 다루는 구조
    result = task_controller.handle_create(request)
    return result.success
