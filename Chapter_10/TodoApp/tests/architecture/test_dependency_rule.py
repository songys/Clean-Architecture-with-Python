# 아키텍처 피트니스 함수 - 의존성 규칙 검증
# - AST(추상 구문 트리)를 활용한 정적 분석으로 import 문 검사
# - 클린 아키텍처의 핵심 원칙: 의존성은 반드시 안쪽(도메인)을 향해야 함
# - 도메인 계층이 application, interfaces, infrastructure를 참조하면 위반
import ast
from pathlib import Path
import unittest


class TestDependencyRule(unittest.TestCase):
    """클린 아키텍처의 의존성 규칙을 검증한다."""

    def test_domain_layer_dependencies(self):
        """도메인 계층에 외부 방향 의존성이 없는지 검증한다."""
        domain_path = Path("todo_app/domain")
        violations = []

        # 도메인 계층의 모든 파이썬 파일을 재귀적으로 탐색
        for py_file in domain_path.rglob("*.py"):
            with open(py_file) as f:
                # AST로 소스 코드 파싱 (실행 없이 구조만 분석)
                tree = ast.parse(f.read())

            # AST 노드를 순회하며 import 문 검사
            for node in ast.walk(tree):
                # import xxx 형태
                if isinstance(node, ast.Import):
                    module = node.names[0].name
                    if module.startswith("todo_app."):
                        layer = module.split(".")[1]
                        # 도메인이 바깥쪽 계층을 참조하면 위반
                        if layer in ["infrastructure", "interfaces", "application"]:
                            violations.append(
                                f"{py_file.relative_to(domain_path)}: "
                                f"도메인 계층은 {layer} 계층에서 임포트할 수 없음"
                            )
                # from xxx import yyy 형태
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("todo_app."):
                        layer = node.module.split(".")[1]
                        if layer in ["infrastructure", "interfaces", "application"]:
                            violations.append(
                                f"{py_file.relative_to(domain_path)}: "
                                f"도메인 계층은 {layer} 계층에서 임포트할 수 없음"
                            )

        # 위반 목록이 비어있어야 테스트 통과
        self.assertEqual(violations, [], "\n의존성 규칙 위반:\n" + "\n".join(violations))
