# AST(추상 구문 트리)를 활용한 의존성 규칙 자동 검증
# - 소스 코드를 파싱하여 import 문을 분석하는 정적 분석 방식
# - 런타임 없이 의존성 위반을 감지 가능
import ast
from pathlib import Path


# 도메인 계층의 의존성 규칙 검증 테스트
# - 클린 아키텍처의 핵심 원칙: 도메인 계층은 어떤 외부 계층도 참조하면 안 됨
# - domain 폴더의 모든 .py 파일을 AST로 파싱하여 import 문 검사
def test_domain_layer_dependencies(self):
    """도메인 계층이 외부 의존성이 없는지 확인한다."""
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
                    # 도메인이 application, interfaces, infrastructure를 참조하면 위반
                    if layer in ["infrastructure", "interfaces", "application"]:
                        violations.append(
                            f"{py_file.relative_to(domain_path)}: "
                            f"도메인 계층은 {layer} 계층에서 "
                            f"임포트할 수 없음"
                        )
            # from xxx import yyy 형태
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("todo_app."):
                    layer = node.module.split(".")[1]
                    if layer in ["infrastructure", "interfaces", "application"]:
                        violations.append(
                            f"{py_file.relative_to(domain_path)}: "
                            f"도메인 계층은 {layer} 계층에서 "
                            f"임포트할 수 없음"
                        )
    # 위반 목록이 비어있어야 테스트 통과
    self.assertEqual(violations, [], "\n의존성 규칙 위반:\n" + "\n".join(violations))
