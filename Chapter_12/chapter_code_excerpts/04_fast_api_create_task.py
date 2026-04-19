# === FastAPI를 활용한 실전 클린 아키텍처 라우트 구현 ===
# 응답 모델, HTTP 상태 코드, 오류 처리를 포함한 완성된 API 엔드포인트 패턴

# 프레임워크 계층 (infrastructure/api/routes.py)
# response_model: 응답 데이터의 자동 직렬화 및 문서화를 위한 Pydantic 모델 지정
# status_code=201: 리소스 생성 성공 시 반환할 HTTP 상태 코드
@app.post("/tasks/", response_model=TaskResponse, status_code=201)
def create_task(task_data: CreateTaskRequest):
    """새 작업 생성"""
    # 컨트롤러가 API 요청 데이터를 도메인 객체로 변환하는 역할 수행
    # 프레임워크 계층은 HTTP 관련 처리만 담당하고, 비즈니스 로직은 컨트롤러에 위임
    result = task_controller.handle_create(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id
    )

    if not result.is_success:
        # 프레임워크 경계에서 오류 처리
        # 도메인/애플리케이션 계층의 Result 객체를 HTTP 오류 응답으로 변환
        # 도메인 오류를 적절한 HTTP 상태 코드로 매핑하는 책임이 이 계층에 위치
        raise HTTPException(status_code=400, detail=result.error.message)

    return result.success  # TaskResponse로 자동 직렬화