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
import os
import sys
import time
import json
import socket
import inspect
import logging
import traceback
from pathlib import Path
from typing import Callable
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from utils.sabangnet_path_utils import SabangNetPathUtils


# 서버 이름 추출
SERVER_ID = socket.gethostname()


# 이미 설정된 로거들 추적 (중복 설정 방지)
_setup_loggers = set()


# 색깔 코드
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class ColoredFormatter(logging.Formatter):
    """콘솔용 색깔 포맷터 -> 실제 로그 레벨에 따라 색깔 적용"""

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
            full_path = Path(record.pathname)
            project_root = SabangNetPathUtils.get_project_root()
            relative_path = full_path.relative_to(project_root)
            record.pathname = str(relative_path)
        except (ValueError, ImportError):
            # 상대 경로 변환 실패 시 원본 사용
            pass

        # 색깔이 적용된 포맷
        if self.log_type == "business":
            colored_format = f"{YELLOW}%(asctime)s | 경로: %(pathname)s | 함수: %(funcName)s() | %(lineno)d번째 줄...{RESET}\n└─{level_color}%(levelname)-5s{RESET} %(message)s"
        else:
            colored_format = f"{YELLOW}%(asctime)s{RESET} | {level_color}%(levelname)-5s{RESET} %(message)s"

        # 임시 포맷터로 포맷팅
        temp_formatter = logging.Formatter(
            colored_format, datefmt='%Y-%m-%d %H:%M:%S')
        return temp_formatter.format(record)


# 파일용 포맷터 (색깔 없음, 깔끔한 텍스트) - 커스텀 클래스로 변경
class PlainFormatter(logging.Formatter):
    """파일용 무색 포맷터 -> 색깔 없이 상대 경로만 표시"""

    def format(self, record):
        # 전체 경로를 프로젝트 루트 기준 상대 경로로 변환
        try:
            full_path = Path(record.pathname)
            project_root = SabangNetPathUtils.get_project_root()
            relative_path = full_path.relative_to(project_root)
            record.pathname = str(relative_path)
        except (ValueError, ImportError):
            # 상대 경로 변환 실패 시 원본 사용
            pass

        return super().format(record)


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답을 커스텀 로거로 기록하는 미들웨어"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 시작 시간 기록
        start_time = time.time()

        # 클라이언트 IP 추출
        client_ip = self.get_client_ip(request)

        # 요청 로깅
        http_cli_logger.info(
            f"사용자 {client_ip} ▷▷▷ 서버 {SERVER_ID} "
            f"🟡 {request.method} {request.url.path}"
            f"{f'?{request.url.query}' if request.url.query else ''}"
        )
        http_file_logger.info(
            f"사용자 {client_ip} ▷▷▷ 서버 {SERVER_ID} "
            f"🟡 {request.method} {request.url.path}"
            f"{f'?{request.url.query}' if request.url.query else ''}"
        )

        try:
            # 실제 요청 처리
            response = await call_next(request)
            # 처리 시간 계산
            process_time = time.time() - start_time
            # 응답 로깅 (상태코드와 처리시간 포함)
            status_emoji = self.get_status_emoji(response.status_code)
            http_cli_logger.info(
                f"사용자 {client_ip} ◁◁◁ 서버 {SERVER_ID} "
                f"{status_emoji} {response.status_code} "
                f"{request.method} {request.url.path} "
                f"({process_time:.3f}s)"
            )
            http_file_logger.info(
                f"사용자 {client_ip} ◁◁◁ 서버 {SERVER_ID} "
                f"{status_emoji} {response.status_code} "
                f"{request.method} {request.url.path} "
                f"({process_time:.3f}s)"
            )
            return response

        except Exception as exc:
            # 서버 측 에러 발생 시 처리 (정상적인 Response가 불가능한 상황)
            process_time = time.time() - start_time
            # 콘솔에는 간단한 에러 로그만
            http_cli_logger.error(
                f"사용자 {client_ip} ◁◁◁ 서버 {SERVER_ID} "
                f"🔴 500 "
                f"{request.method} {request.url.path} "
                f"({process_time:.3f}s)"
            )
            # 파일에는 자세하게 (실제 위치 포함)
            http_file_logger.error(
                f"사용자 {client_ip} ◁◁◁ 서버 {SERVER_ID} "
                f"🔴 500 "
                f"{request.method} {request.url.path} "
                f"({process_time:.3f}s)",
                exc
            )

            # 에러 응답 직접 반환 (스택트레이스 출력 방지)
            return JSONResponse(
                status_code=500,
                content={"error": str(exc)}
            )

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
            return "🟠"  # 클라이언트 에러
        elif 500 <= status_code < 600:
            return "🔴"  # 서버 에러
        else:
            return "⚪"  # 알 수 없음


