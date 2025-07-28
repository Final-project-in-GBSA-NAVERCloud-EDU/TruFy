import torch
from transformers import pipeline
from PIL import Image
import os
import warnings

# 불필요한 경고 메시지 무시
warnings.filterwarnings('ignore')

# --- 1. 모델 로드 (스크립트 실행 시 한 번만 실행) ---

# GPU 사용 가능 여부 확인 및 설정
# pipeline은 device ID를 정수로 받습니다: -1은 CPU, 0은 첫 번째 GPU
device_id = 0 if torch.cuda.is_available() else -1
device_name = "cuda" if device_id == 0 else "cpu"
print(f"Using device: {device_name}")

print("Loading the DeepFake Detector V2 model...")
# 모델 로드 시 허깅페이스에서 파일을 다운로드하므로 시간이 걸릴 수 있습니다.
pipe = pipeline(
    'image-classification',
    model="prithivMLmods/Deep-Fake-Detector-v2-Model",
    device=device_id
)
print("Model loaded successfully.")


# --- 2. 예측 함수 (파일 경로를 입력으로 받도록 수정) ---

def predict_deepfake_from_path(image_path: str):
    """
    이미지 파일 경로를 입력받아 'fake' 또는 'real'을 예측합니다.

    Args:
        image_path (str): 분석할 이미지 파일의 경로

    Returns:
        tuple: (예측 레이블, 신뢰도 점수) 또는 에러 발생 시 (None, None)
    """
    # 파일 존재 여부 확인
    if not os.path.exists(image_path):
        print(f"Error: File not found at '{image_path}'")
        return None, None

    try:
        # PIL 라이브러리를 사용해 이미지 열기
        image = Image.open(image_path)

        # 파이프라인을 통해 예측 수행
        result = pipe(image)

        # 결과 파싱
        # 모델 레이블이 'DeepFake', 'fake', 'Real' 등 다양할 수 있어 소문자로 변환 후 확인
        label = result[0]['label'].lower()
        score = result[0]['score']

        # 'fake' 또는 'deepfake' 문자열이 포함되어 있으면 'fake'로 분류
        predicted_class = "Fake" if 'fake' in label or 'deepfake' in label else "Real"
        
        return predicted_class, score

    except Exception as e:
        print(f"An error occurred while processing the image: {e}")
        return None, None


# --- 3. 스크립트 실행 예시 ---

if __name__ == "__main__":
    # !!! 아래 파일 경로를 실제 테스트하고 싶은 이미지 경로로 변경해주세요 !!!
    # 예: test_image_path = "C:/Users/MyUser/Pictures/my_photo.jpg"
    # 예: test_image_path = "/home/user/images/test.png"

    print("\n" + "="*30)
    print("        DEEPFAKE PREDICTION")
    print("="*30)
    
    # 함수 호출 및 결과 출력
    prediction, confidence = predict_deepfake_from_path(test_image_path)

    if prediction is not None:
        print(f"\n✅ Prediction Result for '{os.path.basename(test_image_path)}'")
        print(f"   - Predicted Label:  '{prediction.upper()}'")
        print(f"   - Confidence:       {confidence:.4f}")