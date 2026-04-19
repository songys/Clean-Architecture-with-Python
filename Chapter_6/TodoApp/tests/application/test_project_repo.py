from uuid import UUID

import pytest

from todo_app.infrastructure.persistence.memory import InMemoryProjectRepository
from todo_app.domain.entities.project import Project
from todo_app.domain.exceptions import ProjectNotFoundError



def test_project_repository_delete():
    """리포지토리에서 프로젝트 삭제 테스트"""
    repo = InMemoryProjectRepository()
    project = Project(name="Test Project")
    repo.save(project)

    # 프로젝트가 존재하는지 확인
    assert repo.get(project.id) == project

    # 프로젝트 삭제
    repo.delete(project.id)

    # 프로젝트가 삭제되었는지 확인
    with pytest.raises(ProjectNotFoundError):
        repo.get(project.id)


def test_project_repository_delete_nonexistent():
    """존재하지 않는 프로젝트 삭제 테스트"""
    repo = InMemoryProjectRepository()
    random_id = UUID("123e4567-e89b-12d3-a456-426614174000")

    # 존재하지 않는 프로젝트를 삭제할 때 오류가 발생하지 않아야 함
    repo.delete(random_id)


def test_project_repository_delete_and_recreate():
    """프로젝트를 삭제한 후 같은 이름으로 새 프로젝트 생성 테스트"""
    repo = InMemoryProjectRepository()

    # 첫 번째 프로젝트 생성 및 삭제
    project1 = Project(name="Test Project")
    repo.save(project1)
    repo.delete(project1.id)

    # 같은 이름으로 두 번째 프로젝트 생성
    project2 = Project(name="Test Project")
    repo.save(project2)

    # 새 프로젝트가 존재하고 다른 ID를 가지는지 확인
    saved_project = repo.get(project2.id)
    assert saved_project == project2
    assert saved_project.id != project1.id
