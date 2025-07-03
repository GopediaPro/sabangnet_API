from pathlib import Path
from typing import List, Optional
from utils.sabangnet_logger import get_logger
from utils.product_create.db_processor import DbProcessor
from repository.product_repository import ProductRepository
from models.product.product_raw_data import ProductRawData
from core.db import get_async_session

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
            async with get_async_session() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_all()
                
                if not product_data_list:
                    raise ValueError("변환할 상품 데이터가 없습니다.")
                
                logger.info(f"전체 상품 데이터 {len(product_data_list)}개를 XML로 변환 시작")
                return DbProcessor.db_to_xml_file(product_data_list)
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류: {e}")
            raise

    @staticmethod
    async def db_to_xml_file_by_gubun(gubun: str) -> str | Path:
        """
        gubun(몰구분)별 데이터를 XML 파일로 변환
        Args:
            gubun: 몰구분 (마스터, 전문몰, 1+1)
        Returns:
            XML 파일 경로
        """
        try:
            async with get_async_session() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_by_gubun(gubun)
                
                if not product_data_list:
                    raise ValueError(f"gubun '{gubun}'에 해당하는 상품 데이터가 없습니다.")
                
                logger.info(f"gubun '{gubun}' 상품 데이터 {len(product_data_list)}개를 XML로 변환 시작")
                return DbProcessor.db_to_xml_file(product_data_list)
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류 (gubun: {gubun}): {e}")
            raise

    @staticmethod
    async def db_to_xml_file_by_ids(ids: List[int]) -> str | Path:
        """
        ID 리스트로 데이터를 XML 파일로 변환
        Args:
            ids: 변환할 상품 ID 리스트
        Returns:
            XML 파일 경로
        """
        try:
            async with get_async_session() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_by_ids(ids)
                
                if not product_data_list:
                    raise ValueError(f"ID {ids}에 해당하는 상품 데이터가 없습니다.")
                
                logger.info(f"ID {ids} 상품 데이터 {len(product_data_list)}개를 XML로 변환 시작")
                return DbProcessor.db_to_xml_file(product_data_list)
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류 (IDs: {ids}): {e}")
            raise

    @staticmethod
    async def db_to_xml_file_by_product_nm(product_nm: str) -> str | Path:
        """
        상품명으로 데이터를 XML 파일로 변환
        Args:
            product_nm: 상품명 (부분 검색)
        Returns:
            XML 파일 경로
        """
        try:
            async with get_async_session() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_by_product_nm(product_nm)
                
                if not product_data_list:
                    raise ValueError(f"상품명 '{product_nm}'에 해당하는 상품 데이터가 없습니다.")
                
                logger.info(f"상품명 '{product_nm}' 상품 데이터 {len(product_data_list)}개를 XML로 변환 시작")
                return DbProcessor.db_to_xml_file(product_data_list)
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류 (상품명: {product_nm}): {e}")
            raise

    @staticmethod
    async def db_to_xml_file_pagination(skip: int = 0, limit: int = 10) -> str | Path:
        """
        페이징으로 데이터를 XML 파일로 변환
        Args:
            skip: 건너뛸 개수
            limit: 조회할 개수
        Returns:
            XML 파일 경로
        """
        try:
            async with get_async_session() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_pagination(skip, limit)
                
                if not product_data_list:
                    raise ValueError(f"페이징 조건(skip: {skip}, limit: {limit})에 해당하는 상품 데이터가 없습니다.")
                
                logger.info(f"페이징(skip: {skip}, limit: {limit}) 상품 데이터 {len(product_data_list)}개를 XML로 변환 시작")
                return DbProcessor.db_to_xml_file(product_data_list)
                
        except Exception as e:
            logger.error(f"DB to XML 변환 중 오류 (페이징 skip: {skip}, limit: {limit}): {e}")
            raise

    @staticmethod
    async def db_to_xml_string_all() -> str:
        """
        test_product_raw_data 테이블의 모든 데이터를 XML 문자열로 변환
        Returns:
            XML 문자열
        """
        try:
            async with get_async_session() as session:
                repo = ProductRepository(session)
                product_data_list = await repo.get_product_raw_data_all()
                
                if not product_data_list:
                    raise ValueError("변환할 상품 데이터가 없습니다.")
                
                logger.info(f"전체 상품 데이터 {len(product_data_list)}개를 XML 문자열로 변환 시작")
                return DbProcessor.db_to_xml_string(product_data_list)
                
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
            async with get_async_session() as session:
                repo = ProductRepository(session)
                return await repo.count_product_raw_data()
        except Exception as e:
            logger.error(f"상품 데이터 개수 조회 중 오류: {e}")
            raise 