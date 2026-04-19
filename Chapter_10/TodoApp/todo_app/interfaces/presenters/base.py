# 프레젠터 추상 기본 클래스 모듈
# - 프레젠터: DTO(응답 데이터)를 뷰 모델(표시 데이터)로 변환하는 역할
# - 추상 클래스로 정의하여 CLI/Web 등 각 인터페이스별 구체적 구현 강제
# - 의존성 역전 원칙: 컨트롤러가 추상 프레젠터에 의존
from abc import ABC, abstractmethod
from typing import Optional

from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from todo_app.interfaces.view_models.task_vm import TaskViewModel

class TaskPresenter(ABC):
    """작업 관련 출력을 위한 추상 기본 프레젠터.
    - CLI, Web 등 각 인터페이스에서 이 클래스를 상속하여 구현
    """

    @abstractmethod
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """작업 응답을 뷰 모델로 변환한다."""
        pass

    @abstractmethod
    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """오류 메시지를 표시용으로 포맷한다."""
        pass

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
        """오류 메시지를 표시용으로 포맷한다."""
        pass
