

FROM python:3.11-slim


WORKDIR /app



RUN apt-get update && apt-get install -y --no-install-recommends 

curl 

&& rm -rf /var/lib/apt/lists/*

requirements.txt 복사 및 파이썬 패키지 설치

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

애플리케이션 소스코드 복사

COPY . .

Cloud Run 포트 개방 (기본 8080)

ENV PORT=8080
EXPOSE 8080

Gunicorn WSGI 서버를 사용하여 고성능 비동기/멀티프로세스 구동

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "0", "main:app"]
