# === 내부 전용 요청 모델 vs API 공개 요청 모델 비교 ===
# 클린 아키텍처에서 "내부용 DTO"와 "외부 공개 API DTO"를 분리하는 이유와 차이점을 보여주는 예제

# 작업 관리 요청 모델 - 내부 전용
# 프레젠테이션 계층(CLI, 웹 UI) 뒤에 숨겨진 내부 모델
# 외부 시스템이 직접 접근하지 않으므로 자유롭게 변경 가능
class CreateTaskRequest:
    """작업 생성 요청을 위한 데이터 구조."""

    title: str
    description: str
    project_id: Optional[str] = None

    def to_execution_params(self) -> dict:
        """검증된 요청 데이터를 유스 케이스 매개변수로 변환"""
        # 내부 모델이므로 strip(), UUID 변환 등 복잡한 변환 로직을 자유롭게 포함
        # 도메인 계층이 필요로 하는 형태로 데이터를 가공하는 역할
        return {
            "title": self.title.strip(),
            "project_id": UUID(self.project_id) if self.project_id else None,
            "description": self.description.strip(),
        }


# API 요청 DTO - 이제 공개 계약
# API 우선 시스템에서는 이 모델이 외부에 직접 노출됨
# 한번 공개되면 함부로 변경할 수 없는 "공개 계약(Public Contract)"
# to_execution_params 메서드가 없는 이유: 클라이언트가 이미 API 계약에 맞춰 데이터를 보내기 때문
class CreateTaskRequest:
    title: str
    description: str
    project_id: Optional[str] = None
