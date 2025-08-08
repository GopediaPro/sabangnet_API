"""
품번코드대량등록툴 통합 서비스

Excel 수식 변환부터 DB 저장까지의 전체 프로세스를 담당합니다.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
from utils.logs.sabangnet_logger import get_logger
from .product_excel_function_service import ProductCodeRegistrationService
from repository.product_registration_repository import ProductRegistrationRepository
from repository.product_repository import ProductRepository
from core.db import get_async_session
from models.product.product_registration_data import ProductRegistrationRawData
from repository.product_mycategory_repository import ProductMyCategoryRepository
from services.product_registration.product_registration_service import ProductRegistrationService
from schemas.product_registration import ExcelProcessResultDto, ProductRegistrationBulkResponseDto, ExcelImportResponseDto
from utils.make_xml.sabang_api_result_parser import SabangApiResultParser

logger = get_logger(__name__)

class ProductCodeIntegratedService:
    """품번코드대량등록툴 통합 서비스"""
    def __init__(self):
        """서비스 초기화 및 의존성 주입"""
        self.reg_repo = None
        self.prod_repo = None 

    async def get_class_cd_dict(self, product_mycategory_repo, reg_dict) -> dict:
        """
        reg_dict에서 class_nm1~4를 꺼내 product_mycategory_repo로 class_cd1~4를 조회해 dict로 반환
        """
        class_cd_dict = {}
        for level in [1, 2, 3, 4]:
            class_nm = reg_dict.get(f'class_nm{level}')
            if class_nm:
                class_cd = await product_mycategory_repo.get_class_cd_from_nm(level, class_nm)
                class_cd_dict[f'class_cd{level}'] = class_cd
            else:
                class_cd_dict[f'class_cd{level}'] = None
        return class_cd_dict

    async def generate_and_save_all_product_code_data(self, limit: int = None, offset: int = None) -> Dict[str, Any]:
        """
        product_registration_raw_data 테이블에서 데이터를 읽어 generate_product_code_data로 변환 후,
        test_product_raw_data 테이블에 저장하는 비동기 통합 함수 (유효성 검증 제외)
        company_goods_cd가 매칭되면 update, 없으면 create 수행
        Args:
            limit: 조회할 데이터 수 제한
            offset: 조회 시작 위치
        Returns:
            {'success': [제품명...], 'failed': [{'제품명', 'error'} ...]}
        """
        from core.db import get_async_session
        
        async for session in get_async_session():
            # repository 인스턴스는 세션이 필요하므로 여기서 할당
            self.reg_repo = ProductRegistrationRepository(session)
            self.prod_repo = ProductRepository(session)
            product_mycategory_repo = ProductMyCategoryRepository(session)
            
            # 1. Fetch all registration data
            registration_data_list: List[ProductRegistrationRawData] = await self.reg_repo.get_all(limit=limit, offset=offset)
            
            # 모든 데이터를 상세히 로깅
            logger.info(f"registration_data_list count: {len(registration_data_list)}")
            for i, reg_data in enumerate(registration_data_list):
                logger.info(f"Data {i+1}: {reg_data.to_dict()}")
            
            success, failed = [], []
            updated_count, created_count = 0, 0
            
            # logger.info(f"registration_data_list log value: {registration_data_list}")
            for reg in registration_data_list:
                reg_dict = reg.to_dict() if hasattr(reg, 'to_dict') else dict(reg.__dict__)
                logger.debug(f"모든 컬럼 값: {reg_dict}")
                logger.info(f"stock_use_yn 값 확인: {reg_dict.get('stock_use_yn')}")
                product_nm = reg_dict.get('product_nm')
                # 여기서 메서드 호출
                class_cd_dict = await self.get_class_cd_dict(product_mycategory_repo, reg_dict)
                # logger.info(f"class_cd_dict for product_nm={product_nm}: {class_cd_dict}")
                for gubun in ["마스터", "전문몰", "1+1"]:
                    try:
                        service = ProductCodeRegistrationService(reg_dict, class_cd_dict)
                        code_data = service.generate_product_code_data(product_nm, gubun)
                        
                        # company_goods_cd로 upsert 수행
                        company_goods_cd = code_data.get('compayny_goods_cd')
                        if company_goods_cd:
                            # upsert 메서드 사용
                            upsert_result = await self.prod_repo.upsert_product_raw_data(code_data)
                            if upsert_result['success']:
                                if upsert_result['action'] == 'updated':
                                    updated_count += 1
                                else:
                                    created_count += 1
                                success.append({
                                    'product_nm': product_nm, 
                                    'gubun': gubun, 
                                    'company_goods_cd': company_goods_cd,
                                    'action': upsert_result['action']
                                })
                            else:
                                failed.append({
                                    'product_nm': product_nm, 
                                    'gubun': gubun, 
                                    'error': 'upsert 실패',
                                    'company_goods_cd': company_goods_cd
                                })
                        else:
                            logger.warning(f"company_goods_cd가 생성되지 않음: {product_nm} ({gubun})")
                            failed.append({'product_nm': product_nm, 'gubun': gubun, 'error': 'company_goods_cd 생성 실패'})
                            
                    except Exception as e:
                        logger.error(f"[generate_and_save_all_product_code_data] Error processing product code for '{product_nm}' ({gubun}): {str(e)}")
                        failed.append({'product_nm': product_nm, 'gubun': gubun, 'error': str(e)})

            logger.info(f"처리 완료 - 생성: {created_count}개, 업데이트: {updated_count}개, 실패: {len(failed)}개")
            return {
                'success': success, 
                'failed': failed,
                'summary': {
                    'created_count': created_count,
                    'updated_count': updated_count,
                    'failed_count': len(failed),
                    'total_processed': len(success) + len(failed)
                }
            }

    async def _process_excel_and_db_storage(self, file_path: str, sheet_name: str) -> Tuple[ExcelProcessResultDto, ProductRegistrationBulkResponseDto]:
        """1단계: Excel 파일 처리 및 DB 저장"""
        logger.info("1단계: Excel 파일 처리 및 DB 저장 시작")
        from core.db import get_async_session
        
        async for session in get_async_session():
            product_registration_service = ProductRegistrationService(session)
            excel_result, bulk_result = await product_registration_service.process_excel_and_create(file_path, sheet_name)
        
        logger.info(f"1단계 완료: Excel 처리 {excel_result.valid_rows}개, DB 저장 {bulk_result.success_count}개")
        return excel_result, bulk_result

    async def _process_db_transfer(self) -> Dict[str, Any]:
        """2단계: DB Transfer (product_registration_raw_data → test_product_raw_data)"""
        logger.info("2단계: DB Transfer 시작")
        transfer_result = await self.generate_and_save_all_product_code_data()
        
        logger.info(f"2단계 완료: 성공 {len(transfer_result['success'])}개, 실패 {len(transfer_result['failed'])}개")
        return transfer_result

    async def _process_sabang_api_request(self) -> Dict[str, Any]:
        """3단계: DB to SabangAPI 요청"""
        logger.info("3단계: DB to SabangAPI 요청 시작")
        logger.info(f"[DEBUG] _process_sabang_api_request 진입")
        
        from core.db import get_async_session
        
        async for session in get_async_session():
            logger.info(f"[DEBUG] session 컨텍스트 진입: {session}")
            product_registration_service = ProductRegistrationService(session)
            logger.info(f"[DEBUG] ProductRegistrationService 생성 완료: {product_registration_service}")
            
            logger.info(f"[DEBUG] process_db_to_xml_and_sabangnet_request 호출 직전")
            sabang_result = await product_registration_service.process_db_to_xml_and_sabangnet_request()
            logger.info(f"[DEBUG] process_db_to_xml_and_sabangnet_request 호출 완료, 결과: {sabang_result}, 타입: {type(sabang_result)}")
        
        # sabang_api_result 추출
        sabang_api_result = sabang_result.get('sabang_api_result', {})
        logger.info(f"사방넷 API 응답 파싱 결과: {sabang_api_result}")
        
        logger.info(f"3단계 완료: {sabang_result['processed_count']}개 상품 처리")
        return {
            **sabang_result,
            'sabang_api_result': sabang_api_result
        }

    async def process_complete_product_registration_workflow(
        self, 
        file_path: str, 
        sheet_name: str = "상품등록"
    ) -> Dict[str, Any]:
        """
        전체 상품 등록 워크플로우를 처리합니다:
        1. Excel 파일 처리 및 DB 저장
        2. DB Transfer (product_registration_raw_data → test_product_raw_data)
        3. DB to SabangAPI 요청
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            
        Returns:
            Dict[str, Any]: 전체 프로세스 결과
        """
        try:
            logger.info("전체 상품 등록 워크플로우 시작")
            
            # 1. Excel 파일 처리 및 DB 저장
            excel_result, bulk_result = await self._process_excel_and_db_storage(file_path, sheet_name)
            
            # 2. DB Transfer (product_registration_raw_data → test_product_raw_data)
            transfer_result = await self._process_db_transfer()
            
            # 3. DB to SabangAPI 요청
            sabang_result = await self._process_sabang_api_request()
            
            # 전체 결과 반환
            return {
                "success": True,
                "message": "전체 상품 등록 워크플로우 완료",
                "excel_processing": {
                    "total_rows": excel_result.total_rows,
                    "valid_rows": excel_result.valid_rows,
                    "invalid_rows": excel_result.invalid_rows,
                    "validation_errors": excel_result.validation_errors
                },
                "database_result": {
                    "success_count": bulk_result.success_count,
                    "error_count": bulk_result.error_count,
                    "created_ids": bulk_result.created_ids,
                    "errors": bulk_result.errors
                },
                "transfer_result": transfer_result,
                "sabang_api_result": sabang_result
            }
            
        except Exception as e:
            logger.error(f"전체 상품 등록 워크플로우 오류: {e}")
            return {
                "success": False,
                "message": f"워크플로우 처리 중 오류 발생: {str(e)}",
                "excel_processing": {
                    "total_rows": 0,
                    "valid_rows": 0,
                    "invalid_rows": 0,
                    "validation_errors": [f"워크플로우 오류: {str(e)}"]
                },
                "database_result": {
                    "success_count": 0,
                    "error_count": 0,
                    "created_ids": [],
                    "errors": [f"워크플로우 오류: {str(e)}"]
                },
                "transfer_result": {
                    "success": [],
                    "failed": [f"워크플로우 오류: {str(e)}"]
                },
                "sabang_api_result": {
                    "processed_count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "errors": [f"워크플로우 오류: {str(e)}"]
                },
                "error": str(e)
            }
