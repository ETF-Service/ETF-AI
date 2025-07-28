#!/bin/bash

# Google Cloud 프로젝트 설정 스크립트

echo "🚀 Google Cloud 프로젝트 설정 시작..."

# 프로젝트 ID 입력 받기
read -p "Google Cloud 프로젝트 ID를 입력하세요: " PROJECT_ID

# 프로젝트 설정
gcloud config set project $PROJECT_ID

echo "📦 필요한 API 활성화 중..."

# 필요한 API들 활성화
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sourcerepo.googleapis.com

echo "🔑 Cloud Build 서비스 계정 권한 설정..."

# Cloud Build 서비스 계정에 Cloud Run 권한 부여
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

echo "✅ 설정 완료!"
echo "이제 Google Cloud Console에서 Cloud Build Triggers를 설정하세요."
echo "Console URL: https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID" 