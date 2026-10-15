from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# 버블 정렬 알고리즘 수행 및 각 단계별 상태(Steps) 추적 함수
def bubble_sort_with_steps(arr):
    """
    버블 정렬을 수행하면서 알고리즘의 모든 중간 상태(비교, 교환, 정렬 완료 영역)를 기록하여 반환합니다.
    시간 복잡도: 평균/최악 O(n²), 최선 O(n)
    공간 복잡도: O(1) (추가 메모리 최소화)
    """
    steps = []
    data = list(arr)
    n = len(data)
    
    # 초기 상태 기록
    steps.append({
        "array": list(data),
        "comparing": [],
        "sortedIndex": [],
        "message": "초기 데이터 배열 생성 완료"
    })

    # 버블 정렬 메인 로직
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # 현재 비교 중인 인덱스 기록
            steps.append({
                "array": list(data),
                "comparing": [j, j + 1],
                "sortedIndex": [n - 1 - k for k in range(i)],
                "message": f"{data[j]}와 {data[j+1]} 비교 중"
            })

            if data[j] > data[j + 1]:
                # 원소 교환 (Swap)
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
                steps.append({
                    "array": list(data),
                    "comparing": [j, j + 1],
                    "sortedIndex": [n - 1 - k for k in range(i)],
                    "message": f"조건 충족으로 위치 교환: {data[j+1]} ↔ {data[j]}"
                })
        
        # 한 패스가 끝날 때마다 맨 뒤 원소는 정렬 완료됨
        steps.append({
            "array": list(data),
            "comparing": [],
            "sortedIndex": [n - 1 - k for k in range(i + 1)],
            "message": f"뒤에서 {i+1}번째 원소 정렬 완료"
        })

        # 최적화: 교환이 일어나지 않았다면 이미 정렬된 상태이므로 조기 종료 가능
        if not swapped and i == 0:
            steps.append({
                "array": list(data),
                "comparing": [],
                "sortedIndex": list(range(n)),
                "message": "배열이 이미 정렬되어 있어 조기 완료되었습니다 (최선 복잡도 O(n))"
            })
            break

    return steps, data

@app.route("/", methods=["POST", "GET"])
def handle_bubble_sort():
    """
    Google Cloud Run에 배포되는 웹훅 엔드포인트입니다.
    POST 요청으로 배열 데이터를 전달받아 버블 정렬 단계별 결과를 JSON으로 반환합니다.
    """
    if request.method == "GET":
        return jsonify({
            "status": "active",
            "message": "Google Cloud Run Bubble Sort API is running smoothly."
        }), 200

    try:
        req_data = request.get_json(silent=True) or {}
        numbers = req_data.get("numbers", [64, 34, 25, 12, 22, 11, 90])
        
        # 숫자가 아닌 값이 포함된 경우 예외 처리
        numbers = [int(x) for x in numbers]

        steps, sorted_result = bubble_sort_with_steps(numbers)

        return jsonify({
            "status": "success",
            "backend": "Google Cloud Run (Python Flask)",
            "steps": steps,
            "sorted": sorted_result,
            "complexity": {
                "time_best": "O(n)",
                "time_worst": "O(n^2)",
                "space": "O(1)"
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == "__main__":
    # Cloud Run은 PORT 환경 변수를 통해 포트를 바인딩합니다.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
