# 아키텍처 피트니스 함수를 위한 구조 정의
# - 코드로 아키텍처 규칙을 표현하여 자동화된 검증 가능
# - CI/CD 파이프라인에서 아키텍처 위반을 조기에 감지
class ArchitectureConfig:
    """클린 아키텍처 구조와 규칙 정의."""

    # 가장 안쪽에서 바깥쪽 계층 순으로 정렬
    # - domain: 핵심 비즈니스 규칙 (엔터티, 값 객체)
    # - application: 유스 케이스, 리포지토리 인터페이스
    # - interfaces: 컨트롤러, 프레젠터, 뷰 모델
    # - infrastructure: 프레임워크, 데이터베이스, 외부 서비스
    LAYER_HIERARCHY = [
        "domain",
        "application",
        "interfaces",
        "infrastructure",
    ]
