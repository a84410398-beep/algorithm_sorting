# -------------------------------------------------------------
# Google Cloud Run 배포용 멀티스테이지/경량화 Dockerfile
# Python 3.12-slim 이미지를 기반으로 빌드합니다.
# -------------------------------------------------------------
FROM python:3.12-slim

# 표준 출력/오류 버퍼링 비활성화 (Cloud Logging에 즉시 출력되도록 설정)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cloud Run 기본 포트 환경변수 설정 (Cloud Run 플랫폼에서 자동 주입)
ENV PORT=8080

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 및 패키지 설치
# 빌드 캐시 최적화를 위해 requirements.txt를 먼저 복사합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드 복사
COPY . .

# 컨테이너 포트 노출
EXPOSE 8080

# Cloud Run 권장 실행 명령:
# Cloud Run이 런타임에 주입하는 $PORT 환경변수를 동적으로 전달할 수 있도록 shell 형식으로 실행합니다.
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}


