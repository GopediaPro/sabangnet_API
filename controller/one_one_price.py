"""
1+1 상품 가격 계산 테스트용 CLI
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_async_session

# 서비스 및 리포지토리 import
from services.product.price_calc.one_one_price_service import OneOnePriceService
from repository.product.price_calc.one_one_price_repository import OneOnePriceRepository
from repository.product_registration_repository import ProductRegistrationRepository
from repository.product_repository import ProductRepository


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
            result = await service.calculate_and_save_one_one_prices(model_nm)
            
            # 성공 결과 출력
            print("✅ DB 저장 성공!")
            print(f"📝 생성된 ID: {result.id}")
            print(f"💰 기준가격: ₩{result.standard_price:,}")
            print(f"🎯 1+1가격: ₩{result.one_one_price:,}")
            print(f"🔗 FK: {result.test_product_raw_data_id}")
            
            # 몇 개 쇼핑몰 가격 샘플 출력
            print(f"🛒 GS Shop: ₩{result.shop0007:,}")
            print(f"🛒 YES24: ₩{result.shop0029:,}")
            print(f"🛒 쿠팡: ₩{result.shop0075:,}")
            print(f"🛒 스마트스토어: ₩{result.shop0055:,}")
            
            break
            
    except ValueError as e:
        print(f"❌ 데이터 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        return False
    
    return True