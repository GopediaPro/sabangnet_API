"""
1+1 상품 가격 계산 테스트용 CLI
"""

# 서비스 및 리포지토리 import
from core.db import AsyncSessionLocal
from utils.logs.sabangnet_logger import get_logger
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto
from services.usecase.product_one_one_price_usecase import ProductOneOnePriceUsecase


logger = get_logger(__name__)


async def test_one_one_price_calculation(product_nm: str, gubun: str):
    """
    1+1 가격 계산 및 DB 저장 테스트
    
    CLI 환경이라 의존성 관리를 직접 해야 함
    """
    
    logger.info(f"🔄 [{gubun}:{product_nm}] 상품의 1+1 가격 계산 및 DB 저장 테스트 시작...")
    
    try:
        # 데이터베이스 세션 생성
        async with AsyncSessionLocal() as session:
            product_one_one_price_usecase = ProductOneOnePriceUsecase(session=session)
            
            result: OneOnePriceDto = await product_one_one_price_usecase.calculate_and_save_one_one_price(product_nm=product_nm, gubun=gubun)
            logger.info(f"✅ 성공! 1+1 가격 계산 및 저장 완료")
            logger.info(f"📊 결과: {result.model_dump_json()}")
            
    except ValueError as e:
        logger.error(f"❌ 데이터 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 시스템 오류: {e}")
        return False
    
    return True
