import boto3
from datetime import datetime
from botocore.client import Config
import sys

today = datetime.today().strftime('%Y-%m-%d')

NCP_S3_ENDPOINT="https://kr.object.ncloudstorage.com"
NCP_S3_ACCESS_KEY_ID=''
NCP_S3_SECRET_ACCESS_KEY=''
NCP_S3_REGION ="kr-standard"
service_name = 's3'
bucket_name = ''
s3 = boto3.client(service_name, endpoint_url=NCP_S3_ENDPOINT, aws_access_key_id=NCP_S3_ACCESS_KEY_ID,
                        aws_secret_access_key=NCP_S3_SECRET_ACCESS_KEY)


def upload_to_ncp(file_bytes: bytes, object_name: str):
    """파일 내용(bytes)과 객체 이름을 받아 NCP Object Storage에 업로드합니다."""
    try:
        s3.put_object(Bucket=bucket_name, Key=f'{today}/{object_name}', Body=file_bytes)
        print(f"✅ NCP Object Storage 업로드 성공: {object_name}")
        return True
    except Exception as e:
        print(f"""❌ NCP Object Storage 업로드 실패: {e}
              파이썬 버전 : {sys.version}
              NCP_S3_ACCESS_KEY_ID : {NCP_S3_ACCESS_KEY_ID}
              NCP_S3_SECRET_ACCESS_KEY : {NCP_S3_SECRET_ACCESS_KEY}
              """)
        return False

def download_from_ncp(object_name: str, download_path: str):
    """NCP Object Storage에서 파일을 다운로드하여 로컬 경로에 저장합니다."""
    print(bucket_name, f'{today}/{object_name}', download_path)
    try:
        s3.download_file(bucket_name, f'{today}/{object_name}', download_path)
        print(f"✅ NCP Object Storage 다운로드 성공: {object_name} -> {download_path}")
        return True
    except Exception as e:
        print(f"❌ NCP Object Storage 다운로드 실패: {e}")
        return False
    