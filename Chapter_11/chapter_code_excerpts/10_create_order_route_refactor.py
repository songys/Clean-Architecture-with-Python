# order_system/app.py의 수정된 라우트
# ──────────────────────────────────────────────────────────────
# 3단계: 스트랭글러 피그(Strangler Fig) 패턴 적용
# 피처 플래그(USE_CLEAN_ARCHITECTURE)를 사용하여
# 레거시 구현과 클린 아키텍처 구현을 점진적으로 전환
# → 한 번에 전부 교체하지 않고 안전하게 단계적 마이그레이션 가능
# ──────────────────────────────────────────────────────────────
from flask import request, jsonify

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()

    # 기본 입력 검증은 라우트 핸들러에 유지
    # (웹 프레임워크 수준의 검증은 인터페이스 어댑터 계층의 책임)
    if not data or not 'customer_id' in data or not 'items' in data:
        return jsonify({'error': '필수 필드가 누락되었습니다'}), 400

    try:
        # 어떤 구현이 요청을 처리할지 제어하는 기능 플래그
        # True → 클린 아키텍처 경로, False → 레거시 경로
        if app.config.get('USE_CLEAN_ARCHITECTURE', False):
            # 클린 구현 사용: 컨트롤러 → 유스케이스 → 도메인 엔티티 흐름
            result = order_controller.handle_create_order(data)
            return jsonify(result), 201
        else:
            # ... 기존 구현은 여기에 유지 ...
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except SystemError:
        return jsonify({'error': '내부 서버 오류'}), 500