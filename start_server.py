from core.settings import SETTINGS
from utils.logs.sabangnet_logger import get_logger
from core.initialization import initialize_program


def run_fastapi():
    """
    'n8n' <-> '사방넷 서버' 간의 https 통신은 'n8n node; http request' 의 'Ignore SSL Issues (Insecure)' 옵션 활성화 하면 되는데,\n
    'FastAPI 서버' <-> '사방넷 서버' 간의 https 통신은 SSL 재협상 허용을 코드로(아니면 터미널에서 직접) 수정해줘야 할 듯 합니다.\n
    
    근데 FastAPI 공식 예제로 나와 있는 uvicorn main:app 방식은 실행 주체가 uvicorn 이 되는 제어역전 방식이기 때문에,\n
    각종 모듈들이 uvicorn 에 의해 import 되는 과정에서 순서가 꼬여서 파일 맨 위의 SSL 설정이 무효화되는 듯 합니다.\n
    그래서 uvicorn.run 을 여기서 호출했더니 실행 흐름이 다시 돌아와서 SSL 재협상 설정이 잘 되는 것 같습니다...
    """
    initialize_program()
    logger = get_logger(__name__)
    try:
        import uvicorn
        uvicorn.run("main:app", host=SETTINGS.FASTAPI_HOST, port=SETTINGS.FASTAPI_PORT, reload=False, access_log=False)
    except Exception as e:
        logger.exception(f"FastAPI 서버 실행 중 오류 발생: {e}")