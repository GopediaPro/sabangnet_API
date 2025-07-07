import re
import os

def sanitize_filename(filename: str) -> str:
    """
    파일 시스템에서 사용할 수 없는 특수문자를 모두 제거하여 안전한 파일명을 반환한다.
    (Windows, macOS, Linux 공통적으로 불가한 문자: \\ / : * ? " < > |)
    """
    # 파일명에서 사용할 수 없는 문자 패턴
    invalid_chars = r'[\\/:*?"<>|\[\]]'
    # 공백이나 기타 특수문자도 필요시 추가 가능
    sanitized = re.sub(invalid_chars, '', filename)
    # 파일명 앞뒤 공백 제거
    sanitized = sanitized.strip()
    # 너무 긴 파일명 방지 (255자 제한)
    return sanitized[:255]
