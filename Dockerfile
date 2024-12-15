#FROM python:3.11-slim
#
## 시스템 패키지 설치를 위해 root 권한으로 실행
#RUN apt-get update && apt-get install -y \
#    libportaudio2 \
#    # 필요한 다른 시스템 라이브러리가 있다면 여기에 추가
#    && rm -rf /var/lib/apt/lists/*
#
#WORKDIR /app
#
#COPY requirements.txt ./
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
#CMD [ "python", "run.py" ]

# 빌드 스테이지
FROM python:3.11-slim as builder

# 빌드에 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libportaudio2 \
    build-essential \
    # 필요한 다른 빌드 의존성이 있다면 여기에 추가
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
    # 런타임에 필요한 다른 라이브러리가 있다면 여기에 추가
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 빌드 스테이지에서 생성된 가상환경 복사
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 애플리케이션 파일 복사
COPY . .

CMD ["python", "run.py"]