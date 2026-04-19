# OperationResult를 사용하는 CLI 애플리케이션의 의사 코드 예제
# - 컨트롤러가 반환한 OperationResult를 통해 성공/실패를 분기 처리하는 흐름
# - CLI는 뷰 모델의 이미 형식화된 필드를 그대로 출력하기만 하면 됨 (험블 뷰 패턴)

# 컨트롤러의 handle_create를 호출하여 OperationResult를 받음
result = app.task_controller.handle_create(title, description)

if result.is_success:  # 성공 여부 확인

    task = result.success  # 성공 값(TaskViewModel)을 꺼냄

    # 뷰 모델의 미리 형식화된 필드를 그대로 출력 (추가 로직 불필요)
    print(f"{task.status_display} [{task.priority_display}] {task.title}")

    return 0  # 정상 종료 코드

# 실패 시 오류 메시지를 빨간색으로 표준 오류 출력에 표시
print(result.error.message, fg='red', err=True)

    return 1  # 오류 종료 코드