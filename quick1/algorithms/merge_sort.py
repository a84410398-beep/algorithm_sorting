"""
병합 정렬(Merge Sort) 알고리즘 및 상태 스냅샷 수집기

[동작 원리]
존 폰 노이만이 제안한 분할 정복(Divide and Conquer) 방식의 안정 정렬 알고리즘입니다.
배열을 크기가 1이 될 때까지 절반으로 논리적 분할한 뒤,
인접한 두 정렬된 부분 배열을 크기 순서로 비교하면서 하나의 배열로 병합합니다.

[스냅샷 기록 내용]
1. 배열이 논리적으로 분할되는 구간
2. 두 부분 배열을 병합하며 좌우 요소를 비교하는 과정
3. 임시 배열에서 정렬 완료된 후 원본 배열로 덮어씌워지는(Overwrite) 상태
4. 최종 정렬 완료 상태
"""

from typing import List, Set
from .models import Snapshot, AlgorithmHistory, ComplexityInfo


def trace_merge_sort(initial_arr: List[int]) -> AlgorithmHistory:
    """
    입력 배열에 대해 병합 정렬을 수행하면서 각 단계의 스냅샷을 수집하여 반환합니다.

    :param initial_arr: 정렬 대상 정수 배열
    :return: 병합 정렬의 메타데이터 및 스냅샷 히스토리 객체
    """
    arr = list(initial_arr)
    n = len(arr)
    snapshots: List[Snapshot] = []
    step_counter = 0
    confirmed_set: Set[int] = set()

    def add_snapshot(
        action: str,
        description: str,
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

    def merge_sort_recursive(low: int, high: int):
        if low >= high:
            return

        mid = (low + high) // 2

        # 2. 논리적 분할 스냅샷
        add_snapshot(
            action="divide",
            description=f"구간 [{low}, {high}]을(를) 좌측 [{low}, {mid}]과(와) 우측 [{mid + 1}, {high}] 구간으로 분할합니다.",
            active_range=[low, high]
        )

        merge_sort_recursive(low, mid)
        merge_sort_recursive(mid + 1, high)

        # 3. 두 부분 배열 병합 (Merge)
        add_snapshot(
            action="merging",
            description=f"정렬된 좌측 구간 [{low}, {mid}]과(와) 우측 구간 [{mid + 1}, {high}]의 병합을 시작합니다.",
            active_range=[low, high]
        )

        left_part = arr[low:mid + 1]
        right_part = arr[mid + 1:high + 1]
        temp: List[int] = []

        i = 0  # left_part 포인터
        j = 0  # right_part 포인터

        # 좌우 요소 비교하면서 작은 순서대로 temp에 적재
        while i < len(left_part) and j < len(right_part):
            actual_left_idx = low + i
            actual_right_idx = mid + 1 + j

            add_snapshot(
                action="comparing",
                description=f"좌측 인덱스 {actual_left_idx}(값: {left_part[i]})과(와) 우측 인덱스 {actual_right_idx}(값: {right_part[j]})을(를) 비교합니다.",
                comparing_indices=[actual_left_idx, actual_right_idx],
                active_range=[low, high]
            )

            # '<=' 비교로 안정 정렬(Stable Sort) 속성 유지
            if left_part[i] <= right_part[j]:
                temp.append(left_part[i])
                i += 1
            else:
                temp.append(right_part[j])
                j += 1

        while i < len(left_part):
            temp.append(left_part[i])
            i += 1

        while j < len(right_part):
            temp.append(right_part[j])
            j += 1

        # 4. 임시 배열의 정렬된 내용을 원본 배열에 순차적으로 덮어쓰기 (Overwrite)
        for idx, val in enumerate(temp):
            target_idx = low + idx
            arr[target_idx] = val

            # 마지막 최상위 병합(low==0 and high==n-1)인 경우 전체 확정 진행
            if low == 0 and high == n - 1:
                confirmed_set.add(target_idx)

            add_snapshot(
                action="overwrite",
                description=f"병합 정렬된 값 {val}을(를) 원본 배열 인덱스 {target_idx}에 덮어씁니다(Overwrite).",
                swapped_indices=[target_idx],
                active_range=[low, high]
            )

    merge_sort_recursive(0, n - 1)

    # 5. 전체 정렬 완료 스냅샷
    confirmed_set.update(range(n))
    add_snapshot(
        action="complete",
        description="병합 정렬이 성공적으로 완료되었습니다.",
        active_range=[0, n - 1],
        confirmed_indices=list(range(n))
    )

    return AlgorithmHistory(
        name_ko="병합 정렬",
        name_en="Merge Sort",
        complexity=ComplexityInfo(
            time_best="O(N log N)",
            time_avg="O(N log N)",
            time_worst="O(N log N)",
            space="O(N)",
            stable=True
        ),
        total_steps=len(snapshots),
        snapshots=snapshots
    )

