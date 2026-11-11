"""
Google Cloud Run 배포용 정렬 알고리즘 시각화 백엔드 서버 (FastAPI)

주요 기능:
1. 셸 정렬, 퀵 정렬, 병합 정렬의 매 스텝별 상태 스냅샷 수집 및 일괄 반환
2. Google Apps Script(GAS) 및 웹 클라이언트의 교차 출처 요청을 위한 CORS 설정
3. Cloud Run의 PORT 환경변수 동적 지원 및 헬스 체크 엔드포인트 제공
4. 엄격한 입력 검증 및 명확한 한국어 오류 메시지 반환
"""

import os
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from algorithms.models import SortRequest, SortResponse
from algorithms.shell_sort import trace_shell_sort
from algorithms.quick_sort import trace_quick_sort
from algorithms.merge_sort import trace_merge_sort

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Sorting Visualization Backend API",
    description="셸 정렬, 퀵 정렬, 병합 정렬의 동작 원리를 매 스냅샷별로 기록하여 스트리밍 시각화를 지원하는 API 서버입니다.",
    version="1.0.0"
)

# CORS 설정: Google Apps Script 및 브라우저에서의 직접 호출을 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션 필요에 따라 도메인을 제한할 수 있습니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="서버 루트 및 상태 확인")
async def root():
    """서버 기본 가동 상태 및 사용 가능한 엔드포인트 안내를 반환합니다."""
    return {
        "status": "online",
        "service": "Sorting Visualization Server (Cloud Run Ready)",
        "supported_algorithms": ["Shell Sort (셸 정렬)", "Quick Sort (퀵 정렬)", "Merge Sort (병합 정렬)"],
        "endpoints": {
            "health_check": "GET /health",
            "sort_api": "POST /api/sort",
            "sample_api": "GET /api/sample",
            "docs": "GET /docs"
        }
    }


@app.get("/health", summary="Cloud Run 헬스체크 엔드포인트")
async def health_check():
    """컨테이너 헬스체크를 위한 경량 엔드포인트"""
    return {"status": "healthy", "code": 200}


@app.get("/api/sample", summary="샘플 정렬 데이터 조회")
async def get_sample():
    """기본 샘플 배열([38, 27, 43, 3, 9, 82, 10, 19, 50, 12])에 대한 정렬 히스토리를 반환합니다."""
    sample_arr = [38, 27, 43, 3, 9, 82, 10, 19, 50, 12]
    return process_sort_request(sample_arr)


@app.post(
    "/api/sort",
    response_model=SortResponse,
    summary="3대 정렬 알고리즘 동시 실행 및 스냅샷 생성",
    status_code=status.HTTP_200_OK
)
async def sort_array(request: SortRequest):
    """
    전달받은 정수 배열에 대해 셸 정렬, 퀵 정렬, 병합 정렬을 동시에 실행하고,
    각 알고리즘의 동작 스냅샷 히스토리 전체를 반환합니다.
    """
    arr = request.array

    # 1. 입력 유효성 정밀 검증
    if not arr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="배열이 비어 있습니다. 최소 1개 이상의 정수를 입력해 주세요."
        )

    if len(arr) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"입력 배열의 크기({len(arr)}개)가 너무 큽니다. 시각화의 가독성과 성능을 위해 50개 이하로 입력해 주세요."
        )

    for idx, item in enumerate(arr):
        if not isinstance(item, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"인덱스 {idx}의 값 '{item}'은(는) 유효한 정수가 아닙니다. 모든 원소는 정수여야 합니다."
            )

    return process_sort_request(arr)


def process_sort_request(arr: List[int]) -> SortResponse:
    """3가지 정렬 알고리즘을 각각 독립적으로 실행하여 스냅샷 히스토리를 통합 생성합니다."""
    shell_history = trace_shell_sort(arr)
    quick_history = trace_quick_sort(arr)
    merge_history = trace_merge_sort(arr)

    # 타임라인 통합 기준 최대 스텝 수 계산
    max_steps = max(
        shell_history.total_steps,
        quick_history.total_steps,
        merge_history.total_steps
    )

    return SortResponse(
        original_array=arr,
        sorted_array=sorted(arr),
        max_steps=max_steps,
        shell_sort=shell_history,
        quick_sort=quick_history,
        merge_sort=merge_history
    )


if __name__ == "__main__":
    import uvicorn
    # Cloud Run 환경변수 PORT(기본값 8080)를 감지하여 실행
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)


