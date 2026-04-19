# === FastAPI 라우트에서의 자동 유효성 검증 동작 방식 ===
# Pydantic 모델을 라우트 파라미터로 선언하면 FastAPI가 자동으로 검증을 수행하는 예시

# FastAPI/Pydantic에서 검증이 작동하는 방식
# task_data 파라미터의 타입을 CreateTaskRequest로 선언하면,
# FastAPI가 요청 본문을 자동으로 파싱하고 Pydantic 모델로 검증
@app.post("/tasks/")
def create_task(task_data: CreateTaskRequest):
    # FastAPI가 이미 모든 필드를 검증함
    # 유효하지 않은 요청은 422 Unprocessable Entity로 거부됨
    # → 라우트 핸들러 코드에 도달하기 전에 검증이 완료되는 구조

    # 검증을 통과한 데이터만 컨트롤러로 전달
    result = task_controller.handle_create(title=task_data.title, description=task_data.description)
    return result.success


# 클라이언트가 빈 제목과 같은 유효하지 않은 데이터를 보낸다고 가정해 보자:

"""
{
  "title": "",
  "description": "테스트 기술"
}
"""

# FastAPI는 자동으로 검증 오류라고 응답할 것이다:
# 422 상태 코드와 함께 어떤 필드가 왜 유효하지 않은지 상세한 오류 정보를 반환
# 개발자가 별도로 오류 응답 형식을 정의할 필요가 없는 표준화된 응답

"""
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 1}
    }
  ]
}
"""
