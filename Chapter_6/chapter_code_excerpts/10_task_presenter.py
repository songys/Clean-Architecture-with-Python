from abc import ABC, abstractmethod
from typing import Optional


# 도메인 데이터를 화면 표시용으로 변환하는 프레젠터의 추상 인터페이스
# - 도메인 응답(TaskResponse)을 뷰 모델(TaskViewModel)로 변환하는 계약 정의
# - 구체적인 구현(CLI용, 웹용 등)은 이 인터페이스를 상속하여 작성
# - 컨트롤러는 이 추상화에만 의존하므로 출력 형식 변경이 유스케이스에 영향을 주지 않음
class TaskPresenter(ABC):
    """작업(Task) 관련 출력을 담당하는 추상 프레젠터"""

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """작업 응답을 뷰 모델로 변환"""

        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """화면 표시를 위한 오류 메시지 형식화"""

        pass
