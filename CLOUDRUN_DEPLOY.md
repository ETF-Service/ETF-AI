# ☁️ Google Cloud Run 배포 가이드

## 📋 사전 준비

### 1. Google Cloud 계정 및 프로젝트 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (예: `etf-ai-project`)
3. 결제 계정 연결 (신용카드 필요, 무료 크레딧 $300 제공)

### 2. 필요한 API 활성화

```bash
# Cloud SDK 설치 후 실행
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 필요한 API 활성화
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## 🚀 배포 방법

### 방법 1: Cloud Build 자동 배포 (추천)

```bash
# 프로젝트 루트에서 실행
cd ETF_AI

# Cloud Build로 배포
gcloud builds submit --config cloudbuild.yaml .
```

### 방법 2: 로컬에서 수동 배포

```bash
# Docker 이미지 빌드
docker build -f Dockerfile.cloudrun -t gcr.io/YOUR_PROJECT_ID/etf-ai-service .

# Container Registry에 푸시
docker push gcr.io/YOUR_PROJECT_ID/etf-ai-service

# Cloud Run에 배포
gcloud run deploy etf-ai-service \
  --image gcr.io/YOUR_PROJECT_ID/etf-ai-service \
  --region asia-northeast3 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 3600 \
  --concurrency 100
```

## ⚙️ 환경변수 설정

Cloud Run 서비스 배포 후:

1. Google Cloud Console → Cloud Run → 서비스 선택
2. "편집 및 새 버전 배포" 클릭
3. "변수 및 보안 비밀" 탭에서 환경변수 추가:

```
# 예시 환경변수
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## 🔧 서비스 확인

### 배포 후 테스트

```bash
# 서비스 URL 확인
gcloud run services describe etf-ai-service --region asia-northeast3

# 헬스체크
curl https://your-service-url/health

# API 테스트
curl -X POST https://your-service-url/persona \
  -H "Content-Type: application/json" \
  -d '{"name": "테스트", "invest_type": 5, "interest": ["SPY"]}'
```

## 💰 비용 관리

### 무료 할당량
- **요청**: 200만 요청/월
- **CPU 시간**: 180,000 vCPU-초/월
- **메모리**: 360,000 GiB-초/월
- **네트워크**: 1GB 아웃바운드/월

### 비용 최적화 팁
- **콜드 스타트 최소화**: 요청 빈도가 높으면 자동으로 인스턴스 유지
- **동시성 설정**: `--concurrency 100` (기본값)으로 효율적인 리소스 사용
- **메모리 최적화**: 필요에 따라 메모리 조정 (512MB~4GB)

## 🔄 ETF_BE와 연동

### ETF_BE 환경변수 설정

Cloud Run 배포 완료 후, ETF_BE에서 다음 환경변수 설정:

```bash
# ETF_BE 환경변수
ETF_AI_SERVICE_URL=https://your-etf-ai-service-url
```

### 인증 설정 (선택사항)

보안이 필요한 경우:

```bash
# 인증 필요로 배포
gcloud run deploy etf-ai-service \
  --no-allow-unauthenticated \
  # ... 기타 옵션

# 서비스 계정 생성 및 권한 부여
gcloud iam service-accounts create etf-backend
gcloud run services add-iam-policy-binding etf-ai-service \
  --member="serviceAccount:etf-backend@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

## 📊 모니터링 및 로그

### Cloud Logging 확인

```bash
# 실시간 로그 확인
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=etf-ai-service"
```

### Cloud Monitoring

- Google Cloud Console → Monitoring
- 대시보드에서 요청 수, 응답 시간, 오류율 확인

## 🛠️ 업데이트 배포

코드 변경 후:

```bash
# Cloud Build로 재배포
gcloud builds submit --config cloudbuild.yaml .
```

## ⚠️ 주의사항

1. **콜드 스타트**: 첫 요청 시 지연 발생 가능 (1-3초)
2. **타임아웃**: 기본 300초, 최대 3600초
3. **파일 시스템**: 읽기 전용 (임시 파일은 /tmp 사용)
4. **상태 저장**: 상태 비저장 설계 필요

## 🔧 문제 해결

### 배포 실패
- Cloud Build 로그 확인
- Dockerfile.cloudrun 문법 확인
- 의존성 버전 호환성 확인

### 메모리 부족
- 메모리 할당량 증가 (`--memory 4Gi`)
- sentence-transformers 모델 최적화

### 응답 속도 개선
- 동시성 조정 (`--concurrency`)
- 인스턴스 수 조정 (`--max-instances`)

이제 Google Cloud Run으로 안정적인 배포가 가능합니다! 