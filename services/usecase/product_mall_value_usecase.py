from sqlalchemy.ext.asyncio import AsyncSession
from services.count_excuting_service import CountExecutingService
from services.product.product_read_service import ProductReadService
from services.product.product_mall_value_write_service import ProductMallValueWriteService
from services.batch_process.batch_process_write_service import BatchProcessWriteService
from services.mall_price.mall_price_request_service import MallPriceRequestService
from utils.logs.sabangnet_logger import get_logger
from utils.mall_price_response_parser import parse_sabangnet_response
from utils.make_xml.product_mall_value_registration_xml import ProductMallValueRegistrationXml
from utils.excel.product_mall_value_log_excel import ProductMallValueLogExcel
from models.count_executing_data.count_executing_data import CountExecuting
from minio_handler import upload_and_get_url_with_count_rev
from schemas.mall_price.product_mall_value_dto import ProductMallValueDto
import uuid


logger = get_logger(__name__)


class ProductMallValueUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_mall_value_write_service = ProductMallValueWriteService(session)
        self.batch_process_write_service = BatchProcessWriteService(session)
        self.count_executing_service = CountExecutingService(session)
        self.product_read_service = ProductReadService(session)
        self.product_mall_value_registration_xml = ProductMallValueRegistrationXml()
        self.mall_price_request_service = MallPriceRequestService()
        self.log_excel = ProductMallValueLogExcel()

    async def setting_product_mall_value(self, compayny_goods_cd: str, gubun: str, request_id: str = None, standard_price: int = None, **kwargs) -> dict:
        """ProductMallValue 설정 및 전체 플로우 실행"""
        try:
            # 배치 ID 생성
            batch_id = str(uuid.uuid4())
            
            # 상품 정보 조회
            product_raw_data_dto = await self.product_read_service.\
                get_product_by_compayny_goods_cd_gubun(compayny_goods_cd=compayny_goods_cd, gubun=gubun)
            
            # standard_price 결정: 요청에 있으면 사용, 없으면 DB에서 가져온 값 사용
            final_standard_price = standard_price if standard_price is not None else int(product_raw_data_dto.goods_price)
            
            # ProductMallValue 설정 및 DB upsert
            # **kwargs에는 다음 필드들이 포함될 수 있음:
            # - mall_prod_name: 쇼핑몰 상품명
            # - mall_prop1_cd: 쇼핑몰 속성1 코드
            # - buinf_id3: 사업자 정보 ID3
            # - mall_stock_rate: 쇼핑몰 재고율
            # - certno: 인증번호
            # - issuedate: 발급일
            # - certdate: 인증일
            # - avlst_dm: 유효시작일
            # - avled_dm: 유효종료일
            # - cert_agency: 인증기관
            # - certfield: 인증분야
            product_mall_value_dto = await self.product_mall_value_write_service.\
                setting_product_mall_value(
                    product_raw_data_id=product_raw_data_dto.id,
                    standard_price=final_standard_price,
                    product_nm=product_raw_data_dto.product_nm,
                    compayny_goods_cd=compayny_goods_cd,
                    gubun=gubun,
                    batch_id=batch_id,
                    **kwargs
                )
            # XML 생성
            product_mall_value_create_db_count = await self.count_executing_service.get_and_increment(
                CountExecuting, "product_mall_value_create_db"
            )
            
            # JSONB shops 데이터 로깅
            shops_data = product_mall_value_dto.shops or {}
            logger.info(f"ProductMallValue DTO 정보 - 상품코드: {compayny_goods_cd}, 구분: {gubun}")
            logger.info(f"생성된 shops 데이터 개수: {len(shops_data)}")
            for shop_code, shop_info in shops_data.items():
                logger.debug(f"  {shop_code}: 가격={shop_info.get('mall_price')}, 상품명={shop_info.get('product_nm')}")
            
            logger.info(f"XML 생성 시작 - count_rev: {product_mall_value_create_db_count}")
            
            xml_file_path = self.product_mall_value_registration_xml.make_product_mall_value_registration_xml(
                product_mall_value_dto=product_mall_value_dto,
                count_rev=product_mall_value_create_db_count
            )
            
            logger.info(f"XML 파일 생성 완료: {xml_file_path}")
            
            # MinIO 업로드 (upload_and_get_url_with_count_rev 사용)
            # 파일명에서 공백과 특수문자 제거 (XML 생성과 동일하게)
            safe_company_goods_cd = compayny_goods_cd.replace(' ', '_').replace('+', 'plus').replace('-', '_')
            xml_url, minio_object_name, file_size = upload_and_get_url_with_count_rev(
                file_path=xml_file_path,
                template_code="product_mall_value",
                file_name=f"{safe_company_goods_cd}_product_mall_value_registration.xml",
                count_rev=product_mall_value_create_db_count
            )
            
            logger.info(f"MinIO에 업로드된 XML 파일: {minio_object_name}, URL: {xml_url}, 크기: {file_size}")
            # 사방넷 API 호출
            response_text = self.mall_price_request_service.request_sabangnet_product_update(xml_url)
            success_items, failed_items = parse_sabangnet_response(response_text)
            processed_count = len(success_items) + len(failed_items)
            
            # BatchProcess DB에 배치 정보 저장 (먼저 저장하여 실제 batch_id 획득)
            batch_process = await self.batch_process_write_service.create_product_mall_value_batch(
                compayny_goods_cd=compayny_goods_cd,
                gubun=gubun,
                created_by=request_id or "system"
            )
            
            # Excel 로그 생성 (실제 BatchProcess batch_id 사용)
            excel_file_path = self.log_excel.create_log_excel(
                batch_id=batch_process.batch_id,  # 실제 BatchProcess batch_id 사용
                success_items=success_items,  # 실제 사방넷 API 응답 데이터
                failed_items=failed_items,    # 실제 사방넷 API 응답 데이터
                processed_count=processed_count,
                xml_url=xml_url,
                product_mall_value_dto=product_mall_value_dto.model_dump()  # ProductMallValue DTO 정보 추가
            )
            
            # Excel 파일도 MinIO에 업로드
            excel_url, excel_object_name, excel_file_size = upload_and_get_url_with_count_rev(
                file_path=excel_file_path,
                template_code="product_mall_value_logs",
                file_name=f"product_mall_value_log_{safe_company_goods_cd}_{batch_process.batch_id}.xlsx",
                count_rev=product_mall_value_create_db_count
            )
            
            logger.info(f"MinIO에 업로드된 Excel 로그 파일: {excel_object_name}, URL: {excel_url}, 크기: {excel_file_size}")
            
            # BatchProcess의 모든 정보 업데이트
            await self.batch_process_write_service.update_batch_process_info(
                batch_id=batch_process.batch_id,
                xml_url=xml_url,
                excel_url=excel_url,
                file_size=file_size,
                excel_file_size=excel_file_size,
                total_records=processed_count,
                success_records=len(success_items),
                fail_records=len(failed_items)
            )
            
            logger.info(f"BatchProcess 저장 완료: batch_id={batch_process.batch_id}")
            
            return {
                "success": True,
                "message": "ProductMallValue 설정 및 처리 완료",
                "batch_id": batch_process.batch_id,  # BatchProcess 모델의 실제 batch_id 사용
                "xml_file_path": xml_url,
                "excel_log_url": excel_url,
                "processed_count": processed_count,
                "success_items": [],
                "failed_items": [],
                "product_mall_value": product_mall_value_dto.model_dump(),
                "shops_summary": {
                    "total_shops": len(shops_data),
                    "shops_with_data": len([shop for shop in shops_data.values() if shop.get('mall_price') is not None])
                }
            }
            
        except Exception as e:
            logger.error(f"ProductMallValue 설정 중 오류: {e}")
            raise
