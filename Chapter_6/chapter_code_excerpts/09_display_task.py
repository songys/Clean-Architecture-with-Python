# "험블 뷰(Humble View)": 로직이 거의 없고 단순하지만 테스트하기는 어려움
# - 모든 형식화 결정(상태, 우선순위, 날짜 표시 방식)은 프레젠터가 담당
# - 뷰는 이미 형식화된 뷰 모델의 필드를 그대로 출력하기만 하는 역할
# - 비즈니스 로직과 표시 로직의 분리를 통해 프레젠테이션 로직만 독립적으로 테스트 가능


def display_task(task_vm: TaskViewModel):
    # 뷰 모델에서 이미 형식화된 상태/우선순위/제목을 그대로 출력
    print(f"{task_vm.status_display} [{task_vm.priority_display}] {task_vm.title}")

    if task_vm.due_date_display:
        # 마감일 정보도 뷰 모델에서 이미 형식화되어 있음
        print(f"Due: {task_vm.due_date_display}")
