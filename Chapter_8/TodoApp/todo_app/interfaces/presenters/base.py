from abc import ABC, abstractmethod
from typing import Optional

from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from todo_app.interfaces.view_models.task_vm import TaskViewModel

# 프레젠터 추상 인터페이스: DTO를 뷰 모델로 변환하는 역할 정의
# CLI, 웹 등 다양한 인터페이스별로 구체 구현체를 제공하는 구조
# 테스트 시 Mock(spec=TaskPresenter)로 대체하여 컨트롤러 테스트 가능
class TaskPresenter(ABC):
    """작업 관련 출력을 위한 추상 기본 프레젠터."""

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """작업 응답을 뷰 모델로 변환한다."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """오류 메시지를 표시용으로 포맷팅한다."""
        pass

class ProjectPresenter(ABC):
    """프로젝트 관련 출력을 위한 추상 기본 프레젠터."""

    @abstractmethod
    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:
        """프로젝트 응답을 뷰 모델로 변환한다."""
        pass

    @abstractmethod
    def present_completion(self, completion_response: CompleteProjectResponse) -> ProjectCompletionViewModel:
        """프로젝트 완료 메시지를 포맷팅한다."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """오류 메시지를 표시용으로 포맷팅한다."""
        pass