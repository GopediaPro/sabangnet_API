#!/usr/bin/env python3
"""
크로스 플랫폼 테스트 실행 스크립트
Windows, Mac, Linux 모든 환경에서 동작합니다.
"""


import sys
import platform
import subprocess
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__, level="DEBUG")


def run_command(cmd, shell=True):
    """명령어 실행"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_uv_available():
    """uv 설치되어 있는지 확인"""
    success, _, _ = run_command("uv --version")
    return success


def run_tests():
    """테스트 실행"""

    success, stdout, stderr = run_command("pytest")

    if stdout:
        logger.info(stdout)
    if stderr:
        logger.error(stderr)
    
    return success


def main():
    """메인 함수"""

    logger.debug("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 테스트 시작 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    logger.debug(f"플랫폼: {platform.system()} {platform.release()}")
    logger.debug(f"Python: {sys.version}")
    
    # uv 사용 여부 확인
    if check_uv_available():
        logger.debug("uv 감지됨")
    
    try:
        # 테스트 실행
        success = run_tests()
        
        if success:
            logger.debug("모든 테스트 통과")
            logger.debug("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 테스트 완료 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        else:
            logger.error("일부 테스트 실패")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.debug("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 테스트 중단됨 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()