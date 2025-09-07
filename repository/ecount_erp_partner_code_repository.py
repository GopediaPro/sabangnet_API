"""
이카운트 ERP 파트너 코드 리포지토리
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.dialects.postgresql import insert
from models.ecount.erp_partner_code import EcountErpPartnerCode
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class EcountErpPartnerCodeRepository:
    """이카운트 ERP 파트너 코드 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_erp_partner_codes(self) -> List[EcountErpPartnerCode]:
        """모든 ERP 파트너 코드 데이터를 조회합니다."""
        try:
            stmt = select(EcountErpPartnerCode)
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"ERP 파트너 코드 조회 중 오류: {e}")
            return []
    
    async def get_erp_partner_code_by_product_nm(self, product_nm: str) -> Optional[EcountErpPartnerCode]:
        """제품명으로 ERP 파트너 코드를 조회합니다."""
        try:
            stmt = select(EcountErpPartnerCode).where(EcountErpPartnerCode.product_nm == product_nm)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"ERP 파트너 코드 조회 중 오류: {e}")
            return None
    
    async def create_erp_partner_code(self, data: dict) -> EcountErpPartnerCode:
        """ERP 파트너 코드를 생성합니다."""
        try:
            erp_partner_code = EcountErpPartnerCode(
                fld_dsp=data.get('fld_dsp'),
                partner_code=data.get('partner_code'),
                product_nm=data.get('product_nm'),
                wh_cd=data.get('wh_cd')
            )
            self.session.add(erp_partner_code)
            await self.session.flush()
            return erp_partner_code
        except Exception as e:
            logger.error(f"ERP 파트너 코드 생성 중 오류: {e}")
            raise
    
    async def update_erp_partner_code(self, product_nm: str, data: dict) -> Optional[EcountErpPartnerCode]:
        """제품명으로 ERP 파트너 코드를 업데이트합니다."""
        try:
            stmt = (
                update(EcountErpPartnerCode)
                .where(EcountErpPartnerCode.product_nm == product_nm)
                .values(
                    fld_dsp=data.get('fld_dsp'),
                    partner_code=data.get('partner_code'),
                    wh_cd=data.get('wh_cd')
                )
                .returning(EcountErpPartnerCode)
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"ERP 파트너 코드 업데이트 중 오류: {e}")
            raise
    
    async def upsert_erp_partner_code(self, data: dict) -> EcountErpPartnerCode:
        """ERP 파트너 코드를 upsert합니다 (product_nm 기준)."""
        try:
            product_nm = data.get('product_nm')
            if not product_nm:
                raise ValueError("product_nm is required for upsert")
            
            # 먼저 기존 데이터가 있는지 확인
            existing = await self.get_erp_partner_code_by_product_nm(product_nm)
            
            if existing:
                # 업데이트
                updated = await self.update_erp_partner_code(product_nm, data)
                return updated
            else:
                # 생성
                return await self.create_erp_partner_code(data)
        except Exception as e:
            logger.error(f"ERP 파트너 코드 upsert 중 오류: {e}")
            raise
    
    async def bulk_upsert_erp_partner_codes(self, data_list: List[dict]) -> List[EcountErpPartnerCode]:
        """ERP 파트너 코드를 일괄 upsert합니다."""
        try:
            upserted_data = []
            
            for data in data_list:
                product_nm = data.get('product_nm')
                fld_dsp = data.get('fld_dsp')
                
                # product_nm 또는 fld_dsp가 있는 경우만 처리
                if product_nm or fld_dsp:
                    upserted = await self.upsert_erp_partner_code(data)
                    upserted_data.append(upserted)
            
            await self.session.commit()
            logger.info(f"ERP 파트너 코드 {len(upserted_data)}건 upsert 완료")
            return upserted_data
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ERP 파트너 코드 일괄 upsert 중 오류: {e}")
            raise
    
    async def delete_all_erp_partner_codes(self) -> int:
        """모든 ERP 파트너 코드를 삭제합니다."""
        try:
            stmt = delete(EcountErpPartnerCode)
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"ERP 파트너 코드 {deleted_count}건 삭제 완료")
            return deleted_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ERP 파트너 코드 삭제 중 오류: {e}")
            raise
