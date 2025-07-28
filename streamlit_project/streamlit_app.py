# streamlit run <filename>.py

import streamlit as st
import io
from PIL import Image
import logging
import uuid
import requests
import time
import base64
import json
from datetime import datetime


# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="Aegis: AI Deepfake Verifier",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 서버 및 API 설정 ---
BROKER_API_URL = "http://127.0.0.1:8000"
CLOVA_API_URL = "https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005"
CLOVA_API_KEY = "" 
CLOVA_API_GATEWAY_KEY = "" 

# --- 세션 상태 초기화 ---
def init_session_state():
    """세션 상태 변수들을 초기화합니다."""
    keys = ['task_id', 'reports', 'clova_result', 'original_result', 'upload_key']
    for key in keys:
        if key not in st.session_state:
            st.session_state[key] = None if key != 'reports' else []
    if 'upload_key' not in st.session_state or st.session_state.upload_key is None:
        st.session_state.upload_key = str(uuid.uuid4())


# --- 스타일링(CSS) ---
def load_css():
    """커스텀 CSS를 로드하여 앱의 디자인을 개선합니다."""
    st.markdown("""
        <style>
            /* 전체적인 폰트 및 배경색 설정 */
            html, body, [class*="st-"] {
                font-family: 'Noto Sans KR', sans-serif;
            }
            /* 메인 컨텐츠 영역 패딩 조정 */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            /* 사이드바 스타일 */
            .st-sidebar {
                background-color: #0E1117;
            }
            /* 버튼 스타일 */
            .stButton>button {
                border-radius: 20px;
                border: 1px solid #4F8BF9;
                background-color: #4F8BF9;
                color: white;
                transition: all 0.3s;
            }
            .stButton>button:hover {
                border: 1px solid #4F8BF9;
                background-color: transparent;
                color: #4F8BF9;
            }
            /* 컨테이너 스타일 */
            .st-emotion-cache-1r6slb0 { /* st.container에 해당하는 클래스 */
                border: 1px solid #262730;
                border-radius: 10px;
                padding: 2rem !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            /* 업로더 스타일 */
            .st-emotion-cache-1gulkj5 { /* st.file_uploader에 해당하는 클래스 */
                border-radius: 10px;
            }
            /* Expander 스타일 */
            .st-expander {
                border-radius: 10px !important;
                border: 1px solid #262730 !important;
            }
        </style>
    """, unsafe_allow_html=True)


