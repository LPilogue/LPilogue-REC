# 빌드 스테이지
FROM python:3.11-slim as builder

# 빌드에 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 가상환경 생성
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 실행 스테이지
FROM python:3.11-slim

# 런타임에 필요한 시스템 라이브러리만 설치
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드 스테이지에서 생성된 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 애플리케이션 코드 복사
COPY . .

# Flask 환경 설정
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# 포트 설정
EXPOSE 5000

# 애플리케이션 실행
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]