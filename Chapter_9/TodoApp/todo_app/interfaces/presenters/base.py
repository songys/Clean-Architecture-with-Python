from abc import ABC, abstractmethod
from typing import Optional

from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from todo_app.interfaces.view_models.task_vm import TaskViewModel


# 프레젠터의 추상 인터페이스 - 클린 아키텍처의 인터페이스 어댑터 계층 핵심
# CLI/웹 등 각 인터페이스는 이 추상 클래스를 구현하여 출력 포맷을 결정
# 컨트롤러는 구체적 프레젠터가 아닌 이 추상 타입에만 의존 (의존성 역전 원칙)
class TaskPresenter(ABC):
    """작업 관련 출력을 위한 추상 기본 프레젠터."""

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """작업 응답을 뷰 모델로 변환한다."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """표시를 위해 오류 메시지를 포맷한다."""
        pass


# 프로젝트 전용 프레젠터 추상 인터페이스
class ProjectPresenter(ABC):
    """프로젝트 관련 출력을 위한 추상 기본 프레젠터."""

    @abstractmethod
    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:
        """프로젝트 응답을 뷰 모델로 변환한다."""
        pass

    @abstractmethod
    def present_completion(self, completion_response: CompleteProjectResponse) -> ProjectCompletionViewModel:
        """프로젝트 완료 메시지를 포맷한다."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """표시를 위해 오류 메시지를 포맷한다."""
        pass