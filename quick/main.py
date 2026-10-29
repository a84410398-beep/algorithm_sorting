"""
알고리즘 실습(정렬) - 구글 클라우드 런(Google Cloud Run) 백엔드 서버
- 프레임워크: FastAPI
- 기능: 셸 정렬, 퀵 정렬, 병합 정렬의 상태 스냅샷 히스토리 생성 및 제공
- Cloud Run 호환: PORT 환경변수(기본 8080) 수신, 헬스체크 지원, 전역 CORS 허용
"""

import os
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from algorithms import (
    get_complexity_info,
    shell_sort_with_snapshots,
    quick_sort_with_snapshots,
    merge_sort_with_snapshots
)

# FastAPI 앱 인스턴스 초기화
app = FastAPI(
    title="Algorithm Sorting Visualization API",
    description="셸 정렬, 퀵 정렬, 병합 정렬의 상태 스냅샷을 스트리밍 타임라인으로 제공하는 API 서버",
    version="1.0.0"
)

# 구글 앱스 스크립트(GAS) 및 웹 클라이언트와의 통신을 위한 CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # GAS 환경 및 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# 요청/응답 스키마 정의 (Pydantic)
# ==============================================================================
class SortRequest(BaseModel):
    numbers: List[int] = Field(
        ...,
        description="정렬할 정수 배열 (최소 3개, 최대 30개)",
        examples=[[8, 3, 5, 1, 9, 2, 7, 4]]
    )


# ==============================================================================
# 예외 핸들러 (자세한 에러 메시지 제공)
# ==============================================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 입력 유효성 검사 실패 시 친절하고 구체적인 에러 반환"""
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "유효하지 않은 입력값입니다.")
        error_details.append(f"[{field}] {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_type": "ValidationError",
            "message": "입력 데이터 형식이 올바르지 않습니다. 정수 배열을 전송해 주세요.",
            "details": error_details
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """서버 내부 예외 발생 시 상세 에러 응답 반환"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_type": type(exc).__name__,
            "message": f"서버 내부 처리 중 오류가 발생했습니다: {str(exc)}"
        }
    )


# ==============================================================================
# 공통 비즈니스 로직
# ==============================================================================
def execute_sorting_and_create_response(numbers: List[int]) -> dict:
    """주어진 배열에 대해 3가지 정렬 알고리즘을 실행하고 상태 스냅샷 히스토리를 반환합니다."""
    # 1. 입력 유효성 엄격 검증
    if not numbers or len(numbers) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="배열이 비어 있습니다. 최소 3개 이상의 정수를 입력해 주세요."
        )

    if len(numbers) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"배열 요소가 {len(numbers)}개로 너무 적습니다. 시각화를 위해 최소 3개 이상 입력해 주세요."
        )

    if len(numbers) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"배열 요소가 {len(numbers)}개로 너무 많습니다. 원활한 동시 애니메이션을 위해 30개 이하로 입력해 주세요."
        )

    # 2. 각 알고리즘별 상태 스냅샷 히스토리 생성
    shell_snapshots = shell_sort_with_snapshots(numbers)
    quick_snapshots = quick_sort_with_snapshots(numbers)
    merge_snapshots = merge_sort_with_snapshots(numbers)

    # 복잡도 메타데이터 가져오기
    complexities = get_complexity_info()

    # 단일 통합 타임라인 계산용 최대 스텝 수
    max_steps = max(len(shell_snapshots), len(quick_snapshots), len(merge_snapshots))

    return {
        "status": "success",
        "original_array": numbers,
        "sorted_array": sorted(numbers),
        "total_elements": len(numbers),
        "max_steps": max_steps,
        "algorithms": {
            "shell_sort": {
                **complexities["shell_sort"],
                "total_steps": len(shell_snapshots),
                "snapshots": shell_snapshots
            },
            "quick_sort": {
                **complexities["quick_sort"],
                "total_steps": len(quick_snapshots),
                "snapshots": quick_snapshots
            },
            "merge_sort": {
                **complexities["merge_sort"],
                "total_steps": len(merge_snapshots),
                "snapshots": merge_snapshots
            }
        }
    }


# ==============================================================================
# API 엔드포인트
# ==============================================================================
@app.get("/", summary="루트 헬스체크 및 서비스 정보")
def root():
    """서버가 정상 구동 중인지 확인하고 기본 API 정보를 제공합니다."""
    return {
        "status": "healthy",
        "service": "Algorithm Sorting Visualization Server",
        "version": "1.0.0",
        "supported_algorithms": ["shell_sort", "quick_sort", "merge_sort"],
        "endpoints": {
            "health": "/health",
            "sort_custom": "POST /api/sort",
            "sort_random": "GET /api/sort/random?size=8"
        }
    }


@app.get("/health", summary="Cloud Run 헬스체크 엔드포인트")
def health_check():
    """Google Cloud Run 수명 주기 점검용 헬스체크"""
    return {"status": "ok", "environment": "Google Cloud Run"}


@app.post("/api/sort", summary="사용자 정의 배열 정렬 스냅샷 생성")
def sort_custom_array(request_body: SortRequest):
    """
    클라이언트가 전달한 임의의 정수 배열에 대해
    셸 정렬, 퀵 정렬, 병합 정렬의 매 스텝 스냅샷을 계산하여 반환합니다.
    """
    return execute_sorting_and_create_response(request_body.numbers)


@app.get("/api/sort/random", summary="랜덤 배열 자동 생성 및 정렬 스냅샷 반환")
def sort_random_array(size: int = 8):
    """
    지정된 크기(기본 8, 5~20)의 랜덤 정수 배열을 생성하여
    세 정렬 알고리즘의 상태 스냅샷을 반환합니다.
    """
    if size < 3 or size > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="size 파라미터는 3 이상 30 이하의 값이어야 합니다."
        )

    # 10부터 99까지의 중복 없는 랜덤 정수 생성
    numbers = random.sample(range(10, 100), size)
    return execute_sorting_and_create_response(numbers)


# ==============================================================================
# 로컬 개발 및 Cloud Run 구동 진입점
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    # Cloud Run은 환경 변수 PORT를 통해 포트 번호를 주입합니다 (기본값 8080)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


