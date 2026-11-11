"""
퀵 정렬(Quick Sort) 알고리즘 및 상태 스냅샷 수집기

[동작 원리]
분할 정복(Divide and Conquer) 알고리즘으로, 하나의 피벗(Pivot) 요소를 정하고,
피벗보다 작은 요소는 피벗의 왼쪽으로, 큰 요소는 피벗의 오른쪽으로 분할한 뒤,
각각의 부분 배열에 대해 재귀적으로 같은 정렬 과정을 반복합니다.

[스냅샷 기록 내용]
1. 피벗(Pivot) 지정
2. 피벗과의 대소 비교 대상 요소
3. 피벗보다 작은 요소를 앞으로 보내기 위한 요소 교환 위치
4. 피벗의 최종 정렬 확정 상태 (피벗의 위치가 결정되어 고정됨)
5. 전체 정렬 완료 상태
"""

from typing import List, Set
from .models import Snapshot, AlgorithmHistory, ComplexityInfo


def trace_quick_sort(initial_arr: List[int]) -> AlgorithmHistory:
    """
    입력 배열에 대해 퀵 정렬을 수행하면서 각 단계의 스냅샷을 수집하여 반환합니다.
    (Lomuto 분할 방식을 기반으로 하여 단계별 변화가 직관적으로 추적됩니다)

    :param initial_arr: 정렬 대상 정수 배열
    :return: 퀵 정렬의 메타데이터 및 스냅샷 히스토리 객체
    """
    arr = list(initial_arr)
    n = len(arr)
    snapshots: List[Snapshot] = []
    step_counter = 0
    confirmed_set: Set[int] = set()

    def add_snapshot(
        action: str,
        description: str,
        pivot_indices: List[int] = None,
        comparing_indices: List[int] = None,
        swapped_indices: List[int] = None,
        active_range: List[int] = None,
        confirmed_indices: List[int] = None
    ):
        nonlocal step_counter
        snapshots.append(
            Snapshot(
                step=step_counter,
                array=list(arr),
                action=action,
                description=description,
                pivot_indices=pivot_indices or [],
                comparing_indices=comparing_indices or [],
                swapped_indices=swapped_indices or [],
                active_range=active_range or [],
                confirmed_indices=confirmed_indices if confirmed_indices is not None else sorted(list(confirmed_set))
            )
        )
        step_counter += 1

    # 1. 초기 상태 스냅샷 기록
    add_snapshot(
        action="init",
        description=f"초기 배열 상태입니다. 원소 개수: {n}개"
    )

    def quick_sort_recursive(low: int, high: int):
        if low > high:
            return

        if low == high:
            # 원소가 1개인 구간은 자동으로 위치 확정
            confirmed_set.add(low)
            add_snapshot(
                action="pivot_fixed",
                description=f"인덱스 {low}(값: {arr[low]})은 원소가 1개이므로 정렬 확정되었습니다.",
                confirmed_indices=sorted(list(confirmed_set)),
                active_range=[low, high]
            )
            return

        # 2. 피벗 선택 (구간의 가장 오른쪽 원소 선택)
        pivot_val = arr[high]
        add_snapshot(
            action="pivot_select",
            description=f"구간 [{low}, {high}]에서 피벗으로 인덱스 {high}(값: {pivot_val})을(를) 선택합니다.",
            pivot_indices=[high],
            active_range=[low, high]
        )

        i = low - 1  # 피벗보다 작은 요소들의 마지막 경계 인덱스

        # 3. 구간 순회하며 피벗과 대소 비교
        for j in range(low, high):
            add_snapshot(
                action="comparing",
                description=f"인덱스 {j}(값: {arr[j]})을(를) 피벗(값: {pivot_val})과 비교합니다.",
                pivot_indices=[high],
                comparing_indices=[j, high],
                active_range=[low, high]
            )

            if arr[j] <= pivot_val:
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    add_snapshot(
                        action="swapped",
                        description=f"피벗({pivot_val}) 이하인 값 {arr[i]}을(를) 왼쪽(인덱스 {i})으로 이동하기 위해 인덱스 {j}와 교환합니다.",
                        pivot_indices=[high],
                        swapped_indices=[i, j],
                        active_range=[low, high]
                    )

        # 4. 피벗을 올바른 분할 위치(i + 1)로 배치
        pivot_final_idx = i + 1
        arr[pivot_final_idx], arr[high] = arr[high], arr[pivot_final_idx]
        confirmed_set.add(pivot_final_idx)

        add_snapshot(
            action="pivot_fixed",
            description=f"피벗(값: {arr[pivot_final_idx]})이(가) 최종 정렬 위치인 인덱스 {pivot_final_idx}에 확정되었습니다.",
            pivot_indices=[pivot_final_idx],
            swapped_indices=[pivot_final_idx, high] if pivot_final_idx != high else [pivot_final_idx],
            active_range=[low, high]
        )

        # 5. 좌측 및 우측 부분 배열 재귀 정렬
        quick_sort_recursive(low, pivot_final_idx - 1)
        quick_sort_recursive(pivot_final_idx + 1, high)

    quick_sort_recursive(0, n - 1)

    # 6. 전체 정렬 완료 스냅샷
    confirmed_set.update(range(n))
    add_snapshot(
        action="complete",
        description="퀵 정렬이 성공적으로 완료되었습니다.",
        active_range=[0, n - 1]
    )

    return AlgorithmHistory(
        name_ko="퀵 정렬",
        name_en="Quick Sort",
        complexity=ComplexityInfo(
            time_best="O(N log N)",
            time_avg="O(N log N)",
            time_worst="O(N^2)",
            space="O(log N)",
            stable=False
        ),
        total_steps=len(snapshots),
        snapshots=snapshots
    )
