"""
상품 등록 워크플로우 매니저

기존 상품 등록 워크플로우와 ProductMallValue 설정을 통합하여 관리하는 매니저 클래스
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from services.product_registration.product_integrated_service_v2 import ProductCodeIntegratedServiceV2
from services.usecase.product_mall_value_usecase import ProductMallValueUsecase

logger = get_logger(__name__)


class ProductRegistrationWorkflowManager:
    """상품 등록 워크플로우 매니저"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_integrated_service = ProductCodeIntegratedServiceV2()
        self.product_mall_value_usecase = ProductMallValueUsecase(session)
    
    async def process_complete_workflow(self, file_path: str, sheet_name: str = "상품등록") -> Dict[str, Any]:
        """
        기존 상품 등록 워크플로우 실행
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            
        Returns:
            Dict[str, Any]: 상품 등록 워크플로우 결과
        """
        logger.info("기존 상품 등록 워크플로우 시작")
        
        try:
            result = await self.product_integrated_service.process_complete_product_registration_workflow_v2(
                file_path=file_path,
                sheet_name=sheet_name
            )
            
            logger.info(f"기존 상품 등록 워크플로우 완료: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"기존 상품 등록 워크플로우 오류: {e}")
            raise
    
    async def process_mall_value_setting(self, registered_products: List[Dict[str, Any]], request_id: str = None) -> Dict[str, Any]:
        """
        등록된 상품들에 대해 ProductMallValue 설정 실행
        
        Args:
            registered_products: 등록된 상품 목록 (transfer_result의 success 항목들)
            request_id: 요청자 ID
            
        Returns:
            Dict[str, Any]: ProductMallValue 설정 결과
        """
        logger.info(f"ProductMallValue 설정 시작: {len(registered_products)}개 상품")
        
        if not registered_products:
            logger.warning("설정할 상품이 없습니다.")
            return {
                "success": True,
                "message": "설정할 상품이 없습니다.",
                "processed_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "success_items": [],
                "failed_items": []
            }
        
        success_items = []
        failed_items = []
        
        for product in registered_products:
            try:
                compayny_goods_cd = product.get('company_goods_cd')
                gubun = product.get('gubun')
                product_nm = product.get('product_nm')
                
                if not compayny_goods_cd or not gubun:
                    failed_items.append({
                        'product_nm': product_nm,
                        'gubun': gubun,
                        'company_goods_cd': compayny_goods_cd,
                        'error': 'company_goods_cd 또는 gubun이 없습니다.'
                    })
                    continue
                
                logger.info(f"ProductMallValue 설정 중: {compayny_goods_cd} ({gubun})")
                
                # 1+1 상품의 경우 특별한 상품명 패턴 적용됨을 로깅
                if gubun == "1+1":
                    logger.info(f"1+1 상품 감지: {compayny_goods_cd} - 각 shop별로 다른 상품명 패턴 적용 예정")
                
                # ProductMallValue 설정 실행 (JSONB 구조로 shops 데이터 생성)
                result = await self.product_mall_value_usecase.setting_product_mall_value(
                    compayny_goods_cd=compayny_goods_cd,
                    gubun=gubun,
                    request_id=request_id
                )
                
                if result.get('success', False):
                    # JSONB shops 데이터 요약 정보 추가
                    shops_summary = result.get('shops_summary', {})
                    product_mall_value = result.get('product_mall_value', {})
                    shops_data = product_mall_value.get('shops', {})
                    
                    success_items.append({
                        'product_nm': product_nm,
                        'gubun': gubun,
                        'company_goods_cd': compayny_goods_cd,
                        'batch_id': str(result.get('batch_id', '')),  # 문자열로 변환
                        'xml_file_path': result.get('xml_file_path'),
                        'excel_log_url': result.get('excel_log_url'),
                        'processed_count': result.get('processed_count'),
                        'success_items': [],  # MallValueSettingItem의 success_items는 빈 리스트
                        'failed_items': [],   # MallValueSettingItem의 failed_items는 빈 리스트
                        'shops_summary': shops_summary,  # JSONB shops 요약 정보
                        'shops_count': len(shops_data)  # 생성된 shops 개수
                    })
                    
                    # JSONB shops 데이터 로깅 (debug 레벨)
                    logger.debug(f"생성된 shops 데이터 ({compayny_goods_cd}): {len(shops_data)}개 shop")
                    
                    # 1+1 상품의 경우 상품명 패턴 분석
                    if gubun == "1+1":
                        special_pattern_shops = []
                        default_pattern_shops = []
                        
                        for shop_code, shop_info in shops_data.items():
                            product_nm = shop_info.get('product_nm', '')
                            if product_nm.startswith('2개세트') or product_nm.startswith('[1개+1개]'):
                                special_pattern_shops.append(f"{shop_code}: {product_nm}")
                            else:
                                default_pattern_shops.append(f"{shop_code}: {product_nm}")
                        
                        if special_pattern_shops:
                            logger.debug(f"  1+1 특별 패턴 적용된 shop들: {special_pattern_shops}")
                        if default_pattern_shops:
                            logger.debug(f"  원본 상품명 사용 shop들: {default_pattern_shops}")
                    else:
                        # 일반 상품의 경우
                        for shop_code, shop_info in shops_data.items():
                            logger.debug(f"  {shop_code}: 가격={shop_info.get('mall_price')}, 상품명={shop_info.get('product_nm')}")
                else:
                    failed_items.append({
                        'product_nm': product_nm,
                        'gubun': gubun,
                        'company_goods_cd': compayny_goods_cd,
                        'success_items': [],  # MallValueSettingItem의 success_items는 빈 리스트
                        'failed_items': [],   # MallValueSettingItem의 failed_items는 빈 리스트
                        'error': result.get('message', '알 수 없는 오류')
                    })
                    
            except Exception as e:
                logger.error(f"ProductMallValue 설정 중 오류 ({product.get('product_nm', 'Unknown')}): {e}")
                failed_items.append({
                    'product_nm': product.get('product_nm'),
                    'gubun': product.get('gubun'),
                    'company_goods_cd': product.get('company_goods_cd'),
                    'success_items': [],  # MallValueSettingItem의 success_items는 빈 리스트
                    'failed_items': [],   # MallValueSettingItem의 failed_items는 빈 리스트
                    'error': str(e)
                })
        
        processed_count = len(success_items) + len(failed_items)
        
        # JSONB shops 데이터 전체 요약 계산
        total_shops_created = sum(item.get('shops_count', 0) for item in success_items)
        total_shops_with_data = sum(
            item.get('shops_summary', {}).get('shops_with_data', 0) 
            for item in success_items
        )
        
        # success_items와 failed_items의 실제 개수 계산 (빈 리스트이므로 0으로 설정)
        total_success_items = 0
        total_failed_items = 0
        
        logger.info(f"ProductMallValue 설정 완료: 성공 {len(success_items)}개, 실패 {len(failed_items)}개")
        logger.info(f"사방넷 API 처리 결과: 성공 {total_success_items}개, 실패 {total_failed_items}개")
        logger.info(f"JSONB shops 데이터 요약: 총 {total_shops_created}개 shop 생성, {total_shops_with_data}개 shop에 데이터 저장")
        
        return {
            "success": len(failed_items) == 0,  # 모든 상품이 성공했을 때만 True
            "message": f"ProductMallValue 설정 완료: 성공 {len(success_items)}개, 실패 {len(failed_items)}개",
            "processed_count": processed_count,
            "success_count": len(success_items),
            "failed_count": len(failed_items),
            "success_items": success_items,
            "failed_items": failed_items,
            "shops_summary": {
                "total_shops_created": total_shops_created,
                "total_shops_with_data": total_shops_with_data,
                "average_shops_per_product": total_shops_created / len(success_items) if success_items else 0
            },
            "sabangnet_api_summary": {
                "total_success_items": total_success_items,
                "total_failed_items": total_failed_items,
                "total_processed_items": total_success_items + total_failed_items
            }
        }
    
    async def execute_full_workflow(
        self, 
        file_path: str, 
        sheet_name: str = "상품등록",
        request_id: str = None,
        enable_mall_value_setting: bool = True
    ) -> Dict[str, Any]:
        """
        전체 워크플로우 실행 (상품 등록 + ProductMallValue 설정)
        
        Args:
            file_path: Excel 파일 경로
            sheet_name: 시트명
            request_id: 요청자 ID
            enable_mall_value_setting: ProductMallValue 설정 활성화 여부
            
        Returns:
            Dict[str, Any]: 전체 워크플로우 결과
        """
        logger.info("전체 워크플로우 시작")
        
        try:
            # 1단계: 기존 상품 등록 워크플로우 실행
            logger.info("=== 1단계: 상품 등록 워크플로우 실행 ===")
            product_registration_result = await self.process_complete_workflow(file_path, sheet_name)
            
            if not product_registration_result.get('success', False):
                logger.error("상품 등록 워크플로우 실패")
                return {
                    "success": False,
                    "message": "상품 등록 워크플로우 실패",
                    "product_registration": product_registration_result,
                    "mall_value_setting": {
                        "success": False,
                        "message": "상품 등록 실패로 인해 ProductMallValue 설정을 건너뜀",
                        "processed_count": 0,
                        "success_count": 0,
                        "failed_count": 0,
                        "success_items": [],
                        "failed_items": []
                    },
                    "overall_success": False
                }
            
            # 2단계: ProductMallValue 설정 (옵션)
            mall_value_setting_result = {
                "success": True,
                "message": "ProductMallValue 설정이 비활성화됨",
                "processed_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "success_items": [],
                "failed_items": []
            }
            
            if enable_mall_value_setting:
                logger.info("=== 2단계: ProductMallValue 설정 실행 ===")
                
                # transfer_result에서 성공한 상품들 추출
                transfer_result = product_registration_result.get('transfer_result', {})
                successful_products = transfer_result.get('success', [])
                
                if successful_products:
                    mall_value_setting_result = await self.process_mall_value_setting(
                        registered_products=successful_products,
                        request_id=request_id
                    )
                else:
                    mall_value_setting_result = {
                        "success": True,
                        "message": "전송된 성공한 상품이 없어 ProductMallValue 설정을 건너뜀",
                        "processed_count": 0,
                        "success_count": 0,
                        "failed_count": 0,
                        "success_items": [],
                        "failed_items": []
                    }
            
            # 전체 성공 여부 결정
            overall_success = (
                product_registration_result.get('success', False) and 
                mall_value_setting_result.get('success', False)
            )
            
            # JSONB shops 데이터 전체 요약
            mall_value_shops_summary = mall_value_setting_result.get('shops_summary', {})
            mall_value_sabangnet_summary = mall_value_setting_result.get('sabangnet_api_summary', {})
            
            logger.info(f"전체 워크플로우 완료: {overall_success}")
            logger.info(f"전체 JSONB shops 데이터 요약: {mall_value_shops_summary}")
            logger.info(f"전체 사방넷 API 처리 요약: {mall_value_sabangnet_summary}")
            
            return {
                "success": overall_success,
                "message": "전체 워크플로우 완료",
                "product_registration": product_registration_result,
                "mall_value_setting": mall_value_setting_result,
                "overall_success": overall_success,
                "shops_summary": mall_value_shops_summary,  # JSONB shops 전체 요약
                "sabangnet_api_summary": mall_value_sabangnet_summary  # 사방넷 API 전체 요약
            }
            
        except Exception as e:
            logger.error(f"전체 워크플로우 오류: {e}")
            return {
                "success": False,
                "message": f"전체 워크플로우 처리 중 오류 발생: {str(e)}",
                "product_registration": {
                    "success": False,
                    "message": f"워크플로우 오류: {str(e)}"
                },
                "mall_value_setting": {
                    "success": False,
                    "message": f"워크플로우 오류: {str(e)}"
                },
                "overall_success": False,
                "error": str(e)
            }
