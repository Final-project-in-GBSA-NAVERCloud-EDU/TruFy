# worker_project/worker_api.py
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import os
import time
from ncp_object import download_from_ncp # ncp_object.py에서 다운로드 함수 가져오기
import sys
from predict import predict_deepfake_from_path as model

app = FastAPI()

# 다운로드 받을 임시 폴더 생성
os.makedirs("temp_files", exist_ok=True)

class FileInfo(BaseModel):
    """중개 서버로부터 받을 파일 정보 모델"""
    object_name: str # NCP에 저장된 파일 이름

def run_ai_model_on_file(file_path: str) -> dict:
    """다운로드된 파일을 가지고 AI 모델을 실행하는 함수"""
    print(f"AI 모델 실행 시작: {file_path}")
    # 여기에서 실제 AI 모델 로딩 및 추론 로직 수행
    
    predicted_label, confidence_score = model(file_path)
    result = {"model_result": predicted_label, "confidence": confidence_score}
    print(f"AI 모델 실행 완료: {file_path}")
    # 작업이 끝난 임시 파일 삭제
    os.remove(file_path)
    return result

@app.post("/process-object/")
async def process_object(file_info: FileInfo):
    """파일 이름을 받아서 NCP에서 다운로드 후 AI 모델을 실행"""
    object_name = file_info.object_name
    download_path = os.path.join("temp_files", object_name)

    # 1. NCP Object Storage에서 파일 다운로드
    if not download_from_ncp(object_name, download_path):
        return {"error": "NCP에서 파일 다운로드 실패"}

    # 2. 다운로드된 파일로 AI 모델 실행
    model_result = run_ai_model_on_file(download_path)

    return {
        "message": "AI 모델 처리가 성공적으로 완료되었습니다!",
        "source_object": object_name,
        **model_result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)