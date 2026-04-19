# 7장

## 장 코드 발췌
이 장의 코드 스니펫은 `chapter_code_excerpts` 폴더에 등장 순서대로 정리되어 있다. 예: `00_error_class.py`
참고용으로 제공되며 직접 실행할 수 있는 코드는 아니다.

## 작업 관리 애플리케이션

이 장에서는 프레임워크 및 드라이버 계층을 추가하여 작업 관리 애플리케이션의 클린 아키텍처 구현을 완성한다. 코드는 깔끔한 아키텍처 경계를 유지하면서 외부 프레임워크, 데이터베이스, 서비스를 통합하는 방법을 보여 준다.

## 작업 관리 애플리케이션 실행

저장소의 [README](../README.md) 섹션의 지침에 따라 환경을 설정해야 한다.

### 구성
애플리케이션은 환경 변수를 통한 구성을 지원한다:

```bash
# 리포지토리 구성 옵션
export TODO_REPOSITORY_TYPE="memory"  # 또는 "file"
export TODO_DATA_DIR="repo_data"      # TODO_REPOSITORY_TYPE에서 `file`을 선택한 경우 사용

# 선택 사항: 이메일 알림 구성
# 설정하지 않으면 기본적으로 (오프라인) NotificationRecorder를 사용
# SendGrid 알림을 설정하려면 [SendGrid 계정](https://sendgrid.com/en-us/solutions/email-api)을 만들어야 한다 (무료 요금제 사용 가능)
export TODO_SENDGRID_API_KEY="your_api_key"
export TODO_NOTIFICATION_EMAIL="recipient@example.com"
```

### 애플리케이션 실행
```bash
cd Chapter_7/TodoApp
python main.py
```

CLI 인터페이스가 실행된다.


## 애플리케이션 사용법
애플리케이션은 작업과 프로젝트를 관리하기 위한 대화형 CLI를 제공한다:

1. 숫자를 사용하여 프로젝트를 확인하고 선택 (예: "1")
2. 프로젝트.작업 형식을 사용하여 작업을 확인하고 선택 (예: "1.a")
3. "np" 명령으로 새 프로젝트 생성
4. 프로젝트 내 또는 기본 INBOX에 작업 생성
5. 작업 완료, 업데이트, 삭제
6. 프로젝트 세부 정보 편집 및 프로젝트 완료 관리

## 역자 추가 코드 예제 노트북

이 장의 코드 예제는 Jupyter 노트북(`Chapter_7_코드예제.ipynb`)으로도 제공된다. [루트 README](../README.md)의 Colab 배지를 클릭하면 바로 실행할 수 있다. 셀을 위에서 아래로 순서대로 실행한다.

- 노트북 코드는 책의 코드 발췌와 동일하되, 노트북 환경에서 실행 가능하도록 일부 수정되었다.
- 수정된 부분은 `[추가]`, `[수정]`, `[보완]` 주석으로 표시되어 있다.
- 첫 번째 코드 셀에서 `TodoApp/` 소스 코드의 경로를 설정한다.
