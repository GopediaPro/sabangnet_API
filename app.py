#!/usr/bin/env python3
"""
사방넷 쇼핑몰 코드 조회 API 클라이언트
"""

# 레거시 SSL 수정
from legacy_SSL_handler import LegacySSLHandler
legacy_ssl_handler = LegacySSLHandler()
legacy_ssl_handler.fix_legacy_ssl_config()
# 레거시 SSL 수정 완료
from core.db import AsyncSessionLocal
from models.receive_order.receive_order import ReceiveOrder
from sqlalchemy import select
import asyncio
from core.db import get_db_pool
from controller import fetch_mall_list, fetch_order_list, create_product_request
from dotenv import load_dotenv
import typer
from services.order_list_write import OrderListWriteService
from core.initialization import initialize_program
from utils.sabangnet_logger import get_logger
from core.settings import SETTINGS

# Create Typer app instance
app = typer.Typer(help="사방넷 쇼핑몰 API CLI 도구")

# Load environment variables
load_dotenv()

# Environment variables
SABANG_COMPANY_ID = SETTINGS.SABANG_COMPANY_ID
SABANG_AUTH_KEY = SETTINGS.SABANG_AUTH_KEY
SABANG_ADMIN_URL = SETTINGS.SABANG_ADMIN_URL
MINIO_ENDPOINT = SETTINGS.MINIO_ENDPOINT
MINIO_ACCESS_KEY = SETTINGS.MINIO_ACCESS_KEY
MINIO_SECRET_KEY = SETTINGS.MINIO_SECRET_KEY
MINIO_BUCKET_NAME = SETTINGS.MINIO_BUCKET_NAME
MINIO_USE_SSL = SETTINGS.MINIO_USE_SSL
MINIO_PORT = SETTINGS.MINIO_PORT

# Logging configuration
logger = get_logger(__name__)


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


@app.command(help="DB 연결을 테스트합니다")
def test_db_connection():
    """PostgreSQL DB 연결 테스트 명령어"""
    async def _test():
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
            if result == 1:
                typer.echo("DB 연결 성공!")
            else:
                typer.echo("DB 연결은 되었으나, 쿼리 결과가 올바르지 않습니다.")
        except Exception as e:
            typer.echo(f"DB 연결 실패: {e}")
    asyncio.run(_test())


@app.command(help="ReceiveOrder 모델 기본 조회 테스트")
def test_receive_order():
    """ReceiveOrder 모델 기본 조회 테스트 - 동기 함수로 변경"""
    async def _test_receive_order():
        async with AsyncSessionLocal() as session:
            try:
                print("=== ReceiveOrder 모델 테스트 ===")
                stmt = select(ReceiveOrder).limit(1)
                result = await session.execute(stmt)
                order = result.scalar_one_or_none()
                if order:
                    print("조회 성공!")
                else:
                    print("조회된 데이터가 없습니다.")
            except Exception as e:
                print(f"에러 발생: {e}")
                import traceback
                traceback.print_exc()

    # 비동기 함수 실행
    asyncio.run(_test_receive_order())


@app.command(help="수집된 주문 DB에 담기")
def create_order():
    try:
        order_create_service = OrderListWriteService()
        asyncio.run(order_create_service.create_orders())
    except Exception as e:
        logger.error(f"쓰기 작업 중 오류 발생: {e}")
        handle_error(e)
        

@app.command(help="상품 등록")
def create_product():
    try:
        create_product_request()
    except Exception as e:
        logger.error(f"쓰기 작업 중 오류 발생: {e}")


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
    initialize_program()
    app()
