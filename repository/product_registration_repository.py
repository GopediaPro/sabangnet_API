"""
Product Registration Repository
상품 등록 데이터 저장소 클래스
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from decimal import Decimal

from models.product.product_registration_data import ProductRegistrationRawData
from schemas.product_registration import ProductRegistrationCreateDto
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)


class ProductRegistrationRepository:
    """상품 등록 데이터 저장소 클래스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_single(self, data: ProductRegistrationCreateDto) -> ProductRegistrationRawData:
        """
        단일 상품 등록 데이터를 생성합니다.
        
        Args:
            data: 생성할 데이터 DTO
            
        Returns:
            ProductRegistrationRawData: 생성된 데이터
            
        Raises:
            SQLAlchemyError: 데이터베이스 오류
        """
        try:
            # DTO를 딕셔너리로 변환
            data_dict = data.dict(exclude_unset=True, exclude_none=True)
            
            # 새 인스턴스 생성
            db_instance = ProductRegistrationRawData(**data_dict)
            
            # 세션에 추가
            self.session.add(db_instance)
            await self.session.flush()  # ID 할당을 위해 flush
            await self.session.refresh(db_instance)  # 최신 데이터로 새로고침
            
            logger.info(f"상품 등록 데이터 생성 완료: ID={db_instance.id}")
            return db_instance
            
        except IntegrityError as e:
            logger.error(f"데이터 무결성 오류: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"알 수 없는 오류: {e}")
            raise
    
    async def create_bulk(self, data_list: List[ProductRegistrationCreateDto]) -> List[int]:
        """
        대량 상품 등록 데이터를 생성합니다.
        
        Args:
            data_list: 생성할 데이터 DTO 리스트
            
        Returns:
            List[int]: 생성된 데이터의 ID 리스트
            
        Raises:
            SQLAlchemyError: 데이터베이스 오류
        """
        try:
            if not data_list:
                return []
            
            # DTO 리스트를 딕셔너리 리스트로 변환
            data_dicts = [
                data.dict(exclude_unset=True, exclude_none=True) 
                for data in data_list
            ]
            
            # 대량 삽입 실행
            stmt = insert(ProductRegistrationRawData).returning(ProductRegistrationRawData.id)
            result = await self.session.execute(stmt, data_dicts)
            
            # 생성된 ID 리스트 반환
            created_ids = [row[0] for row in result.fetchall()]
            
            logger.info(f"대량 상품 등록 데이터 생성 완료: {len(created_ids)}개")
            return created_ids
            
        except IntegrityError as e:
            logger.error(f"데이터 무결성 오류: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"알 수 없는 오류: {e}")
            raise
    
    async def get_by_id(self, id: int) -> Optional[ProductRegistrationRawData]:
        """
        ID로 상품 등록 데이터를 조회합니다.
        
        Args:
            id: 조회할 데이터 ID
            
        Returns:
            Optional[ProductRegistrationRawData]: 조회된 데이터 또는 None
        """
        try:
            stmt = select(ProductRegistrationRawData).where(ProductRegistrationRawData.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"데이터 조회 오류: {e}")
            raise
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ProductRegistrationRawData]:
        """
        모든 상품 등록 데이터를 조회합니다.
        
        Args:
            limit: 조회할 데이터 수 제한
            offset: 조회 시작 위치
            
        Returns:
            List[ProductRegistrationRawData]: 조회된 데이터 리스트
        """
        try:
            stmt = (
                select(ProductRegistrationRawData)
                .offset(offset)
                .limit(limit)
                .order_by(ProductRegistrationRawData.created_at.desc())
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"데이터 목록 조회 오류: {e}")
            raise
    
    async def update_by_id(self, id: int, data: ProductRegistrationCreateDto) -> Optional[ProductRegistrationRawData]:
        """
        ID로 상품 등록 데이터를 업데이트합니다.
        
        Args:
            id: 업데이트할 데이터 ID
            data: 업데이트할 데이터 DTO
            
        Returns:
            Optional[ProductRegistrationRawData]: 업데이트된 데이터 또는 None
        """
        try:
            # 업데이트할 데이터 딕셔너리 생성
            update_data = data.dict(exclude_unset=True, exclude_none=True)
            
            if not update_data:
                # 업데이트할 데이터가 없으면 기존 데이터 반환
                return await self.get_by_id(id)
            
            # 업데이트 실행
            stmt = (
                update(ProductRegistrationRawData)
                .where(ProductRegistrationRawData.id == id)
                .values(**update_data)
                .returning(ProductRegistrationRawData)
            )
            
            result = await self.session.execute(stmt)
            updated_data = result.scalar_one_or_none()
            
            if updated_data:
                logger.info(f"상품 등록 데이터 업데이트 완료: ID={id}")
            
            return updated_data
            
        except SQLAlchemyError as e:
            logger.error(f"데이터 업데이트 오류: {e}")
            raise
    
    async def delete_by_id(self, id: int) -> bool:
        """
        ID로 상품 등록 데이터를 삭제합니다.
        
        Args:
            id: 삭제할 데이터 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            stmt = delete(ProductRegistrationRawData).where(ProductRegistrationRawData.id == id)
            result = await self.session.execute(stmt)
            
            deleted = result.rowcount > 0
            if deleted:
                logger.info(f"상품 등록 데이터 삭제 완료: ID={id}")
            
            return deleted
            
        except SQLAlchemyError as e:
            logger.error(f"데이터 삭제 오류: {e}")
            raise
    
    async def count_all(self) -> int:
        """
        전체 상품 등록 데이터 수를 조회합니다.
        
        Returns:
            int: 전체 데이터 수
        """
        try:
            stmt = select(func.count(ProductRegistrationRawData.id))
            result = await self.session.execute(stmt)
            return result.scalar()
            
        except SQLAlchemyError as e:
            logger.error(f"데이터 수 조회 오류: {e}")
            raise
    
    async def search_by_name(self, search_term: str, limit: int = 50) -> List[ProductRegistrationRawData]:
        """
        제품명이나 상품명으로 데이터를 검색합니다.
        
        Args:
            search_term: 검색어
            limit: 조회할 데이터 수 제한
            
        Returns:
            List[ProductRegistrationRawData]: 검색된 데이터 리스트
        """
        try:
            search_pattern = f"%{search_term}%"
            stmt = (
                select(ProductRegistrationRawData)
                .where(
                    (ProductRegistrationRawData.products_nm.ilike(search_pattern)) |
                    (ProductRegistrationRawData.goods_nm.ilike(search_pattern))
                )
                .limit(limit)
                .order_by(ProductRegistrationRawData.created_at.desc())
            )
            
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"데이터 검색 오류: {e}")
            raise

    async def get_product_price_by_products_nm(self, products_nm: str) -> Optional[Decimal]:
        """상품명으로 상품 가격 조회"""
        query = select(ProductRegistrationRawData.goods_price).where(ProductRegistrationRawData.products_nm == products_nm)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()