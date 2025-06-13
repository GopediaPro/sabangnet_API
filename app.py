#!/usr/bin/env python3
"""
사방넷 쇼핑몰 코드 조회 API 클라이언트
"""

import os
# 레거시 SSL 수정
from legacy_SSL_handler import LegacySSLHandler
legacy_ssl_handler = LegacySSLHandler()
legacy_ssl_handler.fix_legacy_ssl_config()
# 레거시 SSL 수정 완료
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import logging
from dotenv import load_dotenv
from controller import fetch_mall_list, fetch_order_list


load_dotenv()  # .env 파일 로드

SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
MINIO_USE_SSL = os.getenv('MINIO_USE_SSL')
MINIO_PORT = os.getenv('MINIO_PORT')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    print(f"현재 openssl 설정파일: {os.environ.get('OPENSSL_CONF')}")
    try:
        input_controller = input("사용할 API를 선택하세요: (1. 쇼핑몰 목록 조회, 2. 주문 수집)") 
        if input_controller == "1":
            fetch_mall_list()
        elif input_controller == "2":
            fetch_order_list()
        else:
            print("잘못된 입력입니다.")
    except ValueError as e:
        print(f"\n환경변수를 확인해주세요: {e}")
        print("- SABANG_COMPANY_ID: 사방넷 로그인 아이디")
        print("- SABANG_AUTH_KEY: 사방넷 인증키")
        print("- SABANG_ADMIN_URL: 사방넷 어드민 URL (선택사항)")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        print("\n가능한 해결 방법:")
        print("1. 사방넷 계정 정보가 올바른지 확인")
        print("2. 인증키가 유효한지 확인")
        print("3. 네트워크 연결 상태 확인")
        print("4. XML URL 방식으로 다시 시도")


if __name__ == "__main__":
    main()