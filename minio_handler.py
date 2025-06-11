import os
from minio import Minio
from minio.error import S3Error
from urllib.parse import urlparse, urlunparse

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
MINIO_USE_SSL = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
MINIO_PORT = os.getenv('MINIO_PORT')

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
        print(f"MinIO에 업로드된 XML 파일 이름: {object_name}")
        print(f"MinIO에 업로드된 XML 파일 경로: {local_file_path}")
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
        print(f"get_minio_file_url MinIO에 업로드된 XML 파일 URL: {return_url}")
        return return_url
    except S3Error as e:
        raise RuntimeError(f"MinIO get URL failed: {e}") 