# ==============================================================================
# Google Cloud Run 배포용 Dockerfile
# - 경량 Python 3.12 슬림 이미지 기반
# - Cloud Run 수명 주기에 맞춰 동적 PORT 환경변수 지원
# ==============================================================================
FROM python:3.12-slim

# 표준 출력/에러 버퍼링 방지 (실시간 로그 확인용)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cloud Run 기본 수신 포트 환경변수 (Cloud Run이 내부적으로 주입함)
ENV PORT=8080

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 빌드 의존성 및 curl(헬스체크용) 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치 (Docker 캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 포트 노출 (Cloud Run 표준 포트)
EXPOSE 8080

# Cloud Run 컨테이너 기동 명령:
# PORT 환경변수를 읽어 uvicorn 서버 실행 (0.0.0.0에 바인딩 필수)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]


