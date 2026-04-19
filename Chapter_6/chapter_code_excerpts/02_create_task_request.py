from dataclasses import dataclass
from typing import Optional


# 외부 입력을 유스케이스가 요구하는 형식으로 변환하는 요청 모델 (DTO)
# - frozen=True로 불변 객체를 보장하여 데이터 무결성 유지
# - 인터페이스 계층과 애플리케이션 계층 사이의 경계를 넘는 데이터 구조
@dataclass(frozen=True)
class CreateTaskRequest:
    """새로운 작업(Task)을 생성하기 위한 요청 데이터"""

    title: str  # 작업 제목 (필수)

    description: str  # 작업 설명 (필수)

    due_date: Optional[str] = None  # 마감일 (선택, 문자열 형태로 전달)

    priority: Optional[str] = None  # 우선순위 (선택, 문자열 형태로 전달)

    # 문자열 입력을 유스케이스 실행에 필요한 도메인 타입으로 변환하는 메서드
    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 실행에 필요한 파라미터로 변환"""

        params = {
            "title": self.title.strip(),
            "description": self.description.strip(),
        }

        if self.priority:
            # 문자열을 도메인 값 객체(Priority 열거형)로 변환
            params["priority"] = Priority[self.priority.upper()]

        return params


# 컨트롤러에서 요청 모델을 활용하는 흐름의 의사 코드
"""
# TaskController에서

try:

    request = CreateTaskRequest(title=title, description=description)

    # 요청이 검증되고 적절한 형식으로 변환됨

    result = self.create_use_case.execute(request)

except ValueError as e:

    # 유스 케이스에 도달하기 전에 검증 오류를 처리

    return OperationResult.fail(str(e), "VALIDATION_ERROR")

"""
