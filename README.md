🧠 Deepfake Detection Web Service

📌 프로젝트 개요

AI 기반의 딥페이크 탐지 모델을 활용하여 웹에서 실시간으로 이미지/영상을 분석하고 딥페이크 여부를 판별하는 서비스입니다. 
Hugging Face에서 제공하는 사전학습 모델을 사용하고, Streamlit을 통해 직관적인 웹 인터페이스를 제공합니다.

🗂️ 시스템 구성
1. AI/모델 서빙 파트
딥러닝 프레임워크: PyTorch 기반

모델: Hugging Face transformers 라이브러리 사용

서빙 방식: FastAPI 기반 RESTful API로 모델 서빙


2. 서버 스펙 (Naver Cloud High CPU):

vCPU: 4 Core RAM: 32GB

vCPU: 32 Core RAM: 64GB


3. 웹 애플리케이션 (Streamlit 기반)

프레임워크: Streamlit

기능:
사용자가 이미지 업로드

결과 시각화 (딥페이크 여부 등)


백엔드 연동: FastAPI와 연동하여 모델 예측값 수신



✅ 개발 순서 및 주요 구현 포인트
Streamlit 기반 UI 개발

Naver Storage와의 연동 방법 구현

모델 서비스

Hugging Face에서 모델 다운로드 및 API화

FastAPI로 RESTful 서버 구성

CPU 환경에 맞는 모델 최적화

DB 구성 및 연동

결과 및 로그 저장용 데이터베이스 설계

Streamlit 및 FastAPI와 연동


🛠 기술 스택

구성 요소	기술

AI Framework	PyTorch, Transformers

API 서버	FastAPI

웹 프론트/백엔드	Streamlit

스토리지	Naver Object Storage

DB	MySQL
