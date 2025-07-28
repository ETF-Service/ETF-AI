# 🔗 GitHub → Google Cloud Run 자동 배포 설정

## 📋 사전 준비

### 1. Google Cloud SDK 설치 및 인증

```bash
# Google Cloud SDK 설치 (Mac)
brew install google-cloud-sdk

# 또는 다른 OS: https://cloud.google.com/sdk/docs/install

# 인증
gcloud auth login
gcloud auth application-default login
```

### 2. Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (예: `etf-ai-project`)
3. 결제 계정 연결 ($300 무료 크레딧 활용)

## 🚀 자동 설정 스크립트 실행

```bash
# ETF_AI 폴더에서 실행
cd ETF_AI
chmod +x setup-gcp.sh
./setup-gcp.sh
```

이 스크립트가 다음을 자동으로 수행합니다:
- 필요한 Google Cloud API 활성화
- Cloud Build 서비스 계정 권한 설정
- Cloud Run 배포 권한 부여

## 🔧 Cloud Build Triggers 설정

### 1. Google Cloud Console 접속

스크립트 실행 후 출력된 URL로 접속하거나:
`https://console.cloud.google.com/cloud-build/triggers`

### 2. GitHub 저장소 연결

1. **"트리거 만들기"** 클릭
2. **소스 선택**: `GitHub (Cloud Build GitHub 앱)` 선택
3. **저장소 연결**: 
   - "GitHub 앱 설치" 클릭
   - GitHub 계정 인증
   - 저장소 액세스 권한 부여
   - ETF 프로젝트 저장소 선택

### 3. 트리거 구성

다음 설정값들을 입력하세요:

#### 기본 정보
- **이름**: `etf-ai-deploy`
- **설명**: `ETF AI 서비스 자동 배포`

#### 이벤트
- **이벤트 유형**: `저장소에 푸시`
- **소스**: 연결한 GitHub 저장소
- **브랜치**: `^main$` (main 브랜치만)

#### 필터 (중요!)
- **포함된 파일 필터**: `ETF_AI/**`
  > 이렇게 하면 ETF_AI 폴더의 파일이 변경될 때만 배포됩니다

#### 구성
- **유형**: `Cloud Build 구성 파일(yaml 또는 json)`
- **위치**: `저장소`
- **Cloud Build 구성 파일 위치**: `/ETF_AI/cloudbuild.yaml`

### 4. 고급 설정 (선택사항)

- **서비스 계정**: `기본 Cloud Build 서비스 계정` 사용
- **대체 변수**: 필요시 추가

### 5. "만들기" 클릭

## 🧪 배포 테스트

### 1. 코드 변경 및 푸시

```bash
# 테스트용 변경사항 추가
echo "# Auto deployment test" >> ETF_AI/README.md
git add .
git commit -m "Test: Cloud Build auto deployment"
git push origin main
```

### 2. 배포 상태 확인

1. **Cloud Build → 기록** 에서 빌드 진행상황 확인
2. **Cloud Run → 서비스** 에서 배포된 서비스 확인
3. 생성된 URL로 접속하여 헬스체크: `/health`

## 🎯 성공 확인

배포가 성공하면:

1. **Cloud Run 서비스 URL 확인**:
```bash
gcloud run services describe etf-ai-service --region asia-northeast3 --format "value(status.url)"
```

2. **API 테스트**:
```bash
# 헬스체크
curl https://your-service-url/health

# 루트 엔드포인트
curl https://your-service-url/
```

## 🔄 ETF_BE와 연동

Cloud Run 서비스 URL을 확인한 후, ETF_BE 프로젝트의 환경변수에 설정:

```bash
# ETF_BE 환경변수
ETF_AI_SERVICE_URL=https://your-etf-ai-service-url
```

## 📊 모니터링

### 빌드 로그 확인
- Google Cloud Console → Cloud Build → 기록
- 각 빌드의 상세 로그와 성공/실패 상태 확인

### 서비스 상태 모니터링
- Google Cloud Console → Cloud Run → etf-ai-service
- 요청 수, 응답 시간, 오류율 등 메트릭 확인

## 🛠️ 문제 해결

### 빌드 실패 시
1. Cloud Build 로그에서 오류 메시지 확인
2. `cloudbuild.yaml` 파일 문법 검사
3. 서비스 계정 권한 확인

### 배포 실패 시
1. Cloud Run 배포 로그 확인
2. Dockerfile과 requirements.txt 검증
3. 메모리/CPU 설정 조정

## 🎉 완료!

이제 ETF_AI 폴더의 코드가 변경될 때마다 자동으로 Google Cloud Run에 배포됩니다!

- ✅ GitHub 푸시 → 자동 빌드
- ✅ 자동 테스트 → 자동 배포  
- ✅ 실시간 모니터링 