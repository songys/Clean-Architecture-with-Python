# === mypy를 사용한 정적 타입 검사 시연 ===
# mypy는 파이썬 코드를 실행하지 않고 타입 오류를 찾아내는 정적 분석 도구
# 클린 아키텍처에서 계층 간 인터페이스의 타입 안전성 보장에 필수적

# 사용자 ID(int)를 받아 사용자 정보 딕셔너리를 반환하는 함수
def get_user(user_id: int) -> dict:
    # 사용자 조회 시뮬레이션
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


# 사용자 딕셔너리와 제목 문자열을 받아 이메일을 전송하는 함수
def send_email(user: dict, subject: str) -> None:
    print(f"Sending email to {user['email']} with subject: {subject}")


# 사용법 — 의도적 타입 오류 포함
# get_user()는 int를 기대하지만 str "123"을 전달 — mypy가 이 오류를 탐지
user = get_user("123")
send_email(user, "Welcome!")

"""
mypy Chapter_3/08_type_hinting_mypy_cli.py
Chapter_3/08_type_hinting_mypy_cli.py:11: error: Argument 1 to "get_user" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
"""
