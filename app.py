#!/usr/bin/env python3
"""
사방넷 쇼핑몰 코드 조회 API 클라이언트
"""

import os
import typer
from typing import Optional
import logging
from dotenv import load_dotenv
from controller import fetch_mall_list, fetch_order_list

# 레거시 SSL 수정
from legacy_SSL_handler import LegacySSLHandler
legacy_ssl_handler = LegacySSLHandler()
legacy_ssl_handler.fix_legacy_ssl_config()
# 레거시 SSL 수정 완료

# Create Typer app instance
app = typer.Typer(help="사방넷 쇼핑몰 API CLI 도구")

# Load environment variables
load_dotenv()

# Environment variables
SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
MINIO_USE_SSL = os.getenv('MINIO_USE_SSL')
MINIO_PORT = os.getenv('MINIO_PORT')

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.command(help="쇼핑몰 목록을 조회합니다")
def mall_list():
    """쇼핑몰 목록 조회 명령어"""
    try:
        logger.info("쇼핑몰 목록 조회를 시작합니다...")
        fetch_mall_list()
    except Exception as e:
        logger.error(f"쇼핑몰 목록 조회 중 오류 발생: {e}")
        handle_error(e)

@app.command(help="주문 목록을 조회합니다")
def order_list():
    """주문 목록 조회 명령어"""
    try:
        logger.info("주문 목록 조회를 시작합니다...")
        fetch_order_list()
    except Exception as e:
        logger.error(f"주문 목록 조회 중 오류 발생: {e}")
        handle_error(e)

def handle_error(e: Exception):
    """에러 처리 헬퍼 함수"""
    if isinstance(e, ValueError):
        typer.echo(f"\n환경변수를 확인해주세요: {e}")
        typer.echo("필요한 환경변수:")
        typer.echo("- SABANG_COMPANY_ID: 사방넷 로그인 아이디")
        typer.echo("- SABANG_AUTH_KEY: 사방넷 인증키")
        typer.echo("- SABANG_ADMIN_URL: 사방넷 어드민 URL (선택사항)")
    else:
        typer.echo(f"\n오류가 발생했습니다: {e}")
        typer.echo("\n가능한 해결 방법:")
        typer.echo("1. 사방넷 계정 정보가 올바른지 확인")
        typer.echo("2. 인증키가 유효한지 확인")
        typer.echo("3. 네트워크 연결 상태 확인")
        typer.echo("4. XML URL 방식으로 다시 시도")

if __name__ == "__main__":
    app()