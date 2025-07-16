# std
from pprint import pformat
from pathlib import Path
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# model
from models.count_executing_data.count_executing_data import CountExecuting
# utils
from utils.logs.sabangnet_logger import get_logger
from utils.make_xml.product_registration_xml import ProductRegistrationXml
# service
from services.count_excuting_service import CountExecutingService
from services.product.product_read_service import ProductReadService
from services.product.product_update_service import ProductUpdateService
# schema
from schemas.product.product_raw_data_dto import ProductRawDataDto


logger = get_logger(__name__)


class ProductDbXmlUsecase:
    """
    DB 데이터를 XML로 변환하는 서비스
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_read_service = ProductReadService(session)
        self.product_update_service = ProductUpdateService(session)
        self.count_executing_service = CountExecutingService(session)

    async def db_to_xml_file_all(self) -> str | Path:
        """
        test_product_raw_data 테이블의 모든 데이터를 XML 파일로 변환
        Returns:
            XML 파일 경로
        """
        try:
            product_raw_data_dto_list: list[ProductRawDataDto] = await self.product_read_service.get_product_raw_data_all()
            if not product_raw_data_dto_list:
                raise ValueError("변환할 상품 데이터가 없습니다.")
            
            logger.info(f"전체 상품 데이터 {len(product_raw_data_dto_list)}개를 XML로 변환 시작")
            logger.info(f"전체 상품 데이터 확인용: {product_raw_data_dto_list}")
            logger.debug(f"전체 상품 데이터 상세 내용:\n{pformat(product_raw_data_dto_list)}")
            product_create_db_count = await self.count_executing_service.get_and_increment(CountExecuting, "product_create_db")
            xml_generator = ProductRegistrationXml()
            xml_file_path = xml_generator.make_product_registration_xml(product_raw_data_dto_list, product_create_db_count)
            return xml_file_path
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류: {e}")
            raise

    async def get_product_raw_data_count(self) -> int:
        """
        test_product_raw_data 테이블 총 개수 조회
        Returns:
            총 개수
        """
        try:
            return await self.product_read_service.get_product_raw_data_count()
        except Exception as e:
            logger.error(f"상품 데이터 개수 조회 중 오류: {e}")
            raise 

    async def update_product_id_by_compayny_goods_cd(self, compayny_goods_cd_and_product_ids: list[tuple[str, int]]):
        for compayny_goods_cd, product_id in compayny_goods_cd_and_product_ids:
            await self.product_update_service.update_product_id_by_compayny_goods_cd(compayny_goods_cd, product_id)