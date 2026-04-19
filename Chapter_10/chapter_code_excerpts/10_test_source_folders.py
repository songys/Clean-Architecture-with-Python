from pathlib import Path


# 소스 폴더 구조 검증 테스트
# - 프로젝트의 최상위 디렉토리가 클린 아키텍처의 4개 계층과 정확히 일치하는지 확인
# - 새로운 폴더가 무분별하게 추가되는 것을 방지하는 아키텍처 가드레일
def test_source_folders(self):
    """todo_app이 클린 아키텍처 계층 폴더만 포함하는지 확인한다."""
    src_path = Path("todo_app")
    folders = {f.name for f in src_path.iterdir() if f.is_dir()}

    # 검증 1: 모든 필수 계층 폴더가 존재하는지 확인
    for layer in ArchitectureConfig.LAYER_HIERARCHY:
        self.assertIn(layer, folders, f"{layer} 계층 폴더가 없음")

    # 검증 2: 정의되지 않은 예상치 못한 폴더가 없는지 확인
    unexpected = folders - set(ArchitectureConfig.LAYER_HIERARCHY)
    self.assertEqual(
        unexpected,
        set(),
        f"소스는 클린 아키텍처 계층만 포함해야 합니다.\n"
        f"예상치 못한 폴더 발견: {unexpected}",
    )
