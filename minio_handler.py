import os
from minio import Minio
from minio.error import S3Error
from urllib.parse import urlparse, urlunparse
from utils.sabangnet_logger import get_logger
from core.settings import SETTINGS
import shutil
from datetime import datetime

logger = get_logger(__name__)


MINIO_ENDPOINT = SETTINGS.MINIO_ENDPOINT
MINIO_ACCESS_KEY = SETTINGS.MINIO_ACCESS_KEY
MINIO_SECRET_KEY = SETTINGS.MINIO_SECRET_KEY
MINIO_BUCKET_NAME = SETTINGS.MINIO_BUCKET_NAME
MINIO_USE_SSL = SETTINGS.MINIO_USE_SSL
MINIO_PORT = SETTINGS.MINIO_PORT

if MINIO_PORT:
    endpoint = f"{MINIO_ENDPOINT}:{MINIO_PORT}"
else:
    endpoint = MINIO_ENDPOINT

minio_client = Minio(
    endpoint,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_USE_SSL
)

def check_minio_connection():
    """
    Check if MinIO server is reachable and credentials are valid.
    Returns True if connection is successful, otherwise raises an error.
    """
    try:
        # Try to list buckets (will fail if not connected or credentials are wrong)
        minio_client.list_buckets()
        return True
    except Exception as e:
        raise RuntimeError(f"MinIO connection failed: {e}")

def upload_file_to_minio(local_file_path, object_name=None):
    """
    Upload a file to MinIO and return the object name.
    """
    # Check connection before upload
    check_minio_connection()
    if not object_name:
        object_name = os.path.basename(local_file_path)
    try:
        # Ensure bucket exists
        if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
            minio_client.make_bucket(MINIO_BUCKET_NAME)
        minio_client.fput_object(
            MINIO_BUCKET_NAME,
            object_name,
            local_file_path
        )
        logger.info(f"MinIO에 업로드된 XML 파일 이름: {object_name}")
        logger.info(f"MinIO에 업로드된 XML 파일 경로: {local_file_path}")
        return object_name
    except S3Error as e:
        raise RuntimeError(f"MinIO upload failed: {e}")

def remove_port_from_url(url):
    parsed = urlparse(url)
    # netloc에서 포트(:9000 등)만 제거
    if ':' in parsed.netloc:
        host = parsed.netloc.split(':')[0]
    else:
        host = parsed.netloc
    # 다시 URL로 조립
    new_url = urlunparse((
        parsed.scheme,
        host,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    return new_url

def get_minio_file_url(object_name):
    """
    Get a public URL for the uploaded object.
    """
    try:
        url = minio_client.presigned_get_object(MINIO_BUCKET_NAME, object_name)
        return_url = remove_port_from_url(url)
        logger.info(f"get_minio_file_url MinIO에 업로드된 XML 파일 URL: {return_url}")
        return return_url
    except S3Error as e:
        raise RuntimeError(f"MinIO get URL failed: {e}")

def get_minio_file_url_and_size(object_name):
    """
    Get a public URL and file size for the uploaded object.
    """
    try:
        url = minio_client.presigned_get_object(MINIO_BUCKET_NAME, object_name)
        return_url = remove_port_from_url(url)
        stat = minio_client.stat_object(MINIO_BUCKET_NAME, object_name)
        file_size = stat.size  # content_length
        logger.info(f"get_minio_file_url_and_size MinIO에 업로드된 파일 URL: {return_url}, size: {file_size}")
        return return_url, file_size
    except S3Error as e:
        raise RuntimeError(f"MinIO get URL/size failed: {e}")

def temp_file_to_object_name(file):
    # 임시 파일로 저장
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, file.filename)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return temp_file_path

def delete_temp_file(temp_file_path):
    os.remove(temp_file_path)

def url_arrange(url):
    return url.split("?", 1)[0]

def upload_and_get_url(file_path, template_code, file_name=None):
    """
    1. file_name이 없으면 file_path에서 추출
    2. 날짜 기반 minio_object_name 생성
    3. MinIO 업로드
    4. 임시 파일 삭제
    5. presigned url 반환 (쿼리스트링 제거)
    """
    date_now = datetime.now().strftime("%Y%m%d%H%M%S")
    minio_object_name = f"excel/{template_code}/{date_now}_{file_name}"
    object_name = upload_file_to_minio(file_path, minio_object_name)
    delete_temp_file(file_path)
    file_url = get_minio_file_url(object_name)
    return file_url, minio_object_name

def upload_and_get_url_and_size(file_path, template_code, file_name=None):
    """
    1. file_name이 없으면 file_path에서 추출
    2. 날짜 기반 minio_object_name 생성
    3. MinIO 업로드
    4. 임시 파일 삭제
    5. presigned url 반환 (쿼리스트링 제거)
    """
    date_now = datetime.now().strftime("%Y%m%d%H%M%S")
    minio_object_name = f"excel/{template_code}/{date_now}_{file_name}"
    object_name = upload_file_to_minio(file_path, minio_object_name)
    delete_temp_file(file_path)
    file_url, file_size = get_minio_file_url_and_size(object_name)
    return file_url, minio_object_name, file_size