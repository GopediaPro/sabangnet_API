"""
Product Category Repository
상품 카테고리 데이터 저장소 클래스
"""

from decimal import Decimal
from sqlalchemy.engine import Row
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models.product.product_mycategory_data import ProductMycategoryData
from schemas.product.product_mycategory_dto import ProductMycategoryCreateDto
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)


class ProductMyCategoryRepository:
    """상품 카테고리 데이터 저장소 클래스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_class_cd_from_nm(self, level: int, class_nm: str) -> Optional[str]:
        """
        분류명으로 분류코드 조회 (1~4레벨 유동적)
        :param level: 1~4 (분류 단계)
        :param class_nm: 분류명
        :return: 분류코드 or None
        """
        if level not in [1, 2, 3, 4]:
            raise ValueError("level must be 1, 2, 3, or 4")
        cd_field = f'class_cd{level}'
        nm_field = f'class_nm{level}'
        cd_column = getattr(ProductMycategoryData, cd_field)
        nm_column = getattr(ProductMycategoryData, nm_field)
        query = select(cd_column).where(nm_column == class_nm)
        result = await self.session.execute(query)
        row = result.first()
        return row[0] if row else None
        