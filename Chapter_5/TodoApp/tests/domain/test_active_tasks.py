# 활성 작업 조회 기능 테스트
# - 빈 리포지토리, 전체 활성, 혼합 상태, 전체 완료, 완료 후 변경 등 시나리오 검증

from tests.application.conftest import (
    InMemoryTaskRepository,
)
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import TaskStatus


def test_get_active_tasks_empty_repository():
    """빈 리포지토리에서 활성 작업 조회를 테스트한다."""
    repo = InMemoryTaskRepository()
    tasks = repo.get_active_tasks()
    assert len(tasks) == 0


def test_get_active_tasks_only_active():
    """모든 작업이 활성 상태일 때 활성 작업 조회를 테스트한다."""
    repo = InMemoryTaskRepository()

    # 세 개의 활성 작업 생성 및 저장
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    task3 = Task(title="Task 3", description="Test")

    repo.save(task1)
    repo.save(task2)
    repo.save(task3)

    tasks = repo.get_active_tasks()
    assert len(tasks) == 3
    assert all(task.status == TaskStatus.TODO for task in tasks)


def test_get_active_tasks_mixed_status():
    """활성 작업과 완료된 작업이 섞여 있을 때 활성 작업 조회를 테스트한다."""
    repo = InMemoryTaskRepository()

    # 서로 다른 상태의 작업 생성 및 저장
    todo_task = Task(title="Todo Task", description="Test")
    in_progress_task = Task(title="In Progress Task", description="Test")
    in_progress_task.start()  # 상태를 IN_PROGRESS로 설정
    completed_task = Task(title="Completed Task", description="Test")
    completed_task.complete()  # 상태를 DONE으로 설정

    repo.save(todo_task)
    repo.save(in_progress_task)
    repo.save(completed_task)

    tasks = repo.get_active_tasks()
    assert len(tasks) == 2  # TODO와 IN_PROGRESS 작업만 가져와야 함
    assert completed_task not in tasks
    assert all(task.status != TaskStatus.DONE for task in tasks)


def test_get_active_tasks_only_completed():
    """모든 작업이 완료 상태일 때 활성 작업 조회를 테스트한다."""
    repo = InMemoryTaskRepository()

    # 세 개의 완료된 작업 생성 및 저장
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    task3 = Task(title="Task 3", description="Test")

    for task in [task1, task2, task3]:
        task.complete()
        repo.save(task)

    tasks = repo.get_active_tasks()
    assert len(tasks) == 0


def test_get_active_tasks_after_completion():
    """일부 작업 완료 후 활성 작업 조회를 테스트한다."""
    repo = InMemoryTaskRepository()

    # 초기 작업 생성 및 저장
    task1 = Task(title="Task 1", description="Test")
    task2 = Task(title="Task 2", description="Test")
    task3 = Task(title="Task 3", description="Test")

    repo.save(task1)
    repo.save(task2)
    repo.save(task3)

    # 초기에는 모든 작업이 있어야 함
    assert len(repo.get_active_tasks()) == 3

    # 두 개의 작업 완료
    task1.complete()
    task3.complete()
    repo.save(task1)
    repo.save(task3)

    # 이제 활성 작업이 하나만 있어야 함
    active_tasks = repo.get_active_tasks()
    assert len(active_tasks) == 1
    assert task2 in active_tasks
