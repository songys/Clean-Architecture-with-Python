# 안티 예제: 프레임워크에 강하게 결합된 컨트롤러
# - FastAPI의 Request, JSONResponse 등 프레임워크 전용 타입에 직접 의존
# - 이 컨트롤러를 CLI나 다른 프레임워크에서 재사용 불가

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse


# 프레임워크 종속적인 컨트롤러의 안티패턴
# - 클린 아키텍처 위반: 인터페이스 어댑터가 특정 프레임워크에 직접 의존
class WebTaskController:

    def __init__(self, app: FastAPI):

        # 컨트롤러가 FastAPI에 직접 의존 - 프레임워크 교체 시 컨트롤러 전체 수정 필요
        self.app = app
        # 유스 케이스를 직접 생성하여 강한 결합이 발생 - 테스트 시 모의 객체로 교체 불가
        self.create_use_case = CreateTaskUseCase()

    # FastAPI의 Request 타입에 직접 의존하는 비동기 핸들러
    async def handle_create(self, request: Request):

        try:
            # 프레임워크 전용 방식으로 입력을 받음 - 다른 환경에서 재사용 불가
            data = await request.json()
            result = self.create_use_case.execute(data)

            # 프레임워크 전용 응답 형식 사용 - HTTP에 종속적
            return JSONResponse(status_code=201, content={"task": result})

        except ValidationError as e:
            # 프레임워크 전용 예외 처리 방식
            raise HTTPException(status_code=400, detail=str(e))
