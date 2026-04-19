"""
Todo 애플리케이션의 구성 설정.
환경 변수를 통해 리포지토리 유형, 데이터 디렉터리, 외부 서비스 설정 관리
"""

from enum import Enum
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()


# 영속성 구현체 유형 - 환경 변수 TODO_REPOSITORY_TYPE으로 선택
class RepositoryType(Enum):
    MEMORY = "memory"
    FILE = "file"


# 환경 변수 기반 애플리케이션 구성 - 인프라 계층의 설정 관리
class Config:
    """애플리케이션 구성."""

    # 기본값
    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.MEMORY
    DEFAULT_DATA_DIR = "repo_data"

    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """구성된 리포지토리 유형을 가져온다."""
        repo_type_str = os.getenv("TODO_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"잘못된 리포지토리 유형: {repo_type_str}")

    @classmethod
    def get_data_directory(cls) -> Path:
        """데이터 디렉터리 경로를 가져온다."""
        data_dir = os.getenv("TODO_DATA_DIR", cls.DEFAULT_DATA_DIR)
        path = Path(data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_sendgrid_api_key(cls) -> str:
        """SendGrid API 키를 가져온다."""
        return os.getenv("TODO_SENDGRID_API_KEY", "")

    @classmethod
    def get_notification_email(cls) -> str:
        """알림 수신자 이메일을 가져온다."""
        return os.getenv("TODO_NOTIFICATION_EMAIL", "")
