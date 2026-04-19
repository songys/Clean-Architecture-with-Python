# 관측 가능성 적용 전의 Flask 라우트 예시
# - 프레임워크(Flask)의 로깅 기능을 비즈니스 로직과 직접 결합한 안티패턴
# - app.logger는 Flask에 종속적이므로 클린 아키텍처의 의존성 규칙 위반
@app.route('/tasks/new', methods=['POST'])
def create_task():
    task = create_task_from_request(request.form)
    app.logger.info('Created task %s', task.id)  # 프레임워크 특정 로깅
    return redirect(url_for('index'))
