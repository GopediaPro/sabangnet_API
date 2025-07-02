"""
품번코드대량등록툴 통합 서비스

Excel 수식 변환부터 DB 저장까지의 전체 프로세스를 담당합니다.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from utils.sabangnet_logger import get_logger
from .product_excel_function_service import ProductCodeRegistrationService
from repository.product_registration_repository import ProductRegistrationRepository
from repository.product_repository import ProductRepository
from core.db import get_async_session
from models.product.product_registration_data import ProductRegistrationRawData

logger = get_logger(__name__)

class ProductCodeIntegratedService:
    """품번코드대량등록툴 통합 서비스"""
    def __init__(self):
        """서비스 초기화 및 의존성 주입"""
        self.reg_repo = None
        self.prod_repo = None 

    async def generate_and_save_all_product_code_data(self, limit: int = None, offset: int = None) -> Dict[str, Any]:
        """
        product_registration_raw_data 테이블에서 데이터를 읽어 generate_product_code_data로 변환 후,
        test_product_raw_data 테이블에 저장하는 비동기 통합 함수 (유효성 검증 제외)
        Args:
            limit: 조회할 데이터 수 제한
            offset: 조회 시작 위치
        Returns:
            {'success': [제품명...], 'failed': [{'제품명', 'error'} ...]}
        """
        async_session = await get_async_session()
        async with async_session as session:
            # repository 인스턴스는 세션이 필요하므로 여기서 할당
            self.reg_repo = ProductRegistrationRepository(session)
            self.prod_repo = ProductRepository(session)
            
            # 1. Fetch all registration data
            registration_data_list: List[ProductRegistrationRawData] = await self.reg_repo.get_all(limit=limit, offset=offset)
            success, failed = [], []
            product_raw_data_list = []
            logger.info(f"registration_data_list log value: {registration_data_list}")
            for reg in registration_data_list:
                reg_dict = reg.to_dict() if hasattr(reg, 'to_dict') else dict(reg.__dict__)
                logger.debug(f"모든 컬럼 값: {reg_dict}")
                product_nm = reg_dict.get('products_nm') or reg_dict.get('product_nm')
                for gubun in ["마스터","전문몰","1+1"]:
                    try:
                        service = ProductCodeRegistrationService(reg_dict)
                        code_data = service.generate_product_code_data(product_nm, gubun)
                        product_raw_data_list.append(code_data)
                        success.append({'product_nm': product_nm, 'gubun': gubun})
                    except Exception as e:
                        logger.error(f"[generate_and_save_all_product_code_data] Error generating product code for '{product_nm}' ({gubun}): {str(e)}")
                        failed.append({'product_nm': product_nm, 'gubun': gubun, 'error': str(e)})

            # 3. Bulk insert into test_product_raw_data
            if product_raw_data_list:
                try:
                    await self.prod_repo.product_raw_data_create(product_raw_data_list)
                except Exception as e:
                    logger.error(f"[generate_and_save_all_product_code_data] Bulk insert error: {str(e)}")
                    failed.append({'bulk_insert_error': str(e)})

            return {'success': success, 'failed': failed}
