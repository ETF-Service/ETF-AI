FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (Chrome 및 기타 필수 패키지 포함)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    gnupg2 \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Chrome 설치 (Selenium용)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Chrome이 샌드박스 모드에서 실행되도록 환경변수 설정
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome

# 포트 노출
EXPOSE 8001

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"] 