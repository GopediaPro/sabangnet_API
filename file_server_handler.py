import os
import requests
from typing import Optional
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)

# HTTPS 사용으로 변경 (SSL 검증은 환경에 따라 조정)
FILE_SERVER_BASE_URL = os.getenv('FILE_SERVER_BASE_URL', 'https://file.lyckabc.xyz')
FILE_SERVER_API_URL = f"{FILE_SERVER_BASE_URL}/api"
FILE_SERVER_DOWNLOAD_URL = f"{FILE_SERVER_BASE_URL}/files"

# SSL 검증 설정 (개발환경에서는 false, 프로덕션에서는 true)
VERIFY_SSL = os.getenv('VERIFY_SSL', 'false').lower() == 'true'

def upload_to_file_server(local_file_path: str, object_name: Optional[str] = None) -> str:
    """
    Upload a file to the file server and return the object name (filename).
    """
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Local file not found: {local_file_path}")
    
    if not object_name:
        object_name = os.path.basename(local_file_path)
    
    try:
        with open(local_file_path, 'rb') as f:
            files = {'file': f}
            data = {'filename': object_name}
            
            logger.info(f"Uploading {local_file_path} as {object_name}")
            response = requests.post(
                f"{FILE_SERVER_API_URL}/upload", 
                files=files, 
                data=data,
                timeout=30,
                verify=VERIFY_SSL  # SSL 검증 설정 적용
            )
            response.raise_for_status()
            
            result = response.json()
            
            if not result.get('success', False):
                raise RuntimeError(f"Upload failed: {result.get('message', 'Unknown error')}")
            
            filename = result.get('filename', object_name)
            logger.info(f"Upload successful: {filename}")
            return filename
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during upload: {e}")
        raise RuntimeError(f"File server upload failed (network error): {e}")
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise RuntimeError(f"File server upload failed: {e}")

def get_file_server_url(object_name: str) -> str:
    """
    Get a public URL for the uploaded object on the file server.
    """
    return f"{FILE_SERVER_DOWNLOAD_URL}/{object_name}"

def upload_xml_content_to_file_server(xml_content: str, filename: str) -> str:
    """
    Upload XML content directly to the file server.
    Args:
        xml_content: The XML content as string
        filename: The filename for the XML file
    Returns:
        str: The filename of the uploaded file
    Raises:
        RuntimeError: If the upload fails
    """
    try:
        data = {
            'content': xml_content,
            'filename': filename
        }
        logger.info(f"Uploading XML content as {filename}")
        response = requests.post(
            f"{FILE_SERVER_API_URL}/upload-xml",
            data=data,
            timeout=30,
            verify=VERIFY_SSL
        )
        response.raise_for_status()
        result = response.json()
        if not result.get('success', False):
            raise RuntimeError(f"XML upload failed: {result.get('message', 'Unknown error')}")
        uploaded_filename = result.get('filename', filename)
        logger.info(f"XML upload successful: {uploaded_filename}")
        return uploaded_filename
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during XML upload: {e}")
        raise RuntimeError(f"XML upload failed (network error): {e}")
    except Exception as e:
        logger.error(f"XML upload error: {e}")
        raise RuntimeError(f"XML upload failed: {e}")

# 테스트용 함수
def test_connection():
    """
    파일 서버 연결 테스트
    """
    try:
        # API 서버 테스트
        response = requests.get(f"{FILE_SERVER_API_URL}/health", timeout=10, verify=VERIFY_SSL)
        if response.status_code == 200:
            print("✅ API 서버 연결 성공!")
            api_ok = True
        else:
            print(f"❌ API 서버 응답 오류: {response.status_code}")
            api_ok = False
            
        # 파일 서버 테스트
        response = requests.get(f"{FILE_SERVER_BASE_URL}/health", timeout=10, verify=VERIFY_SSL)
        if response.status_code == 200:
            print("✅ 파일 서버 연결 성공!")
            file_ok = True
        else:
            print(f"❌ 파일 서버 응답 오류: {response.status_code}")
            file_ok = False
            
        return api_ok and file_ok
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

if __name__ == "__main__":
    # 연결 테스트
    if test_connection():
        print("파일 업로드 준비 완료!")
    else:
        print("파일 서버 설정을 확인해주세요.")