# 안티패턴: 컨트롤러에 인터페이스별 로직이 포함됨
# 의존성 규칙 위반 사례 - 인터페이스 어댑터 계층의 컨트롤러가
# 프레임워크 계층(Click)을 직접 참조하여 특정 인터페이스에 종속됨
def handle_create(self, request_data: dict) -> dict:
    """하면 안 되는 것: 컨트롤러에 CLI 형식 혼합"""
    try:
        result = self.create_use_case.execute(request_data)
        if result.is_success:
            # 잘못됨: CLI 전용 형식은 여기에 있을 수 없음
            # click.style()은 CLI 프레임워크 전용 함수 - 웹에서 재사용 불가
            return {"message": click.style(f"Created task: {result.value.title}", fg="green")}
    except ValueError as e:
        # 잘못됨: CLI 전용 오류 형식
        # 이렇게 하면 웹 인터페이스 추가 시 컨트롤러 수정이 필요
        return {"error": click.style(str(e), fg="red")}
