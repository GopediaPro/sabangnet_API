"""
이카운트 IYES 단가 리포지토리
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.dialects.postgresql import insert
from models.ecount.iyes_cost import EcountIyesCost
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class EcountIyesCostRepository:
    """이카운트 IYES 단가 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_iyes_costs(self) -> List[EcountIyesCost]:
        """모든 IYES 단가 데이터를 조회합니다."""
        try:
            stmt = select(EcountIyesCost)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"IYES 단가 조회 중 오류: {e}")
            return []
    
    async def get_iyes_cost_by_product_nm(self, product_nm: str) -> Optional[EcountIyesCost]:
        """제품명으로 IYES 단가를 조회합니다."""
        try:
            stmt = select(EcountIyesCost).where(EcountIyesCost.product_nm == product_nm)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"IYES 단가 조회 중 오류: {e}")
            return None
    
    async def create_iyes_cost(self, product_nm: str, cost: Optional[int] = None, 
                              cost_10_vat: Optional[int] = None, cost_20_vat: Optional[int] = None) -> EcountIyesCost:
        """IYES 단가를 생성합니다."""
        try:
            iyes_cost = EcountIyesCost(
                product_nm=product_nm,
                cost=cost,
                cost_10_vat=cost_10_vat,
                cost_20_vat=cost_20_vat
            )
            self.session.add(iyes_cost)
            await self.session.flush()
            return iyes_cost
        except Exception as e:
            logger.error(f"IYES 단가 생성 중 오류: {e}")
            raise
    
    async def update_iyes_cost(self, product_nm: str, cost: Optional[int] = None, 
                              cost_10_vat: Optional[int] = None, cost_20_vat: Optional[int] = None) -> Optional[EcountIyesCost]:
        """제품명으로 IYES 단가를 업데이트합니다."""
        try:
            update_values = {}
            if cost is not None:
                update_values['cost'] = cost
            if cost_10_vat is not None:
                update_values['cost_10_vat'] = cost_10_vat
            if cost_20_vat is not None:
                update_values['cost_20_vat'] = cost_20_vat
            
            if not update_values:
                return None
                
            stmt = (
                update(EcountIyesCost)
                .where(EcountIyesCost.product_nm == product_nm)
                .values(**update_values)
                .returning(EcountIyesCost)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"IYES 단가 업데이트 중 오류: {e}")
            raise
    
    async def upsert_iyes_cost(self, product_nm: str, cost: Optional[int] = None, 
                              cost_10_vat: Optional[int] = None, cost_20_vat: Optional[int] = None) -> EcountIyesCost:
        """IYES 단가를 upsert합니다 (product_nm 기준)."""
        try:
            # 먼저 기존 데이터가 있는지 확인
            existing = await self.get_iyes_cost_by_product_nm(product_nm)
            
            if existing:
                # 업데이트
                updated = await self.update_iyes_cost(product_nm, cost, cost_10_vat, cost_20_vat)
                return updated
            else:
                # 생성
                return await self.create_iyes_cost(product_nm, cost, cost_10_vat, cost_20_vat)
        except Exception as e:
            logger.error(f"IYES 단가 upsert 중 오류: {e}")
            raise
    
    async def bulk_upsert_iyes_costs(self, data_list: List[dict]) -> List[EcountIyesCost]:
        """IYES 단가를 일괄 upsert합니다."""
        try:
            upserted_data = []
            
            for data in data_list:
                product_nm = data.get('product_nm')
                cost = data.get('cost')
                cost_10_vat = data.get('cost_10_vat')
                cost_20_vat = data.get('cost_20_vat')
                
                if product_nm:  # product_nm이 있는 경우만 처리
                    upserted = await self.upsert_iyes_cost(product_nm, cost, cost_10_vat, cost_20_vat)
                    upserted_data.append(upserted)
            
            await self.session.commit()
            logger.info(f"IYES 단가 {len(upserted_data)}건 upsert 완료")
            return upserted_data
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"IYES 단가 일괄 upsert 중 오류: {e}")
            raise
    
    async def delete_all_iyes_costs(self) -> int:
        """모든 IYES 단가를 삭제합니다."""
        try:
            stmt = delete(EcountIyesCost)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"IYES 단가 {deleted_count}건 삭제 완료")
            return deleted_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"IYES 단가 삭제 중 오류: {e}")
            raise
