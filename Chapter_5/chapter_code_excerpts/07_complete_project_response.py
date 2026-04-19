# 응답 DTO(Data Transfer Object) - 프로젝트 완료 응답
# - 도메인 엔터티의 데이터를 외부(API 등)에 전달하기 적합한 형태로 변환하는 역할
# - from_entity 팩토리 메서드로 도메인 객체에서 응답 DTO로의 변환 수행
# - 요청 DTO의 to_execution_params와 대칭적인 구조: 입력은 외부→도메인, 출력은 도메인→외부

from dataclasses import dataclass
from typing import Optional, Self

from todo_app.domain.entities.project import Project


# 외부 서비스 스텁 (실제로는 사용자 정보 조회 등에 활용)
class UserService:
    """mypy를 위한 스텁"""

    ...


# 불변 데이터 클래스로 정의한 프로젝트 완료 응답 DTO
# - 도메인 객체(Project)를 직접 노출하지 않고, 필요한 필드만 선별하여 외부에 전달
@dataclass(frozen=True)
class CompleteProjectResponse:
    """프로젝트 완료 응답을 위한 데이터 구조"""

    # UUID를 문자열로 변환한 프로젝트 ID (외부 API 호환용)
    id: str
    # 프로젝트 상태를 문자열로 변환한 값
    status: str
    # 완료 일시를 ISO 형식 문자열로 변환한 값
    completion_date: str
    # 프로젝트에 포함된 작업 수 (도메인 객체에서 파생한 계산 필드)
    task_count: int
    # 완료 메모 (선택 사항)
    completion_notes: Optional[str]

    # 도메인 엔터티(Project)로부터 응답 DTO를 생성하는 팩토리 메서드
    # - 도메인 객체의 내부 구조를 외부에 노출하지 않으면서 필요한 데이터만 변환
    @classmethod
    def from_entity(cls, project: Project, user_service: UserService) -> Self:
        """도메인 엔터티로부터 응답 생성"""
        return cls(
            id=str(project.id),
            status=project.status.value,
            completion_date=project.completed_at.isoformat(),
            task_count=len(project.tasks),
            completion_notes=project.completion_notes,
        )
