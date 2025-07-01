"""
설명:
    로거 모아놓은 파일입니다.
    비즈니스 로직에는 get_logger 함수를 사용하고,
    HTTP 로깅에는 get_http_logger 함수를 사용합니다.
    근데 HTTP 로거는 서버 시작할 때 자동으로 미들웨어로 등록되기 때문에,
    실제로 쓸 때는 따로 선언할 필요가 없습니다.
    그리고 두 함수 모두 파일명을 파라미터로 받아서 로거를 생성합니다.

사용법:
    파일명은 __name__ 을 사용하면 되고,
    실제로 쓸 때는 스크립트 최상단에 logger = get_logger(__name__) 처럼 선언한 뒤,
    logger.info("로그 메시지") 처럼 사용하면 됩니다.
    
예시:
    from utils.sabangnet_logger import get_logger
    logger = get_logger(__name__)
    ...
    비즈니스 로직 코드
    ...
    logger.info("로그 메시지")
"""


import sys
import time
import logging
from typing import Callable
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from utils.sabangnet_path_utils import SabangNetPathUtils


# 이미 설정된 로거들 추적 (중복 설정 방지)
_setup_loggers = set()


# 색깔 코드
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class ColoredFormatter(logging.Formatter):
    """색깔 포맷터 -> 실제 로그 레벨에 따라 색깔 적용"""

    LEVEL_COLORS = {
        'DEBUG': BLUE,
        'INFO': GREEN,
        'WARNING': YELLOW,
        'ERROR': RED,
        'CRITICAL': RED,
    }

    def __init__(self, log_type: str):
        super().__init__()
        self.log_type = log_type

    def format(self, record):
        # 실제 로그 레벨에 따라 색깔 선택
        level_color = self.LEVEL_COLORS.get(record.levelname, RESET)

        # 전체 경로를 프로젝트 루트 기준 상대 경로로 변환
        try:
            from pathlib import Path
            full_path = Path(record.pathname)
            project_root = SabangNetPathUtils.get_project_root()
            relative_path = full_path.relative_to(project_root)
            record.pathname = str(relative_path)
        except (ValueError, ImportError):
            # 상대 경로 변환 실패 시 원본 사용
            pass

        # 색깔이 적용된 포맷
        if self.log_type == "business_logic":
            colored_format = f"{YELLOW}%(asctime)s | 경로: %(pathname)s | 함수: %(funcName)s() | %(lineno)d번째 줄...{RESET}\n└─{level_color}%(levelname)s{RESET} %(message)s"
        elif self.log_type == "http_requests":
            colored_format = f"{YELLOW}%(asctime)s{RESET} | {level_color}%(levelname)s{RESET} %(message)s"

        # 임시 포맷터로 포맷팅
        temp_formatter = logging.Formatter(
            colored_format, datefmt='%Y-%m-%d %H:%M:%S')
        return temp_formatter.format(record)


# 파일용 포맷터 (색깔 없음, 깔끔한 텍스트) - 커스텀 클래스로 변경
class PlainFormatter(logging.Formatter):
    """파일용 포맷터 -> 색깔 없이 상대 경로만 표시"""

    def format(self, record):
        # 전체 경로를 프로젝트 루트 기준 상대 경로로 변환
        try:
            from pathlib import Path
            full_path = Path(record.pathname)
            project_root = SabangNetPathUtils.get_project_root()
            relative_path = full_path.relative_to(project_root)
            record.pathname = str(relative_path)
        except (ValueError, ImportError):
            # 상대 경로 변환 실패 시 원본 사용
            pass

        return super().format(record)


