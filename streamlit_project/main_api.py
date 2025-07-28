# app_project/main_api.py
import uvicorn
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import uuid
from ncp_object import upload_to_ncp # ncp_object.py에서 업로드 함수 가져오기

app = FastAPI()
tasks_db = {}

# Worker 서버의 새 API 엔드포인트 주소
WORKER_API_URL = "http://10.0.0.6:8001/process-object/"

def upload_and_signal_worker(task_id: str, file_content: bytes, filename: str):
    """NCP에 업로드하고 Worker 서버에 신호를 보내는 백그라운드 함수"""
    # 1. NCP Object Storage에 파일 업로드
    if not upload_to_ncp(file_bytes=file_content, object_name=filename):
        tasks_db[task_id]['status'] = 'failed'
        tasks_db[task_id]['result'] = {'error': 'NCP Object Storage 업로드 실패'}
        return

    # 2. Worker 서버에 파일 이름(object_name)을 담아 처리 신호 전송
    try:
        # 파일 내용 대신 JSON 데이터 전송
        response = requests.post(WORKER_API_URL, json={"object_name": filename}, timeout=300)
        
        if response.status_code == 200:
            tasks_db[task_id]['status'] = 'completed'
            tasks_db[task_id]['result'] = response.json()
        else:
            tasks_db[task_id]['status'] = 'failed'
            tasks_db[task_id]['result'] = {'error': f"Worker 서버 오류: {response.text}"}
    except Exception as e:
        tasks_db[task_id]['status'] = 'failed'
        tasks_db[task_id]['result'] = {'error': str(e)}

@app.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Streamlit에서 파일을 받아 백그라운드 작업을 시작"""
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {"status": "processing", "result": None}
    file_content = await file.read()
    background_tasks.add_task(upload_and_signal_worker, task_id, file_content, file.filename)
    return {"task_id": task_id, "message": "파일 업로드 성공. 처리를 시작합니다."}

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """작업 상태 확인 API"""
    task = tasks_db.get(task_id)
    if not task:
        return JSONResponse(status_code=404, content={"status": "not_found"})
    return task

#######################YOUTUBE API################################
from fastapi import FastAPI, HTTPException, Query
import httpx
 
# app = FastAPI()
 
YOUTUBE_API_KEY = ""  # 여기에 본인의 YouTube API 키를 넣어주세요
 
@app.get("/tubef") #영상 검색
async def search_youtube_videos(search: str = Query(..., title="Search Term")):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"
 
    search_params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": search,
        "type": "video",
        "maxResults": 10,
    }
 
    async with httpx.AsyncClient() as client:
        search_response = await client.get(search_url, params=search_params)
        search_data = search_response.json()
 
        if "items" in search_data:
            video_ids = ",".join([item["id"]["videoId"] for item in search_data["items"]])
 
            video_params = {
                "key": YOUTUBE_API_KEY,
                "part": "snippet,statistics",
                "id": video_ids,
            }
 
            video_response = await client.get(video_url, params=video_params)
            video_data = video_response.json()
 
            if "items" in video_data:
                videos = []
                for item in video_data["items"]:
                    video = {
                        "title": item["snippet"]["title"],
                        "video_id": item["id"],
                        "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                        "view_count": int(item["statistics"]["viewCount"])
                    }
                    videos.append(video)
                return {"videos": videos}
            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve video details from YouTube")
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve search results from YouTube")
 
 
@app.get("/trending") #오늘의 인기 영
async def get_trending_videos():
    base_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet,statistics",  # statistics 부분 추가
        "chart": "mostPopular",
        "regionCode": "KR",
        "maxResults": 10,
    }
 
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        data = response.json()
 
    if "items" in data:
        videos = []
        for item in data["items"]:
            video_url = f"https://www.youtube.com/watch?v={item['id']}"
            video = {
                "title": item["snippet"]["title"],
                "video_url": video_url,
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
                "view_count": int(item["statistics"]["viewCount"])  # 조회수 정보 추가
            }
            videos.append(video)
        return {"videos": videos}
    else:
        raise HTTPException(status_code=500, detail="Failed to retrieve YouTube data")





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)