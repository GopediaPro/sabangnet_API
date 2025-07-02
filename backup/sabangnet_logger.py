import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from utils.sabangnet_path_utils import SabangNetPathUtils

# 이미 설정된 로거들 추적 (중복 설정 방지)
_setup_loggers = set()


class LazyFileHandler(logging.Handler):
    """
    실제 로그 호출 시에만 파일을 생성하는 지연 파일 핸들러
    """
    
    def __init__(self, log_path: Path, encoding: str = 'utf-8'):
        super().__init__()
        self.log_path = log_path
        self.encoding = encoding
        self._file_handler: Optional[logging.FileHandler] = None
        self._is_initialized = False
    
    def _ensure_file_handler(self):
        """파일 핸들러가 없으면 생성"""
        if not self._is_initialized:
            # 디렉토리 생성 (실제 로그 호출 시에만)
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 핸들러 생성 (실제 로그 호출 시에만)
            self._file_handler = logging.FileHandler(self.log_path, encoding=self.encoding)
            self._file_handler.setLevel(self.level)
            self._file_handler.setFormatter(self.formatter)
            self._is_initialized = True
    
    def emit(self, record):
        """로그 레코드를 처리 (실제 로그 호출 시에만 파일 생성됨)"""
        self._ensure_file_handler()
        if self._file_handler:
            self._file_handler.emit(record)
    
    def close(self):
        """핸들러 종료"""
        if self._file_handler:
            self._file_handler.close()
        super().close()


def get_logger(file_name: str, level: str = "INFO") -> logging.Logger:
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
            actual_file_name: str = os.path.basename(frame.f_globals['__file__'])
            file_name = actual_file_name.replace('.py', '')  # app.py → app 같이 파일명만 남기고 확장자 없앰
    
    # 이미 설정된 로거는 재설정하지 않음 (단, 핸들러가 있는 경우만)
    existing_logger = logging.getLogger(file_name)
    if file_name in _setup_loggers and existing_logger.handlers:
        return existing_logger

    # 로거 생성
    logger = logging.getLogger(file_name)

    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:  # 슬라이싱 -> 얕은복사 -> 원본 삭제되도 괜찮음...
        logger.removeHandler(handler)

    # 로거 전파 비활성화 (부모 로거로 전파 방지 -> 중복 로그 방지)
    logger.propagate = False

    # 로깅 레벨 설정 (파라미터로 받은 레벨 우선하고, info 같이 들어와도 무조건 대문자로 바꿔주고 없으면 기본 INFO)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 포맷터 생성
    log_format: str = "%(asctime)s | %(name)s.%(funcName)s()\n└─%(levelname)s: %(message)s"
    formatter = logging.Formatter(log_format)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 지연 파일 핸들러 추가 (실제 로그 호출 시에만 파일 생성됨) -> files/logs/{날짜}/{모듈명}.log 형식
    date_folder = datetime.now().strftime('%Y%m%d')
    safe_file_name = file_name.replace('.', '_')  # 파일명에서 '.'을 '_'로 변경
    log_path = SabangNetPathUtils.get_log_file_path() / date_folder / f"{safe_file_name}.log"
    
    lazy_file_handler = LazyFileHandler(log_path, encoding='utf-8')
    lazy_file_handler.setLevel(log_level)
    lazy_file_handler.setFormatter(formatter)
    logger.addHandler(lazy_file_handler)

    # 설정 완료 추가
    _setup_loggers.add(file_name)

    return logger