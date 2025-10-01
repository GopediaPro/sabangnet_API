import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class ProductMallValueLogExcel:
    """ProductMallValue 작업 로그를 Excel로 생성하는 클래스"""

    def __init__(self):
        self._PATH = "./files/excel/product_mall_value_logs"

    def create_log_excel(self, batch_id: str, success_items: List[Dict[str, Any]], 
                        failed_items: List[Dict[str, Any]], 
                        processed_count: int, xml_url: str = None, 
                        product_mall_value_dto: Dict[str, Any] = None) -> str:
        """
        ProductMallValue 작업 로그 Excel 파일 생성
        
        Args:
            batch_id: 배치 ID
            success_items: 성공한 항목들
            failed_items: 실패한 항목들
            processed_count: 처리된 총 개수
            xml_url: XML 파일 URL
            product_mall_value_dto: ProductMallValue DTO 정보
            
        Returns:
            생성된 Excel 파일 경로
        """
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"product_mall_value_log_{batch_id}_{timestamp}.xlsx"
            file_path = Path(self._PATH) / file_name
            
            # 디렉토리 생성
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ExcelWriter 생성
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 요약 정보 시트
                self._create_summary_sheet(writer, batch_id, success_items, failed_items, 
                                         processed_count, xml_url)
                
                # 요청 항목 시트 (ProductMallValue DTO 정보)
                if product_mall_value_dto:
                    self._create_request_sheet(writer, product_mall_value_dto)
                
                # 성공 항목 시트
                if success_items:
                    self._create_success_sheet(writer, success_items)
                
                # 실패 항목 시트
                if failed_items:
                    self._create_failed_sheet(writer, failed_items)
            
            logger.info(f"ProductMallValue 로그 Excel 파일 생성 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"ProductMallValue 로그 Excel 생성 중 오류: {e}")
            raise

    def _create_summary_sheet(self, writer, batch_id: str, success_items: List[Dict[str, Any]], 
                            failed_items: List[Dict[str, Any]], processed_count: int, xml_url: str = None):
        """요약 정보 시트 생성"""
        summary_data = {
            '항목': [
                '배치 ID',
                '처리 일시',
                '총 처리 개수',
                '성공 개수',
                '실패 개수',
                '성공률 (%)',
                'XML 파일 URL'
            ],
            '값': [
                batch_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                processed_count,
                len(success_items),
                len(failed_items),
                round((len(success_items) / processed_count * 100), 2) if processed_count > 0 else 0,
                xml_url or "N/A"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='요약', index=False)

    def _create_request_sheet(self, writer, product_mall_value_dto: Dict[str, Any]):
        """요청 항목 시트 생성 (ProductMallValue DTO 정보)"""
        try:
            # 기본 정보
            basic_info = {
                '항목': [
                    '상품코드 (COMPAYNY_GOODS_CD)',
                    '구분 (GUBUN)',
                    '표준가격 (STANDARD_PRICE)',
                    '상품명 (PRODUCT_NM)',
                    'Product Raw Data ID',
                    '생성일시'
                ],
                '값': [
                    product_mall_value_dto.get('compayny_goods_cd', 'N/A'),
                    product_mall_value_dto.get('gubun', 'N/A'),
                    product_mall_value_dto.get('standard_price', 'N/A'),
                    product_mall_value_dto.get('product_nm', 'N/A'),
                    product_mall_value_dto.get('product_raw_data_id', 'N/A'),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            
            # 추가 필드들 (kwargs로 전달된 필드들)
            additional_fields = [
                'mall_prod_name', 'mall_prop1_cd', 'buinf_id3', 'mall_stock_rate',
                'certno', 'issuedate', 'certdate', 'avlst_dm', 'avled_dm',
                'cert_agency', 'certfield'
            ]
            
            for field in additional_fields:
                if field in product_mall_value_dto and product_mall_value_dto[field] is not None:
                    basic_info['항목'].append(f'{field.upper()}')
                    basic_info['값'].append(str(product_mall_value_dto[field]))
            
            # JSONB shops 데이터 정보
            shops_data = product_mall_value_dto.get('shops', {})
            if shops_data:
                basic_info['항목'].append('생성된 Shop 개수')
                basic_info['값'].append(len(shops_data))
                
                basic_info['항목'].append('Shop별 상세 정보')
                shop_details = []
                for shop_code, shop_info in shops_data.items():
                    mall_price = shop_info.get('mall_price', 'N/A')
                    product_nm = shop_info.get('product_nm', 'N/A')
                    shop_details.append(f"{shop_code}: 가격={mall_price}, 상품명={product_nm}")
                basic_info['값'].append('\n'.join(shop_details))
            
            df_basic = pd.DataFrame(basic_info)
            df_basic.to_excel(writer, sheet_name='요청항목', index=False)
            
            # Shop별 상세 정보를 별도 시트로 생성
            if shops_data:
                shop_details_data = []
                for shop_code, shop_info in shops_data.items():
                    shop_details_data.append({
                        'Shop 코드': shop_code,
                        '쇼핑몰 가격': shop_info.get('mall_price', 'N/A'),
                        '상품명': shop_info.get('product_nm', 'N/A')
                    })
                
                df_shop_details = pd.DataFrame(shop_details_data)
                df_shop_details.to_excel(writer, sheet_name='Shop별상세정보', index=False)
                
        except Exception as e:
            logger.error(f"요청 항목 시트 생성 중 오류: {e}")
            # 오류 발생 시 기본 정보만 표시
            error_data = {
                '항목': ['오류'],
                '값': [f'요청 항목 시트 생성 중 오류 발생: {str(e)}']
            }
            df_error = pd.DataFrame(error_data)
            df_error.to_excel(writer, sheet_name='요청항목', index=False)

    def _create_success_sheet(self, writer, success_items: List[Dict[str, Any]]):
        """성공 항목 시트 생성"""
        if not success_items:
            return
            
        # 성공 항목을 DataFrame으로 변환
        df_success = pd.DataFrame(success_items)
        df_success.to_excel(writer, sheet_name='성공항목', index=False)

    def _create_failed_sheet(self, writer, failed_items: List[Dict[str, Any]]):
        """실패 항목 시트 생성"""
        if not failed_items:
            return
            
        # 실패 항목을 DataFrame으로 변환
        df_failed = pd.DataFrame(failed_items)
        df_failed.to_excel(writer, sheet_name='실패항목', index=False)
