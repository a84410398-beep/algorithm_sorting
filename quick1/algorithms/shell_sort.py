"""
셸 정렬(Shell Sort) 알고리즘 및 상태 스냅샷 수집기

[동작 원리]
삽입 정렬의 단점(원소가 목표 위치에서 멀리 떨어져 있을 때 1칸씩 이동하여 O(N^2) 소요)을
보완하기 위해, 일정 간격(Gap)을 두고 떨어진 원소들을 묶어 대략적으로 먼저 정렬한 후,
점진적으로 간격을 좁혀가며 최종적으로 간격이 1이 되었을 때 거의 정렬된 배열에 삽입 정렬을 적용합니다.

[스냅샷 기록 내용]
1. 간격(Gap)의 크기 변화
2. 설정된 간격만큼 떨어진 요소들 간의 비교 상태
3. 큰 원소가 뒤로 밀려나는 이동 상태
4. 현재 임시 저장된 원소가 올바른 위치에 삽입되는 상태
5. 최종 정렬 완료 상태
"""

from typing import List
from .models import Snapshot, AlgorithmHistory, ComplexityInfo


def trace_shell_sort(initial_arr: List[int]) -> AlgorithmHistory:
    """
    입력 배열에 대해 셸 정렬을 수행하면서 각 단계의 스냅샷을 수집하여 반환합니다.
    
    :param initial_arr: 정렬 대상 정수 배열
    :return: 셸 정렬의 메타데이터 및 스냅샷 히스토리 객체
    """
    arr = list(initial_arr)
    n = len(arr)
    snapshots: List[Snapshot] = []
    step_counter = 0

    def add_snapshot(
        action: str,
        description: str,
        comparing_indices: List[int] = None,
        swapped_indices: List[int] = None,
        confirmed_indices: List[int] = None,
        gap: int = None
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
                confirmed_indices=confirmed_indices or [],
                gap=gap
            )
        )
        step_counter += 1

    # 1. 초기 상태 스냅샷 기록
    add_snapshot(
        action="init",
        description=f"초기 배열 상태입니다. 원소 개수: {n}개"
    )

    # 2. 간격(Gap) 설정: n // 2 에서 시작하여 매번 1/2로 줄여나감
    gap = n // 2
    while gap > 0:
        # 간격 변화 스냅샷
        add_snapshot(
            action="gap_change",
            description=f"간격(Gap)을 {gap}(으)로 설정하고 부분 정렬을 시작합니다.",
            gap=gap
        )

        # gap 간격으로 떨어진 원소들을 삽입 정렬
        for i in range(gap, n):
            temp = arr[i]
            j = i

            # 비교 시작 스냅샷
            add_snapshot(
                action="comparing",
                description=f"인덱스 {j - gap}(값: {arr[j - gap]})과 삽입 대상 인덱스 {j}(값: {temp})를 간격 {gap}으로 비교합니다.",
                comparing_indices=[j - gap, j],
                gap=gap
            )

            # 앞의 원소가 temp보다 크면 뒤로 gap만큼 이동
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                add_snapshot(
                    action="swapped",
                    description=f"{arr[j]}이(가) {temp}보다 크므로 인덱스 {j}(으)로 {gap}칸 뒤로 이동합니다.",
                    swapped_indices=[j],
                    comparing_indices=[j - gap, j],
                    gap=gap
                )
                j -= gap

                # 다음 앞선 원소와의 비교가 남아있는 경우 비교 스냅샷
                if j >= gap:
                    add_snapshot(
                        action="comparing",
                        description=f"이전 간격 위치인 인덱스 {j - gap}(값: {arr[j - gap]})과 {temp}을(를) 비교합니다.",
                        comparing_indices=[j - gap, j],
                        gap=gap
                    )

            # 적절한 위치 j에 temp 삽입
            arr[j] = temp
            add_snapshot(
                action="inserted",
                description=f"값 {temp}을(를) 정렬된 위치인 인덱스 {j}에 삽입(배치)합니다.",
                swapped_indices=[j],
                gap=gap
            )

        gap //= 2

    # 3. 전체 정렬 완료 스냅샷
    add_snapshot(
        action="complete",
        description="셸 정렬이 성공적으로 완료되었습니다.",
        confirmed_indices=list(range(n)),
        gap=0
    )

    return AlgorithmHistory(
        name_ko="셸 정렬",
        name_en="Shell Sort",
        complexity=ComplexityInfo(
            time_best="O(N log N)",
            time_avg="O(N^1.3) ~ O(N^1.5)",
            time_worst="O(N^2)",
            space="O(1)",
            stable=False
        ),
        total_steps=len(snapshots),
        snapshots=snapshots
    )

