from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from models.smile.smile_settlement_data import SmileSettlementData
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class SmileSettlementDataRepository:
    """
    스마일배송 정산 데이터 리포지토리
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_settlement_data(self) -> List[SmileSettlementData]:
        """
        모든 정산 데이터 조회
        
        Returns:
            List[SmileSettlementData]: 정산 데이터 리스트
        """
        try:
            query = select(SmileSettlementData)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"정산 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_settlement_data_by_site(self, site: str) -> List[SmileSettlementData]:
        """
        사이트별 정산 데이터 조회
        
        Args:
            site: 사이트명 (G마켓, 옥션 등)
            
        Returns:
            List[SmileSettlementData]: 사이트별 정산 데이터 리스트
        """
        try:
            query = select(SmileSettlementData).where(SmileSettlementData.site == site)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"사이트별 정산 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_settlement_data_by_order_number(self, order_number: str) -> List[SmileSettlementData]:
        """
        주문번호로 정산 데이터 조회
        
        Args:
            order_number: 주문번호
            
        Returns:
            List[SmileSettlementData]: 주문번호별 정산 데이터 리스트
        """
        try:
            # 입력값을 문자열로 확실히 변환
            order_number_str = str(order_number) if order_number is not None else ""
            
            query = select(SmileSettlementData).where(SmileSettlementData.order_number == order_number_str)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"주문번호로 정산 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_settlement_data_by_date_range(self, start_date: datetime, end_date: datetime) -> List[SmileSettlementData]:
        """
        날짜 범위로 정산 데이터 조회
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            List[SmileSettlementData]: 날짜 범위 정산 데이터 리스트
        """
        try:
            query = select(SmileSettlementData).where(
                SmileSettlementData.payment_date >= start_date,
                SmileSettlementData.payment_date <= end_date
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"날짜 범위 정산 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_settlement_data_by_settlement_type(self, settlement_type: str) -> List[SmileSettlementData]:
        """
        정산 구분으로 정산 데이터 조회
        
        Args:
            settlement_type: 정산 구분
            
        Returns:
            List[SmileSettlementData]: 정산 구분별 데이터 리스트
        """
        try:
            query = select(SmileSettlementData).where(SmileSettlementData.settlement_type == settlement_type)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"정산 구분별 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def create_settlement_data(self, settlement_data: SmileSettlementData) -> SmileSettlementData:
        """
        정산 데이터 생성
        
        Args:
            settlement_data: 생성할 정산 데이터
            
        Returns:
            SmileSettlementData: 생성된 정산 데이터
        """
        try:
            self.session.add(settlement_data)
            await self.session.commit()
            await self.session.refresh(settlement_data)
            return settlement_data
        except Exception as e:
            await self.session.rollback()
            logger.error(f"정산 데이터 생성 중 오류: {str(e)}")
            raise
    
    async def bulk_create_settlement_data(self, settlement_data_list: List[SmileSettlementData], site: str) -> List[SmileSettlementData]:
        """
        정산 데이터 일괄 생성
        
        Args:
            settlement_data_list: 생성할 정산 데이터 리스트
            site: 사이트명 (G마켓, 옥션 등)
            
        Returns:
            List[SmileSettlementData]: 생성된 정산 데이터 리스트
        """
        logger.info(f"정산 데이터 일괄 생성 - site: '{site}' (type: {type(site)})")
        logger.info(f"정산 데이터 리스트 개수: {len(settlement_data_list)}")
        
        try:
            # site 정보를 각 데이터에 설정
            for settlement_data in settlement_data_list:
                settlement_data.site = site
            logger.info(f"정산 데이터 일괄 생성 - settlement_data: '{settlement_data}' (type: {type(settlement_data)})")
            self.session.add_all(settlement_data_list)
            await self.session.commit()
            
            # 생성된 데이터들을 refresh
            for settlement_data in settlement_data_list:
                await self.session.refresh(settlement_data)
            
            return settlement_data_list
        except Exception as e:
            await self.session.rollback()
            logger.error(f"정산 데이터 일괄 생성 중 오류: {str(e)}")
            raise
    
    async def delete_all_settlement_data(self) -> bool:
        """
        모든 정산 데이터 삭제
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            await self.session.execute("DELETE FROM smile_settlement_data")
            await self.session.commit()
            logger.info("모든 정산 데이터가 삭제되었습니다.")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"정산 데이터 삭제 중 오류: {str(e)}")
            return False 