class EnhancedLogger(logging.Logger):
    """스택트레이스 자동 추가 로거"""

    def error(self, message, *args, **kwargs):
        """ERROR 레벨에서 자동으로 stack_info 추가"""
        if 'stack_info' not in kwargs:
            kwargs['stack_info'] = True
        super().error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """CRITICAL 레벨에서 자동으로 stack_info 추가"""
        if 'stack_info' not in kwargs:
            kwargs['stack_info'] = True
        super().critical(message, *args, **kwargs)


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답을 커스텀 로거로 기록하는 미들웨어"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 시작 시간 기록
        start_time = time.time()

        # 클라이언트 IP 추출
        client_ip = self.get_client_ip(request)

        # 요청 로깅
        http_logger.info(
            f"사용자 {client_ip} -> 요청 "
            f"🔵 {request.method} {request.url.path}"
            f"{f'?{request.url.query}' if request.url.query else ''}"
        )

        # 실제 요청 처리
        response = await call_next(request)

        # 처리 시간 계산
        process_time = time.time() - start_time

        # 응답 로깅 (상태코드와 처리시간 포함)
        status_emoji = self.get_status_emoji(response.status_code)
        http_logger.info(
            f"사용자 {client_ip} <- 응답 "
            f"{status_emoji} {response.status_code} "
            f"{request.method} {request.url.path} "
            f"({process_time:.3f}s)"
        )

        return response

    def get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 직접 연결된 클라이언트 IP
        if hasattr(request.client, "host"):
            return request.client.host

        return "unknown"

    def get_status_emoji(self, status_code: int) -> str:
        """HTTP 상태코드에 따른 이모지 반환"""
        if 200 <= status_code < 300:
            return "🟢"  # 성공
        elif 300 <= status_code < 400:
            return "🔵"  # 리다이렉트
        elif 400 <= status_code < 500:
            return "🟡"   # 클라이언트 에러
        elif 500 <= status_code < 600:
            return "🔴"  # 서버 에러
        else:
            return "❔"  # 알 수 없음


def get_logger(file_name: str, level: str = "INFO") -> EnhancedLogger:
    """
    지정된 이름으로 로거를 가져옵니다.
    사용법: get_logger(__name__)  # __name__ 사용 강제

    Args:
        file_name: 로거 이름 (반드시 __name__ 사용) - 로그에 {file_name}.함수명 형태로 표시

    Returns:
        로거 인스턴스
    """
    # __main__인 경우 실제 파일명으로 변환
    if file_name == "__main__":
        import inspect
        frame = inspect.currentframe().f_back  # 이 __name__ 이라고 호출한 실제 파일 이름
        if frame and frame.f_globals.get('__file__'):
            import os
            actual_file_name: str = os.path.basename(
                frame.f_globals['__file__'])
            file_name = actual_file_name.replace(
                '.py', '')  # app.py → app 같이 파일명만 남기고 확장자 없앰

    # EnhancedLogger 클래스를 기본으로 설정
    logging.setLoggerClass(EnhancedLogger)

    # 이미 설정된 로거는 재설정하지 않음 (단, 핸들러가 있는 경우만)
    existing_logger = logging.getLogger(file_name)
    if file_name in _setup_loggers and existing_logger.handlers:
        return existing_logger

    # 로거 생성 (EnhancedLogger 사용)
    logger = logging.getLogger(file_name)

    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:  # 슬라이싱 -> 얕은복사 -> 원본 삭제되도 반영 안되서 괜찮음...
        logger.removeHandler(handler)

    # 로거 전파 비활성화 (부모 로거로 전파 방지 -> 중복 로그 방지 -> 활성화 하면 부모 로거에서 또 로그 찍혀서 두 번씩 나오는 것 처럼 보임)
    logger.propagate = False

    # 로깅 레벨 설정 (파라미터로 받은 레벨 우선하고, info 같이 들어와도 무조건 대문자로 바꿔주고 없으면 기본 INFO)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 색깔 있는 콘솔용 포맷터
    console_formatter = ColoredFormatter("business_logic")

    file_format = "%(asctime)s | 경로: %(pathname)s | 함수: %(funcName)s() | %(lineno)d번째 줄... \n└─%(levelname)s: %(message)s"
    file_formatter = PlainFormatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 추가 (색깔 없음)
    date_folder = datetime.now().strftime('%Y%m%d')
    safe_file_name = file_name.replace('.', '_')  # 파일명에서 '.'을 '_'로 변경
    log_path = SabangNetPathUtils.get_log_file_path() / date_folder / \
        f"{safe_file_name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, delay=True, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 설정 완료 추가
    _setup_loggers.add(file_name)

    return logger


# HTTP 로깅 전용 간단한 로거 생성
def get_http_logger():
    """HTTP 요청/응답 전용 간단한 로거 (경로/함수 정보 없음)"""
    # EnhancedLogger 클래스를 기본으로 설정 (일관성)
    logging.setLoggerClass(EnhancedLogger)

    logger = logging.getLogger("http_requests")

    # 이미 설정된 경우 재사용
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    # 색깔 있는 콘솔용 포맷터
    console_formatter = ColoredFormatter("http_requests")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


http_logger = get_http_logger()