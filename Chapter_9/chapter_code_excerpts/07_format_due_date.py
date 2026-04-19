from datetime import datetime, timezone
from typing import Optional


# 프레젠터 내부의 날짜 포맷팅 메서드
# 도메인의 비즈니스 규칙(마감 시점)과 표시 관심사(포맷)를 분리하는 역할
def _format_due_date(self, due_date: Optional[datetime]) -> str:
    """웹 표시를 위해 마감일을 포맷한다."""
    if not due_date:
        return ""

    # UTC 기준으로 기한 초과 여부 판단 (시간대 인식 비교)
    is_overdue = due_date < datetime.now(timezone.utc)
    date_str = due_date.strftime("%Y-%m-%d")
    # 기한 초과 시 "기한 초과:" 접두사 추가 - HTML 템플릿에서 스타일링에 활용 가능
    return f"기한 초과: {date_str}" if is_overdue else date_str