# --- API 호출 함수 ---
def get_clova_analysis(img_url, orig_res):
    """HyperCLOVA X API에 분석을 요청하고 스트리밍으로 결과를 반환합니다."""
    headers = {
        'Authorization': CLOVA_API_KEY,
        'X-NCP-CLOVASTUDIO-REQUEST-ID': str(uuid.uuid4()),
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'text/event-stream'
    }
    system_text = f"""당신은 디지털 포렌식 전문가이자, 딥페이크 탐지 AI 모델입니다.

                        입력된 이미지에 대해 기술적인 딥페이크 분석을 수행하고, 주어진 [내부 모델 판별 데이터]와 교차 검증하여 최종 보고서를 생성합니다.

                        [내부 모델 판별 데이터]
                        - Class: {orig_res['predict']} 
                        - Confidence: {orig_res['prob']}

                        [분석 작업 지시]
                        **카테고리** : 해당 이미지가 어떤 카테고리에 해당 하는지 한 가지 단어로 나타내세요. ex) 인물, 사물, 연예인, 정치인, 풍경
                        1.  **픽셀 및 압축 아티팩트(Artifact) 분석**: 이미지의 미세한 픽셀 깨짐, 부자연스러운 JPEG 압축 흔적, 색상 불일치 등을 탐지하여 보고하세요.
                        2.  **조명 및 그림자 일관성 분석**: 피사체에 비치는 조명의 방향, 강도, 색온도가 배경 및 다른 객체와 일치하는지 평가하세요. 그림자의 형태가 광원과 맞지 않는 부분을 찾아내세요.
                        3.  **기하학적 비일관성 분석**: 얼굴의 좌우 대칭성, 눈동자의 초점 및 반사광, 치아나 귀의 비정상적인 형태 등 해부학적으로 부자연스러운 특징을 찾아내세요.
                        4.  **배경 및 컨텍스트 분석**: 이미지의 배경에 나타나는 왜곡이나 논리적으로 맞지 않는 부분을 분석하세요. (예: 피사체와 배경의 해상도 차이)
                        5.  **종합 결론**: 위의 분석들을 종합하여 '딥페이크(Deepfake)' 또는 '실제(Real)'로 최종 판정하고, 그 근거를 기술적인 용어를 사용하여 명확하게 설명하세요.
                        6.  **교차 검증**: 당신의 결론과 [내부 모델 판별 데이터]를 비교하고, 두 결과가 일치하는지 혹은 차이가 발생하는지 명시하세요. 만약 결과에 차이가 있다면, 어떤 분석 항목(예: 조명 분석, 기하학적 분석)에서 다른 판단을 내렸는지 구체적으로 설명하세요.

                        결과는 반드시 마크다운 형식으로, 각 분석 항목을 명확히 구분하여 작성해주세요.
                        """
    prompt_text = "사진이 딥페이크 사진인지 판단해줘."
    
    data = {
        "messages": [
            {"role": "system", "content" : system_text},
            {"role": "user", "content": [{"type": "text", "text": prompt_text}, {"type": "image_url", "imageUrl": {"url": img_url}}]}
            
            ],
        "maxTokens": 400, "temperature": 0.5, "topP": 0.8, "topK": 0,
        "repeatPenalty": 5.0, "stop": [], "includeAiFilters": True, "seed": 0
    }
    try:
        with requests.post(CLOVA_API_URL, headers=headers, json=data, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        try:
                            json_data_str = decoded_line.split('data:', 1)[1]
                            json_data = json.loads(json_data_str)
                            content = json_data.get("message", {}).get("content", "")
                            yield content  # 받은 내용을 그대로 전달
                        except (json.JSONDecodeError, IndexError):
                            continue
    except Exception as e:
        yield f"클로버X API 호출 중 오류가 발생했습니다: {e}"


class CompletionExecutor:
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, skill_set_cot_request):
        headers = {
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
        }
        response = requests.post(
            self._host + '/v1/skillsets/fv46yhgb/versions/2/final-answer',
            headers=headers,
            json=skill_set_cot_request,
            stream=False
        )
        try:
            json_data = response.json()
            print("✅ JSON parsing successful. 응답 내용:", json_data)
        except json.JSONDecodeError as e:
            print("❌ JSON parsing failed:", e)
            return "⚠️ 응답을 파싱하지 못했습니다."

        return json_data.get('result', {}).get('finalAnswer', '⚠️ 응답에 결과가 없습니다.')




# --- 페이지 렌더링 함수 ---

