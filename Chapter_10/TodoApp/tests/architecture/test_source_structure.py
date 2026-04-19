# 아키텍처 피트니스 함수 - 소스 폴더 구조 검증
# - 코드로 아키텍처 규칙을 표현하여 CI/CD에서 자동 검증 가능
# - 프로젝트 디렉토리가 클린 아키텍처의 4개 계층과 정확히 일치하는지 확인
from pathlib import Path
import unittest


class ArchitectureConfig:
    """클린 아키텍처 구조와 규칙을 정의한다."""

    # 가장 안쪽에서 가장 바깥쪽 계층 순서
    # - domain: 핵심 비즈니스 규칙 (엔터티, 값 객체)
    # - application: 유스 케이스, 리포지토리 인터페이스
    # - interfaces: 컨트롤러, 프레젠터, 뷰 모델
    # - infrastructure: 프레임워크, 데이터베이스, 외부 서비스
    LAYER_HIERARCHY = ["domain", "application", "interfaces", "infrastructure"]


class TestSourceStructure(unittest.TestCase):
    """최상위 소스 구조가 클린 아키텍처를 따르는지 검증한다."""

    def test_source_folders(self):
        """todo_app이 클린 아키텍처 계층 폴더만 포함하는지 검증한다."""
        src_path = Path(__file__).parent.parent.parent / "todo_app"
        # 파이썬이 자동 생성하는 __pycache__ 등 dunder 접두어 폴더는 검증에서 제외
        folders = {
            f.name
            for f in src_path.iterdir()
            if f.is_dir() and not f.name.startswith("__")
        }

        # 검증 1: 모든 필수 계층 폴더 존재 확인
        for layer in ArchitectureConfig.LAYER_HIERARCHY:
            self.assertIn(layer, folders, f"{layer} 계층 폴더가 없음")

        # 검증 2: 정의되지 않은 예상치 못한 폴더가 없는지 확인
        unexpected = folders - set(ArchitectureConfig.LAYER_HIERARCHY)
        self.assertEqual(
            unexpected,
            set(),
            f"소스에는 클린 아키텍처 계층만 포함해야 합니다.\n"
            f"예상하지 못한 폴더 발견: {unexpected}",
        )
