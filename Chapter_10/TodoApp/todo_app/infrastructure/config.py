"""
할 일 애플리케이션의 설정 구성.
- 환경 변수(.env)에서 설정을 읽어 애플리케이션에 제공
- 리포지토리 타입, 데이터 디렉토리, API 키 등 인프라 설정 관리
"""

from enum import Enum
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()


# 리포지토리 타입
class RepositoryType(Enum):
    MEMORY = "memory"
    FILE = "file"


class Config:
    """애플리케이션 설정."""

    # 기본값
    DEFAULT_REPOSITORY_TYPE: RepositoryType = RepositoryType.MEMORY
    DEFAULT_DATA_DIR = "repo_data"
    DEFAULT_LOG_DIR = "logs"  # 앱 실행 위치 기준 상대 경로
    DEFAULT_LOG_FILE = "todo_app.log"

    @classmethod
    def get_repository_type(cls) -> RepositoryType:
        """설정된 리포지토리 타입을 가져온다."""
        repo_type_str = os.getenv("TODO_REPOSITORY_TYPE", cls.DEFAULT_REPOSITORY_TYPE.value)
        try:
            return RepositoryType(repo_type_str.lower())
        except ValueError:
            raise ValueError(f"잘못된 리포지토리 타입: {repo_type_str}")

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
        """알림 수신 이메일을 가져온다."""
        return os.getenv("TODO_NOTIFICATION_EMAIL", "")

    @classmethod
    def get_log_file_path(cls) -> Path:
        """로그 파일 경로를 가져온다.

        Returns:
            필요한 경우 상위 디렉터리를 생성한 후 로그 파일 경로.
        """
        log_dir = Path(os.getenv("TODO_LOG_DIR", cls.DEFAULT_LOG_DIR))
        log_file = os.getenv("TODO_LOG_FILE", cls.DEFAULT_LOG_FILE)

        # 로그 디렉터리 존재 확인
        log_dir.mkdir(parents=True, exist_ok=True)

        return log_dir / log_file
