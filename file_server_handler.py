import os
import requests
from typing import Optional, Dict, Any
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

FILE_SERVER_BASE_URL = os.getenv('FILE_SERVER_BASE_URL', 'https://file.lyckabc.xyz')
FILE_SERVER_API_URL = f"{FILE_SERVER_BASE_URL}/api"
FILE_SERVER_DOWNLOAD_URL = f"{FILE_SERVER_BASE_URL}/files"

def upload_to_file_server(local_file_path: str, object_name: Optional[str] = None) -> str:
    """
    Upload a file to the file server and return the object name (filename).
    
    Args:
        local_file_path: Path to the local file to upload
        object_name: Optional custom filename for the uploaded file
        
    Returns:
        str: The filename of the uploaded file
        
    Raises:
        FileNotFoundError: If the local file doesn't exist
        RuntimeError: If the upload fails
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
                timeout=30  # 타임아웃 추가
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
            timeout=30
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

def get_file_server_url(object_name: str) -> str:
    """
    Get a public URL for the uploaded object on the file server.
    
    Args:
        object_name: The filename/object name on the server
        
    Returns:
        str: The public URL to access the file
    """
    return f"{FILE_SERVER_DOWNLOAD_URL}/{object_name}"

def check_file_exists(object_name: str) -> bool:
    """
    Check if a file exists on the file server.
    
    Args:
        object_name: The filename to check
        
    Returns:
        bool: True if file exists, False otherwise
    """
    try:
        url = get_file_server_url(object_name)
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Error checking file existence: {e}")
        return False

def delete_file_from_server(object_name: str) -> bool:
    """
    Delete a file from the file server.
    
    Args:
        object_name: The filename to delete
        
    Returns:
        bool: True if deletion successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{FILE_SERVER_API_URL}/delete/{object_name}",
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        success = result.get('success', False)
        
        if success:
            logger.info(f"File deleted successfully: {object_name}")
        else:
            logger.warning(f"File deletion failed: {result.get('message', 'Unknown error')}")
            
        return success
        
    except Exception as e:
        logger.error(f"Error deleting file {object_name}: {e}")
        return False

def list_files_on_server() -> Optional[Dict[str, Any]]:
    """
    List all files on the file server.
    
    Returns:
        dict: Response containing file list, or None if failed
    """
    try:
        response = requests.get(f"{FILE_SERVER_API_URL}/files", timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('success', False):
            return result
        else:
            logger.warning("Failed to list files")
            return None
            
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return None

# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 파일 업로드 예제
        filename = upload_to_file_server("/path/to/local/file.xml", "custom_name.xml")
        print(f"업로드된 파일: {filename}")
        
        # 파일 URL 생성
        file_url = get_file_server_url(filename)
        print(f"파일 URL: {file_url}")
        
        # XML 내용 직접 업로드 예제
        xml_content = """<?xml version="1.0" encoding="EUC-KR"?>
<SABANG_MALL_LIST>
    <HEADER>
        <SEND_COMPAYNY_ID>TEST</SEND_COMPAYNY_ID>
        <SEND_AUTH_KEY>TESTKEY123</SEND_AUTH_KEY>
        <SEND_DATE>20240101</SEND_DATE>
    </HEADER>
</SABANG_MALL_LIST>"""
        
        xml_filename = upload_xml_content_to_file_server(xml_content, "test_sabang.xml")
        xml_url = get_file_server_url(xml_filename)
        print(f"XML URL: {xml_url}")
        
        # 파일 존재 확인
        if check_file_exists(filename):
            print(f"파일 {filename}이 서버에 존재합니다.")
        
        # 파일 목록 조회
        files_info = list_files_on_server()
        if files_info:
            print(f"서버의 파일 개수: {files_info['count']}")
            
    except Exception as e:
        print(f"오류 발생: {e}")