def render_detector_page():
    """딥페이크 판별 메인 페이지를 렌더링합니다."""
    st.title("🛡️ Aegis: AI Deepfake Verifier")
    st.caption("AI 기술을 활용하여 이미지의 진위를 판별합니다. 분석하고 싶은 이미지를 업로드해주세요.")

    with st.container():
        upload_jpg = st.file_uploader(
            "분석할 이미지를 업로드하세요.(JPG) ",
            type='jpg',
            key=st.session_state.upload_key
        )
        st.caption("*업로드된 이미지는 모델 성능 향상에 사용될 수 있습니다.")
        if upload_jpg is not None:
            st.image(upload_jpg, caption="업로드된 이미지", use_container_width=True)

            if st.button("🔍 이미지 분석 요청"):
                # 분석 요청 시 기존 결과 초기화
                st.session_state.original_result = None
                st.session_state.task_id = None

                with st.spinner('서버에 파일을 전송하고 분석을 시작합니다...'):
                    files = {'file': (upload_jpg.name, upload_jpg.getvalue())}
                    try:
                        response = requests.post(f"{BROKER_API_URL}/upload/", files=files)
                        if response.status_code == 200:
                            st.session_state.task_id = response.json().get("task_id")
                            st.success("✅ 분석 요청이 성공적으로 접수되었습니다.")
                            st.info(f"작업 ID: {st.session_state.task_id}")
                        else:
                            st.error(f"서버 요청 실패: {response.text}")
                    except requests.ConnectionError:
                        st.error("❌ 분석 서버에 연결할 수 없습니다. 서버 상태를 확인해주세요.")

    # Polling 및 결과 표시
    if st.session_state.task_id:
        with st.spinner("분석 결과를 기다리는 중입니다... 이 작업은 다소 시간이 소요될 수 있습니다."):
            while True:
                try:
                    status_response = requests.get(f"{BROKER_API_URL}/status/{st.session_state.task_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data["status"] == "completed":
                            st.success("🎉 분석이 완료되었습니다!")
                            backend_result = status_data["result"]
                            predict = backend_result.get("model_result", "N/A")
                            prob = backend_result.get("confidence", 0.0)

                            st.session_state.original_result = {
                                "predict": predict,
                                "prob": f"{prob * 100:.1f}%",
                                "filename": upload_jpg.name
                            }
                            st.session_state.reports.append({
                                "id": str(uuid.uuid4())[:8],
                                "filename": upload_jpg.name,
                                "image_bytes": upload_jpg.getvalue(),
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                **st.session_state.original_result
                            })
                            st.session_state.task_id = None
                            st.session_state.upload_key = str(uuid.uuid4()) # 분석 완료 후 키 초기화
                            st.rerun() # 결과 표시를 위해 화면 새로고침
                        elif status_data["status"] == "failed":
                            st.error("분석 중 오류가 발생했습니다.")
                            st.json(status_data.get("result", "No error details"))
                            st.session_state.task_id = None
                            break
                        time.sleep(2)
                    else:
                        st.error("상태 조회에 실패했습니다. 서버 응답을 확인해주세요.")
                        st.session_state.task_id = None
                        break
                except requests.ConnectionError:
                    st.error("❌ 분석 서버에 연결할 수 없습니다.")
                    st.session_state.task_id = None
                    break

    # 분석 완료 후 결과 표시
    if st.session_state.original_result and not st.session_state.task_id:
        st.markdown("---")
        st.subheader("📊 분석 결과")

        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown("#### 🤖 자체 모델 분석 결과")
                orig_res = st.session_state.original_result
                st.metric(label="판별 결과", value=orig_res['predict'])
                st.metric(label="신뢰도", value=orig_res['prob'])


        with col2:
            with st.container():
                st.markdown("#### 🍀 HyperCLOVA X 전문가 분석")
                if st.button("CLOVA X에게 심층 분석 요청하기"):
                    # 이전 결과 초기화
                    st.session_state.clova_result = None
                    st.session_state.category = None

                    with st.spinner('클로버 X가 이미지를 심층 분석 중입니다...'):
                        filename_for_clova = st.session_state.original_result['filename']
                        image_url_for_clova = f"https://kr.object.ncloudstorage.com/fake-storage/{datetime.today().strftime('%Y-%m-%d')}/{filename_for_clova}"
            
                        # 1. 빈 문자열 변수 생성
                        # 이 변수에 API가 보내는 모든 텍스트 조각을 저장할 것입니다.
                        full_response_text = ""
                        
                        # 2. get_clova_analysis가 주는 모든 조각을 순회하면서 하나로 합칩니다.
                        for chunk in get_clova_analysis(image_url_for_clova, st.session_state.original_result):
                            if chunk:
                                full_response_text = chunk  # += 로 모든 내용을 이어붙입니다.

                        # 3. 루프가 끝나면, 완성된 전체 텍스트에서 '카테고리'를 추출합니다.
                        # 정규표현식을 사용하여 "**카테고리** :" 뒤에 오는 단어를 찾습니다.
                        # 정규표현식을 사용하기 위해 import
                        import re
                        match = re.search(r"카테고리\s*:\s*(.*)", full_response_text)
                        
                        if match:
                            # 정규표현식의 첫 번째 그룹(괄호 안의 내용)을 가져옵니다.
                            category = match.group(1).strip()
                            st.session_state['category'] = category
                            # UI에 성공 메시지를 잠시 보여줍니다.
                            st.toast(f"✅ 카테고리 '{category}' 저장 완료!")
                        else:
                            st.warning("⚠️ 응답에서 카테고리를 찾을 수 없습니다.")

                        # 4. 완성된 전체 답변을 세션 상태에 저장합니다.
                        st.session_state.clova_result = full_response_text
                        
                        # 화면을 새로고침하여 최종 결과를 표시합니다.
                        st.rerun()

            # st.rerun() 이후, 세션 상태에 저장된 최종 결과가 화면에 표시됩니다.
            if st.session_state.clova_result:
                st.subheader("🍀 클로버 X 분석 결과")
                st.markdown(st.session_state.clova_result)


def render_report_page():
    """분석 리포트 페이지를 렌더링합니다."""
    st.title("📋 분석 리포트")
    st.caption("과거에 분석했던 이미지들의 결과를 확인합니다.")

    if not st.session_state.reports:
        st.info("아직 분석한 이미지가 없습니다. 'Detector' 메뉴에서 이미지를 분석해주세요.")
    else:
        # 최신 리포트가 위로 오도록 역순으로 표시
        for report in reversed(st.session_state.reports):
            with st.expander(f"📁 {report['filename']} (분석일: {report['timestamp']})"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(report["image_bytes"], use_container_width=True)
                with col2:
                    st.markdown(f"**- 판별 결과:** `{report['predict']}`")
                    st.markdown(f"**- 신뢰도:** `{report['prob']}`")
                    st.markdown(f"**- 리포트 ID:** `{report['id']}`")
                    


def render_youtube_page():
    from streamlit_chat import message
    
    st.title("📺 딥페이크 관련 영상")
    # 세션 상태 초기화 (youtube 페이지 전용)
    st.divider() # 가로선 추가

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(" 📺 딥페이크 피해 사례 영상")
        st.video("https://www.youtube.com/watch?v=cWNgdQt_PIo")

    with col2:
        st.markdown(" 🎓 딥페이크 예방 교육 영상")
        st.video("https://www.youtube.com/watch?v=K8eG4Kfwqik") 
    if 'youtube_generated' not in st.session_state:
        st.session_state['youtube_generated'] = []
    if 'youtube_past' not in st.session_state:
        st.session_state['youtube_past'] = []

    # 사용자 입력 폼
    with st.form('youtube_form', clear_on_submit=True):
        # st.session_state에 'category'가 없을 경우를 대비해 기본값 처리
        default_keyword = st.session_state.get('category', '')
        user_input = st.text_area('알고 싶은 딥페이크 관련 키워드를 입력하세요:', f'{default_keyword} 딥페이크 피해사례 관련 영상 링크', key='youtube_input', height=100)
        submitted = st.form_submit_button('영상 검색')

        if submitted and user_input:
            with st.spinner("💬 HyperCLOVA가 관련 영상을 검색 중입니다..."):
                completion_executor = CompletionExecutor(
                    host='https://clovastudio.stream.ntruss.com',
                    api_key='', 
                    request_id='',
                )
                request_data = {"query": user_input, "tokenStream": False}

                response_text = completion_executor.execute(request_data)
                st.session_state.youtube_past.append(user_input)
                st.session_state.youtube_generated.append(response_text)
                st.rerun() # 응답 받은 후 바로 새로고침하여 채팅창에 반영

    # 응답 메시지 출력
    if st.session_state['youtube_generated']:
        # 가장 마지막 결과만 표시하도록 수정
        last_index = len(st.session_state['youtube_generated']) - 1
        user_msg = st.session_state['youtube_past'][last_index]
        response_msg = st.session_state['youtube_generated'][last_index]

        message(user_msg, is_user=True, key=f"{last_index}_user")
        
        # --- 이 부분이 링크로 다시 수정되었습니다 ---
        lines = response_msg.split('\n')
        processed_lines = []

        for line in lines:
            if line.strip().startswith("썸네일 : https://i.ytimg.com/vi/"):
                try:
                    video_id = line.split("/vi/")[1].split("/")[0]
                    # 표준 유튜브 시청 URL로 변경
                    video_url = f"https://www.youtube.com/watch?v=cWNgdQt_PIo{video_id}"
                    # st.video 대신 마크다운 링크 추가
                    processed_lines.append(f"🔗 [영상 바로가기]({video_url})")
                except Exception:
                    processed_lines.append("🔗 [링크 변환 실패]")
            else:
                processed_lines.append(line)
        
        # 처리된 라인들을 하나의 텍스트로 합쳐서 출력
        final_response = "\n".join(processed_lines)
        st.markdown(final_response)
        # ------------------------------------


# --- 메인 실행 로직 ---
def main():
    """메인 함수: 앱을 실행합니다."""
    init_session_state()
    load_css()

    # 사이드바 네비게이션
    with st.sidebar:
        st.markdown("# 🛡️ Aegis Verifier")
        page = st.radio(
            "메뉴를 선택하세요",
            ("Detector", "Report","관련 영상"),
            label_visibility="hidden"
        )
        st.markdown("---")
        st.info("""
            **딥페이크(Deepfake)란?**
            AI 기술을 사용해 사람의 얼굴이나 목소리를 조작한 가짜 콘텐츠입니다.
            Aegis는 정교한 AI 모델을 통해 이미지의 진위를 판별하여 허위 정보와 사기 범죄를 예방하는 데 도움을 줍니다.
        """)
        
        # 여기에 로고 이미지 등을 추가할 수 있습니다.
        # st.image("your_logo.png")

    # 선택된 페이지 렌더링
    if page == "Detector":
        render_detector_page()
    elif page == "Report":
        render_report_page()
    elif page == "관련 영상": 
        render_youtube_page() 
if __name__ == "__main__":
    main()