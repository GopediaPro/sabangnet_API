"""
1+1 상품 가격 계산 테스트용 CLI
"""

# 서비스 및 리포지토리 import
from core.db import get_async_session
from services.one_one_price.one_one_price_service import OneOnePriceService
from repository.one_one_price.one_one_price_repository import OneOnePriceRepository
from repository.product_registration_repository import ProductRegistrationRepository
from repository.product_repository import ProductRepository
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)


async def test_one_one_price_calculation(model_nm: str):
    """1+1 가격 계산 및 DB 저장 테스트"""
    
    print(f"🔄 '{model_nm}' 상품의 1+1 가격 계산 및 DB 저장 테스트 시작...")
    
    try:
        # 데이터베이스 세션 생성
        async for session in get_async_session():
            # Repository 인스턴스 생성
            product_registration_repo = ProductRegistrationRepository(session)
            product_repo = ProductRepository(session)
            one_one_price_repo = OneOnePriceRepository(session)
            
            # Service 인스턴스 생성
            service = OneOnePriceService(
                session=session,
                product_registration_repository=product_registration_repo,
                product_repository=product_repo,
                one_one_price_repository=one_one_price_repo
            )
            
            # 1+1 가격 계산 및 저장 실행
            await service.calculate_and_save_one_one_prices(model_nm)

            break
            
    except ValueError as e:
        print(f"❌ 데이터 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        return False
    
    return True