def get_logger_base(file_name: str):
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
        frame = inspect.currentframe().f_back  # 이 __name__ 이라고 호출한 실제 파일 이름
        if frame and frame.f_globals.get('__file__'):
            actual_file_name: str = os.path.basename(
                frame.f_globals['__file__'])
            file_name = actual_file_name.replace(
                '.py', '')  # app.py → app 같이 파일명만 남기고 확장자 없앰

    # 이미 설정된 로거는 재설정하지 않음 (단, 핸들러가 있는 경우만)
    existing_logger = logging.getLogger(file_name)
    if file_name in _setup_loggers and existing_logger.handlers:
        return existing_logger

    logger = logging.getLogger(file_name)

    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:  # 슬라이싱 -> 얕은복사 -> 원본 삭제되도 반영 안되서 괜찮음...
        logger.removeHandler(handler)

    # 로거 전파 비활성화 (부모 로거로 전파 방지 -> 중복 로그 방지 -> 활성화 하면 부모 로거에서 또 로그 찍혀서 두 번씩 나오는 것 처럼 보임)
    logger.propagate = False

    return logger


def get_logger(file_name: str, level: str = "INFO") -> logging.Logger:
    # 로깅 레벨 설정 (파라미터로 받은 레벨 우선하고, info 같이 들어와도 무조건 대문자로 바꿔주고 없으면 기본 INFO)
    logger = get_logger_base(file_name)

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 콘솔 핸들러 추가
    console_formatter = ColoredFormatter("business")
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

    file_format = "%(asctime)s | 경로: %(pathname)s | 함수: %(funcName)s() | %(lineno)d번째 줄... \n└─%(levelname)-5s: %(message)s"
    file_formatter = PlainFormatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler(log_path, delay=True, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 설정 완료 추가
    _setup_loggers.add(file_name)

    return logger


# HTTP 로깅 전용 로거 생성
def get_http_cli_logger(level: str = "INFO"):
    """HTTP 요청/응답 전용 커맨드라인 로거"""
    logger = get_logger_base("http_cli_logger")

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 이미 설정된 경우 재사용
    if logger.handlers:
        return logger

    # 색깔 있는 콘솔용 포맷터
    console_formatter = ColoredFormatter("http")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def get_http_file_logger(level: str = "INFO"):
    """HTTP 요청/응답 전용 파일 로거"""
    logger = get_logger_base("http_file_logger")

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 이미 설정된 경우 재사용
    if logger.handlers:
        return logger

    # 파일 핸들러 추가 (색깔 없음)
    date_folder = datetime.now().strftime('%Y%m%d')
    log_path = SabangNetPathUtils.get_log_file_path() / date_folder / "server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_format = "%(asctime)s | 경로: %(pathname)s | 함수: %(funcName)s() | %(lineno)d번째 줄... \n└─%(levelname)-5s: %(message)s"
    file_formatter = PlainFormatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler(log_path, delay=True, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # 에러 전용 메서드 추가
    def log_error_with_location(msg: str, exc: Exception):
        """실제 에러 발생 위치로 로그 기록"""
        tb = traceback.extract_tb(exc.__traceback__)
        if tb:
            last_trace = tb[-1] # 여기가 실제 위치임
            record = logging.LogRecord(
                name=logger.name, level=logging.ERROR,
                pathname=last_trace.filename, lineno=last_trace.lineno,
                msg=f"{msg}\n{str(exc)}",
                args=(), exc_info=(type(exc), exc, exc.__traceback__), func=last_trace.name
            )
            logger.handle(record)
        else:
            logger.error(f"{msg}\n{str(exc)}", exc_info=(type(exc), exc, exc.__traceback__))
    
    # 몽키패칭
    logger.error = log_error_with_location

    return logger

http_cli_logger = get_http_cli_logger()
http_file_logger = get_http_file_logger()