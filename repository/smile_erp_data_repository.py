from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from models.smile.smile_erp_data import SmileErpData
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class SmileErpDataRepository:
    """
    스마일배송 ERP 데이터 리포지토리
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_erp_data(self) -> List[SmileErpData]:
        """
        모든 ERP 데이터 조회
        
        Returns:
            List[SmileErpData]: ERP 데이터 리스트
        """
        try:
            query = select(SmileErpData)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"ERP 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_erp_data_by_fld_dsp(self, fld_dsp: str) -> List[SmileErpData]:
        """
        사이트별 ERP 데이터 조회
        
        Args:
            fld_dsp: 사이트명 (G마켓, 옥션 등)
            
        Returns:
            List[SmileErpData]: 사이트별 ERP 데이터 리스트
        """
        try:
            query = select(SmileErpData).where(SmileErpData.fld_dsp == fld_dsp)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"사이트별 ERP 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_erp_data_by_order_number(self, order_number: str) -> Optional[SmileErpData]:
        """
        주문번호로 ERP 데이터 조회
        
        Args:
            order_number: 주문번호
            
        Returns:
            Optional[SmileErpData]: ERP 데이터 또는 None
        """
        try:
            # 입력값을 문자열로 확실히 변환
            order_number_str = str(order_number) if order_number is not None else ""
            
            logger.debug(f"ERP 데이터베이스 조회: 주문번호='{order_number_str}'")
            
            query = select(SmileErpData).where(SmileErpData.order_number == order_number_str)
            result = await self.session.execute(query)
            erp_data = result.scalar_one_or_none()
            
            if erp_data:
                logger.debug(f"ERP 데이터 찾음: 주문번호='{order_number_str}' -> ERP코드='{erp_data.erp_code}'")
            else:
                logger.debug(f"ERP 데이터 없음: 주문번호='{order_number_str}'")
            
            return erp_data
        except Exception as e:
            logger.error(f"주문번호로 ERP 데이터 조회 중 오류: {str(e)}")
            return None
    
    async def get_erp_data_by_date_range(self, start_date: datetime, end_date: datetime) -> List[SmileErpData]:
        """
        날짜 범위로 ERP 데이터 조회
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            List[SmileErpData]: 날짜 범위 ERP 데이터 리스트
        """
        try:
            query = select(SmileErpData).where(
                SmileErpData.date >= start_date,
                SmileErpData.date <= end_date
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"날짜 범위 ERP 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def create_erp_data(self, erp_data: SmileErpData) -> SmileErpData:
        """
        ERP 데이터 생성
        
        Args:
            erp_data: 생성할 ERP 데이터
            
        Returns:
            SmileErpData: 생성된 ERP 데이터
        """
        try:
            self.session.add(erp_data)
            await self.session.commit()
            await self.session.refresh(erp_data)
            return erp_data
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ERP 데이터 생성 중 오류: {str(e)}")
            raise
    
    async def bulk_create_erp_data(self, erp_data_list: List[SmileErpData]) -> List[SmileErpData]:
        """
        ERP 데이터 일괄 생성
        
        Args:
            erp_data_list: 생성할 ERP 데이터 리스트
            
        Returns:
            List[SmileErpData]: 생성된 ERP 데이터 리스트
        """
        try:
            
            self.session.add_all(erp_data_list)
            await self.session.commit()
            
            # 생성된 데이터들을 refresh
            for erp_data in erp_data_list:
                await self.session.refresh(erp_data)
            
            return erp_data_list
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ERP 데이터 일괄 생성 중 오류: {str(e)}")
            raise
    
    async def delete_all_erp_data(self) -> bool:
        """
        모든 ERP 데이터 삭제
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            await self.session.execute("DELETE FROM smile_erp_data")
            await self.session.commit()
            logger.info("모든 ERP 데이터가 삭제되었습니다.")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"ERP 데이터 삭제 중 오류: {str(e)}")
            return False 