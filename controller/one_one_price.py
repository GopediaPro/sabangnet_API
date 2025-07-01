"""
1+1 상품 가격 계산 테스트용 CLI
"""

# 서비스 및 리포지토리 import
from core.db import AsyncSessionLocal
from utils.sabangnet_logger import get_logger
from schemas.one_one_price.one_one_price_dto import OneOnePriceDto
from services.one_one_price.one_one_price_service import OneOnePriceService
from services.usecase.product_one_one_price_usecase import ProductOneOnePriceUsecase
from services.product_registration.product_registration_read_service import ProductRegistrationReadService
from repository.one_one_price_repository import OneOnePriceRepository


logger = get_logger(__name__)


async def test_one_one_price_calculation(product_nm: str):
    """
    1+1 가격 계산 및 DB 저장 테스트
    
    CLI 환경이라 의존성 관리를 직접 해야 함
    """
    
    logger.info(f"🔄 '{product_nm}' 상품의 1+1 가격 계산 및 DB 저장 테스트 시작...")
    
    try:
        # 데이터베이스 세션 생성
        async with AsyncSessionLocal() as session:
            # 필요한 리포지토리들 생성
            one_one_price_repository = OneOnePriceRepository(session)
            
            # 필요한 서비스들 수동 생성 (의존성 주입)
            one_one_price_service = OneOnePriceService(session, one_one_price_repository)
            product_registration_read_service = ProductRegistrationReadService(session)
            
            # 유즈케이스 인스턴스 생성
            product_one_one_price_usecase = ProductOneOnePriceUsecase(
                session=session,
                one_one_price_service=one_one_price_service,
                product_registration_read_service=product_registration_read_service
            )
            
            result: OneOnePriceDto = await product_one_one_price_usecase.calculate_and_save_one_one_prices(product_nm=product_nm)
            logger.info(f"✅ 성공! 1+1 가격 계산 및 저장 완료")
            logger.info(f"📊 결과: {result.model_dump_json()}")
            
    except ValueError as e:
        logger.error(f"❌ 데이터 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 시스템 오류: {e}")
        return False
    
    return True
