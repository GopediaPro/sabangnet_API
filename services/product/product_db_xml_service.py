from pathlib import Path
from typing import List, Optional
from utils.sabangnet_logger import get_logger
from utils.product_create.db_processor import DbProcessor
from repository.product_repository import ProductRepository
from models.product.product_raw_data import ProductRawData
from core.db import get_async_session
from repository.product_repository import ProductRepository
from models.product.product_raw_data import ProductRawData
from core.db import AsyncSessionLocal
from repository.count_executing_repository import CountExecutingRepository
from models.count_executing_data import CountExecuting
from utils.make_xml.product_registration_xml import ProductRegistrationXml
from pprint import pformat


logger = get_logger(__name__)


class ProductDbXmlService:
    """
    DB 데이터를 XML로 변환하는 서비스
    """

    @staticmethod
    async def db_to_xml_file_all() -> str | Path:
        """
        test_product_raw_data 테이블의 모든 데이터를 XML 파일로 변환
        Returns:
            XML 파일 경로
        """
        try:
            async with AsyncSessionLocal() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_all()
                
                if not product_data_list:
                    raise ValueError("변환할 상품 데이터가 없습니다.")
                
                logger.info(f"전체 상품 데이터 {len(product_data_list)}개를 XML로 변환 시작")
                logger.info(f"전체 상품 데이터 확인용: {product_data_list}")
                logger.debug(f"전체 상품 데이터 상세 내용:\n{pformat(product_data_list)}")
                count_repo = CountExecutingRepository(session)
                product_create_db_count = await count_repo.get_and_increment(CountExecuting, "product_create_db", id_value=1)
                xml_generator = ProductRegistrationXml()
                xml_file_path = xml_generator.make_product_registration_xml(product_data_list, product_create_db_count)
                return xml_file_path
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류: {e}")
            raise

    @staticmethod
    async def get_product_raw_data_count() -> int:
        """
        test_product_raw_data 테이블 총 개수 조회
        Returns:
            총 개수
        """
        try:
            async with AsyncSessionLocal() as session:
                repo = ProductRepository(session)
                return await repo.count_product_raw_data()
        except Exception as e:
            logger.error(f"상품 데이터 개수 조회 중 오류: {e}")
            raise 