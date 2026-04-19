"""
Todo 애플리케이션의 구성 설정.

인프라스트럭처 계층에 위치하며, 환경 변수를 통해 리포지토리 유형,
데이터 디렉터리, 외부 서비스 인증 정보 등 런타임 설정을 관리.
"""

from enum import Enum
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드 — 개발 환경 편의를 위한 설정
load_dotenv()


# 리포지토리 저장소 유형 열거형 — 메모리 또는 파일 시스템
class RepositoryType(Enum):
    MEMORY = "memory"
    FILE = "file"


class Config:
    """애플리케이션 구성 — 환경 변수 기반 설정 관리 클래스."""

    # 기본값 — 환경 변수가 없을 때 사용
    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.MEMORY
    DEFAULT_DATA_DIR = "repo_data"

    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """환경 변수 TODO_REPOSITORY_TYPE에서 리포지토리 유형 조회."""
        repo_type_str = os.getenv("TODO_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"잘못된 리포지토리 타입: {repo_type_str}")

    @classmethod
    def get_data_directory(cls) -> Path:
        """파일 리포지토리용 데이터 디렉터리 경로 — 존재하지 않으면 자동 생성."""
        data_dir = os.getenv("TODO_DATA_DIR", cls.DEFAULT_DATA_DIR)
        path = Path(data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_sendgrid_api_key(cls) -> str:
        """SendGrid API 키 조회 — 외부 이메일 알림 서비스 인증용."""
        return os.getenv("TODO_SENDGRID_API_KEY", "")

    @classmethod
    def get_notification_email(cls) -> str:
        """알림 수신자 이메일 조회 — 이메일 알림 발송 대상."""
        return os.getenv("TODO_NOTIFICATION_EMAIL", "")
