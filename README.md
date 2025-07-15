# 🧠 Deepfake Detection Web Service

AI 기반의 딥페이크 탐지 모델을 활용하여 웹에서 실시간으로 이미지/영상을 분석하고 딥페이크 여부를 판별하는 서비스입니다.  
Hugging Face에서 제공하는 사전학습 모델을 사용하고, Streamlit을 통해 직관적인 웹 인터페이스를 제공합니다.

---

## 📌 프로젝트 개요

- **프로젝트명**: Deepfake Detection Web Service
- **목표**: 이미지 또는 영상이 딥페이크인지 실시간으로 판별하는 AI 기반 웹 애플리케이션 구축
- **기술 스택**:  
  - AI Framework: `PyTorch`, `Transformers`
  - Backend API: `FastAPI`
  - Web UI: `Streamlit`
  - Storage: `Naver Object Storage`
  - Database: `Naver Cloud DB (MySQL 등)`
  - Infra: `Naver Cloud High CPU 인스턴스`

---

## 🗂️ 시스템 구성

### 1. 🧠 AI/모델 서빙

- **딥러닝 프레임워크**: PyTorch 기반
- **모델**: Hugging Face `prithivMLmods/Deep-Fake-Detector-v2-Model`  
- **서빙 방식**: FastAPI 기반 RESTful API  
- **모델 처리 흐름**:  
  - 이미지 입력 → 전처리 → 모델 추론 → 딥페이크 여부 결과 반환

### 2. ⚙️ 인퍼런스 서버 (High CPU 서버)

- **서버 환경 (Naver Cloud High CPU 인스턴스)**:
  - 선택 1: vCPU 4 Core / RAM 32GB
  - 선택 2: vCPU 32 Core / RAM 64GB
- GUI 없는 환경에서 최적화된 추론 처리

### 3. 🌐 웹 애플리케이션 (Streamlit)

- **기능**:
  - 이미지 업로드
  - 딥페이크 여부 시각화 (결과 그래프, 확률 등)
  - Archive 기능 (결과 저장 및 조회)
- **FastAPI 연동**: 모델 추론 API 호출 및 결과 수신

### 4. ☁️ 스토리지 및 데이터베이스

- **Naver Object Storage**:
  - 사용자 업로드 이미지 저장소
  - Streamlit에서 접근 가능
- **Cloud DB (MySQL 등)**:
  - 사용자 요청 기록 저장
  - 예측 결과 저장
  - 향후 통계/로그 기능 확장 가능

---

## ✅ 개발 순서 및 주요 구현 포인트

| 단계 | 구현 내용 |
|------|-----------|
| 1 | Streamlit 기반 사용자 인터페이스(UI) 개발 |
| 2 | Naver Object Storage 연동 구현 |
| 3 | Hugging Face 모델 다운로드 및 API화 |
| 4 | FastAPI를 이용한 RESTful API 서버 구축 |
| 5 | CPU 환경에 맞춘 모델 최적화 |
| 6 | 결과 저장용 데이터베이스 설계 및 연동 |
| 7 | Streamlit ↔ FastAPI 간 예측 결과 연결 |

---

## 🛠 기술 스택 요약

| 구성 요소 | 기술 |
|-----------|------|
| AI Framework | PyTorch, Transformers |
| API 서버 | FastAPI |
| 웹 프론트엔드 | Streamlit |
| 스토리지 | Naver Object Storage |
| 데이터베이스 | Naver Cloud DB (MySQL) |
| 인프라 | Naver Cloud High CPU 인스턴스 |

---

## 🚀 향후 확장 계획

| 항목 | 내용 |
|------|------|
| 📹 영상 딥페이크 판별 | 이미지뿐 아니라 영상 분석 기능 확장 |
| 📊 통계 기능 | 누적 결과 기반 사용자 대시보드 개발 |
| 🧪 성능 향상 | 모델 경량화 및 추론 속도 최적화 |
| 🔒 보안 강화 | 업로드 데이터에 대한 저장 및 접근 제어 |

---


