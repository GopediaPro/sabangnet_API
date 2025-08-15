"""
품번코드대량등록툴 통합 서비스 V2

Excel 수식 변환부터 DB 저장까지의 전체 프로세스를 담당합니다.
V2에서는 bulk_result 데이터를 기반으로 DB Transfer와 SabangAPI 요청을 처리합니다.
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
from schemas.product_registration import (
    ExcelProcessResultDto, 
    ProductRegistrationBulkResponseDto
)
from utils.make_xml.product_registration_xml import ProductRegistrationXml
from services.product.product_read_service import ProductReadService
from services.count_excuting_service import CountExecutingService
from models.count_executing_data.count_executing_data import CountExecuting
from schemas.product.product_raw_data_dto import ProductRawDataDto

logger = get_logger(__name__)

class ProductCodeIntegratedServiceV2:
    """품번코드대량등록툴 통합 서비스 V2"""
    
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

    async def _process_excel_and_db_storage(self, file_path: str, sheet_name: str) -> Tuple[ExcelProcessResultDto, ProductRegistrationBulkResponseDto]:
        """1단계: Excel 파일 처리 및 DB 저장"""
        logger.info("1단계: Excel 파일 처리 및 DB 저장 시작")
        from core.db import get_async_session
        
        async for session in get_async_session():
            product_registration_service = ProductRegistrationService(session)
            excel_result, bulk_result = await product_registration_service.process_excel_and_create(file_path, sheet_name)
        
        logger.info(f"1단계 완료: Excel 처리 {excel_result.valid_rows}개, DB 저장 {bulk_result.success_count}개")
        return excel_result, bulk_result

    async def _process_db_transfer_with_bulk_result(self, bulk_result: ProductRegistrationBulkResponseDto) -> Dict[str, Any]:
        """
        2단계: DB Transfer (product_registration_raw_data → test_product_raw_data)
        bulk_result의 created_ids를 기반으로 처리
        """
        logger.info("2단계: DB Transfer 시작 (bulk_result 기반)")
        
        if not bulk_result.created_ids:
            logger.warning("전송할 데이터가 없습니다.")
            return {
                'success': [],
                'failed': [],
                'summary': {
                    'created_count': 0,
                    'updated_count': 0,
                    'failed_count': 0,
                    'total_processed': 0
                }
            }
        
        from core.db import get_async_session
        
        async for session in get_async_session():
            # repository 인스턴스는 세션이 필요하므로 여기서 할당
            self.reg_repo = ProductRegistrationRepository(session)
            self.prod_repo = ProductRepository(session)
            product_mycategory_repo = ProductMyCategoryRepository(session)
            
            # bulk_result의 created_ids를 기반으로 데이터 조회
            registration_data_list: List[ProductRegistrationRawData] = []
            for created_id in bulk_result.created_ids:
                reg_data = await self.reg_repo.get_by_id(created_id)
                if reg_data:
                    registration_data_list.append(reg_data)
            
            logger.info(f"전송할 데이터 수: {len(registration_data_list)}")
            
            success, failed = [], []
            updated_count, created_count = 0, 0
            
            for reg in registration_data_list:
                reg_dict = reg.to_dict() if hasattr(reg, 'to_dict') else dict(reg.__dict__)
                logger.debug(f"모든 컬럼 값: {reg_dict}")
                logger.info(f"stock_use_yn 값 확인: {reg_dict.get('stock_use_yn')}")
                product_nm = reg_dict.get('product_nm')
                
                # 여기서 메서드 호출
                class_cd_dict = await self.get_class_cd_dict(product_mycategory_repo, reg_dict)
                
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
                        logger.error(f"[_process_db_transfer_with_bulk_result] Error processing product code for '{product_nm}' ({gubun}): {str(e)}")
                        failed.append({'product_nm': product_nm, 'gubun': gubun, 'error': str(e)})

            logger.info(f"2단계 완료: 생성 {created_count}개, 업데이트 {updated_count}개, 실패 {len(failed)}개")
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

    async def _process_sabang_api_request_with_transfer_result(self, transfer_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        3단계: DB to SabangAPI 요청
        transfer_result의 성공한 데이터를 기반으로 처리
        """
        logger.info("3단계: DB to SabangAPI 요청 시작 (transfer_result 기반)")
        
        # transfer_result에서 성공한 상품들의 company_goods_cd 추출
        successful_products = transfer_result.get('success', [])
        if not successful_products:
            logger.warning("SabangAPI 요청할 성공한 상품이 없습니다.")
            return {
                'processed_count': 0,
                'success_count': 0,
                'error_count': 0,
                'errors': ['전송된 성공한 상품이 없습니다.'],
                'sabang_api_result': {}
            }
        
        try:
            # 1. transfer_result 기반으로 XML 파일 생성
            xml_file_path = await self._create_xml_from_transfer_result(transfer_result)
            
            # 2. 생성된 XML 파일로 SabangAPI 요청
            sabang_result = await self._process_sabang_api_request_with_xml(xml_file_path, transfer_result)
            
            logger.info(f"3단계 완료: {sabang_result.get('processed_count', 0)}개 상품 처리")
            return sabang_result
            
        except Exception as e:
            logger.error(f"SabangAPI 요청 처리 중 오류: {e}")
            return {
                'processed_count': 0,
                'success_count': 0,
                'error_count': len(successful_products),
                'errors': [f'SabangAPI 요청 처리 중 오류: {str(e)}'],
                'sabang_api_result': {},
                'requested_company_goods_cds': [item.get('company_goods_cd') for item in successful_products if item.get('company_goods_cd')]
            }

    async def _create_xml_from_transfer_result(self, transfer_result: Dict[str, Any]) -> str:
        """
        transfer_result 기반으로 XML 파일 생성
        Args:
            transfer_result: DB Transfer 결과
        Returns:
            XML 파일 경로
        """
        logger.info("transfer_result 기반 XML 파일 생성 시작")
        
        # transfer_result에서 성공한 상품들의 company_goods_cd 추출
        successful_products = transfer_result.get('success', [])
        if not successful_products:
            logger.warning("XML 생성할 성공한 상품이 없습니다.")
            raise ValueError("전송된 성공한 상품이 없습니다.")
        
        # 성공한 상품들의 company_goods_cd 목록
        company_goods_cds = [item.get('company_goods_cd') for item in successful_products if item.get('company_goods_cd')]
        logger.info(f"XML 생성할 상품 수: {len(company_goods_cds)}")
        
        from core.db import get_async_session
        
        async for session in get_async_session():
            # 서비스 인스턴스 생성
            product_read_service = ProductReadService(session)
            count_executing_service = CountExecutingService(session)
            
            # 특정 company_goods_cd들로 데이터 조회
            product_raw_data_dto_list: List[ProductRawDataDto] = await product_read_service.get_product_raw_data_by_company_goods_cds(company_goods_cds)
            
            if not product_raw_data_dto_list:
                logger.warning("조회된 상품 데이터가 없습니다.")
                raise ValueError("조회된 상품 데이터가 없습니다.")
            
            logger.info(f"XML 변환할 상품 데이터 {len(product_raw_data_dto_list)}개")
            
            # 카운터 증가
            product_create_db_count = await count_executing_service.get_and_increment(CountExecuting, "product_create_db")
            
            # XML 생성
            xml_generator = ProductRegistrationXml()
            xml_file_path = xml_generator.make_product_registration_xml(product_raw_data_dto_list, product_create_db_count)
            
            logger.info(f"XML 파일 생성 완료: {xml_file_path}")
            return xml_file_path

    async def _process_sabang_api_request_with_xml(self, xml_file_path: str, transfer_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        XML 파일을 사용하여 SabangAPI 요청 처리
        Args:
            xml_file_path: 생성된 XML 파일 경로
            transfer_result: DB Transfer 결과
        Returns:
            SabangAPI 요청 결과
        """
        logger.info("XML 기반 SabangAPI 요청 시작")
        
        # transfer_result에서 성공한 상품들의 company_goods_cd 추출
        successful_products = transfer_result.get('success', [])
        company_goods_cds = [item.get('company_goods_cd') for item in successful_products if item.get('company_goods_cd')]
        
        from core.db import get_async_session
        
        async for session in get_async_session():
            product_registration_service = ProductRegistrationService(session)
            
            # XML 파일을 사용하여 SabangAPI 요청
            sabang_result = await product_registration_service.request_product_create_with_xml(xml_file_path)
            
            logger.info(f"SabangAPI 요청 완료: {sabang_result.get('processed_count', 0)}개 상품 처리")
            
            return {
                **sabang_result,
                'requested_company_goods_cds': company_goods_cds,
                'xml_file_path': xml_file_path
            }

    async def process_complete_product_registration_workflow_v2(
        self, 
        file_path: str, 
        sheet_name: str = "상품등록"
    ) -> Dict[str, Any]:
        """
        전체 상품 등록 워크플로우 V2를 처리합니다:
        1. Excel 파일 처리 및 DB 저장
        2. DB Transfer (product_registration_raw_data → test_product_raw_data) - bulk_result 기반
        3. DB to SabangAPI 요청 - transfer_result 기반
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            
        Returns:
            Dict[str, Any]: 전체 프로세스 결과
        """
        try:
            logger.info("전체 상품 등록 워크플로우 V2 시작")
            
            # 1. Excel 파일 처리 및 DB 저장
            excel_result, bulk_result = await self._process_excel_and_db_storage(file_path, sheet_name)
            
            # 2. DB Transfer (product_registration_raw_data → test_product_raw_data) - bulk_result 기반
            transfer_result = await self._process_db_transfer_with_bulk_result(bulk_result)
            
            # 3. DB to SabangAPI 요청 - transfer_result 기반
            sabang_result = await self._process_sabang_api_request_with_transfer_result(transfer_result)
            
            # 전체 결과 반환
            return {
                "success": True,
                "message": "전체 상품 등록 워크플로우 V2 완료",
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
            logger.error(f"전체 상품 등록 워크플로우 V2 오류: {e}")
            return {
                "success": False,
                "message": f"워크플로우 V2 처리 중 오류 발생: {str(e)}",
                "excel_processing": {
                    "total_rows": 0,
                    "valid_rows": 0,
                    "invalid_rows": 0,
                    "validation_errors": [f"워크플로우 V2 오류: {str(e)}"]
                },
                "database_result": {
                    "success_count": 0,
                    "error_count": 0,
                    "created_ids": [],
                    "errors": [f"워크플로우 V2 오류: {str(e)}"]
                },
                "transfer_result": {
                    "success": [],
                    "failed": [f"워크플로우 V2 오류: {str(e)}"]
                },
                "sabang_api_result": {
                    "processed_count": 0,
                    "success_count": 0,
                    "error_count": 0,
                    "errors": [f"워크플로우 V2 오류: {str(e)}"]
                },
                "error": str(e)
            }

    async def process_step_by_step_workflow_v2(
        self, 
        file_path: str, 
        sheet_name: str = "상품등록"
    ) -> Dict[str, Any]:
        """
        단계별 상품 등록 워크플로우 V2를 처리합니다.
        각 단계의 결과를 상세히 반환합니다.
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            
        Returns:
            Dict[str, Any]: 단계별 상세 결과
        """
        try:
            logger.info("단계별 상품 등록 워크플로우 V2 시작")
            
            # 1단계: Excel 파일 처리 및 DB 저장
            logger.info("=== 1단계: Excel 파일 처리 및 DB 저장 ===")
            excel_result, bulk_result = await self._process_excel_and_db_storage(file_path, sheet_name)
            
            # 2단계: DB Transfer (bulk_result 기반)
            logger.info("=== 2단계: DB Transfer (bulk_result 기반) ===")
            transfer_result = await self._process_db_transfer_with_bulk_result(bulk_result)
            
            # 3단계: SabangAPI 요청 (transfer_result 기반)
            logger.info("=== 3단계: SabangAPI 요청 (transfer_result 기반) ===")
            sabang_result = await self._process_sabang_api_request_with_transfer_result(transfer_result)
            
            # 단계별 상세 결과 반환
            return {
                "success": True,
                "message": "단계별 상품 등록 워크플로우 V2 완료",
                "step_1_excel_processing": {
                    "status": "completed",
                    "total_rows": excel_result.total_rows,
                    "valid_rows": excel_result.valid_rows,
                    "invalid_rows": excel_result.invalid_rows,
                    "validation_errors": excel_result.validation_errors,
                    "created_ids_count": len(bulk_result.created_ids)
                },
                "step_2_database_result": {
                    "status": "completed",
                    "success_count": bulk_result.success_count,
                    "error_count": bulk_result.error_count,
                    "created_ids": bulk_result.created_ids,
                    "errors": bulk_result.errors
                },
                "step_3_transfer_result": {
                    "status": "completed",
                    "summary": transfer_result.get('summary', {}),
                    "success_count": len(transfer_result.get('success', [])),
                    "failed_count": len(transfer_result.get('failed', [])),
                    "success_items": transfer_result.get('success', []),
                    "failed_items": transfer_result.get('failed', [])
                },
                "step_4_sabang_api_result": {
                    "status": "completed",
                    "processed_count": sabang_result.get('processed_count', 0),
                    "success_count": sabang_result.get('success_count', 0),
                    "error_count": sabang_result.get('error_count', 0),
                    "requested_company_goods_cds": sabang_result.get('requested_company_goods_cds', []),
                    "sabang_api_result": sabang_result.get('sabang_api_result', {})
                }
            }
            
        except Exception as e:
            logger.error(f"단계별 상품 등록 워크플로우 V2 오류: {e}")
            return {
                "success": False,
                "message": f"단계별 워크플로우 V2 처리 중 오류 발생: {str(e)}",
                "error": str(e),
                "step_1_excel_processing": {"status": "failed", "error": str(e)},
                "step_2_database_result": {"status": "failed", "error": str(e)},
                "step_3_transfer_result": {"status": "failed", "error": str(e)},
                "step_4_sabang_api_result": {"status": "failed", "error": str(e)}
            }
