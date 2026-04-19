# === 도메인 계층: 작업-프로젝트 관계와 Inbox 패턴 ===
# 모든 작업은 반드시 프로젝트에 속하며, 프로젝트를 지정하지 않은 작업은 INBOX에 자동 할당

# 1. 도메인 계층: ProjectType 추가 및 엔터티 업데이트
from dataclasses import dataclass, field
from uuid import UUID


# 프로젝트 유형을 구분하는 값 객체 — REGULAR(일반)과 INBOX(기본 수집함)
class ProjectType(Enum):
    REGULAR = "REGULAR"
    INBOX = "INBOX"


@dataclass
class Project(Entity):
    """여러 작업을 포함하는 프로젝트 엔터티"""
    name: str
    description: str = ""
    project_type: ProjectType = field(default=ProjectType.REGULAR)

    @classmethod
    def create_inbox(cls) -> "Project":
        """INBOX 프로젝트 팩토리 메서드 — 할당되지 않은 작업의 기본 수집함"""
        return cls(
            name="INBOX",
            description="할당되지 않은 작업을 위한 기본 프로젝트",
            project_type=ProjectType.INBOX,
        )


@dataclass
class Task(Entity):
    """완료해야 할 작업 엔터티"""
    title: str
    description: str
    project_id: UUID  # 필수 필드 — 모든 작업은 반드시 프로젝트에 소속
