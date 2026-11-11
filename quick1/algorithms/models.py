"""
정렬 시각화 상태 스냅샷 및 API 요청/응답을 위한 Pydantic 데이터 모델
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Snapshot(BaseModel):
    """단일 정렬 스텝에서의 상태 스냅샷"""
    step: int = Field(..., description="스냅샷의 순차적 인덱스 (0부터 시작)")
    array: List[int] = Field(..., description="현재 시점의 배열 전체 상태 복사본")
    action: str = Field(
        ..., 
        description="동작 구분 코드 (init, gap_change, comparing, swapped, inserted, pivot_select, pivot_fixed, divide, merging, overwrite, complete)"
    )
    description: str = Field(..., description="사용자 화면에 노출할 직관적인 한국어 동작 설명")
    
    # 시각화 하이라이트 인덱스 정보
    pivot_indices: List[int] = Field(default_factory=list, description="피벗(기준점) 요소의 인덱스 목록")
    comparing_indices: List[int] = Field(default_factory=list, description="현재 비교 중인 요소들의 인덱스 목록")
    swapped_indices: List[int] = Field(default_factory=list, description="방금 교환, 삽입 또는 덮어쓰기된 요소의 인덱스 목록")
    active_range: List[int] = Field(default_factory=list, description="현재 활성화된 부분 배열 범위 [시작인덱스, 끝인덱스]")
    confirmed_indices: List[int] = Field(default_factory=list, description="정렬이 최종 확정된 요소들의 인덱스 목록")
    
    # 알고리즘 고유 보조 정보
    gap: Optional[int] = Field(None, description="셸 정렬 전용: 현재 비교 간격(Gap)")


class ComplexityInfo(BaseModel):
    """알고리즘 시간 및 공간 복잡도 정보"""
    time_best: str = Field(..., description="최선 시간 복잡도")
    time_avg: str = Field(..., description="평균 시간 복잡도")
    time_worst: str = Field(..., description="최악 시간 복잡도")
    space: str = Field(..., description="공간 복잡도")
    stable: bool = Field(..., description="안정 정렬(Stable Sort) 여부")


class AlgorithmHistory(BaseModel):
    """단일 알고리즘의 전체 실행 기록 및 메타데이터"""
    name_ko: str = Field(..., description="알고리즘 한글명 (예: 셸 정렬)")
    name_en: str = Field(..., description="알고리즘 영문명 (예: Shell Sort)")
    complexity: ComplexityInfo = Field(..., description="복잡도 정보")
    total_steps: int = Field(..., description="정렬 완료까지 소요된 총 스텝 수")
    snapshots: List[Snapshot] = Field(..., description="스냅샷 히스토리 배열")


class SortRequest(BaseModel):
    """정렬 요청 데이터 모델"""
    array: List[int] = Field(
        default=[38, 27, 43, 3, 9, 82, 10, 19, 50, 12],
        description="정렬할 정수 배열 (기본값 제공)"
    )


class SortResponse(BaseModel):
    """정렬 응답 데이터 모델 (3개 알고리즘 동시 반환)"""
    original_array: List[int] = Field(..., description="요청받은 원본 배열")
    sorted_array: List[int] = Field(..., description="최종 정렬된 결과 배열")
    max_steps: int = Field(..., description="세 알고리즘 중 가장 긴 스텝 수 (타임라인 통합 기준)")
    shell_sort: AlgorithmHistory = Field(..., description="셸 정렬 히스토리")
    quick_sort: AlgorithmHistory = Field(..., description="퀵 정렬 히스토리")
    merge_sort: AlgorithmHistory = Field(..., description="병합 정렬 히스토리")

