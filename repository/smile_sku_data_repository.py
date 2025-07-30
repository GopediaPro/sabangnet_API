from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.smile.smile_sku_data import SmileSkuData
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class SmileSkuDataRepository:
    """
    스마일배송 SKU 데이터 리포지토리
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all_sku_data(self) -> List[SmileSkuData]:
        """
        모든 SKU 데이터 조회
        
        Returns:
            List[SmileSkuData]: SKU 데이터 리스트
        """
        try:
            query = select(SmileSkuData)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"SKU 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_sku_data_by_sku_number(self, sku_number: str) -> Optional[SmileSkuData]:
        """
        SKU 번호로 SKU 데이터 조회
        
        Args:
            sku_number: SKU 번호
            
        Returns:
            Optional[SmileSkuData]: SKU 데이터 또는 None
        """
        try:
            query = select(SmileSkuData).where(SmileSkuData.sku_number == sku_number)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"SKU 번호로 SKU 데이터 조회 중 오류: {str(e)}")
            return None
    
    async def get_sku_data_by_model_name(self, model_name: str) -> List[SmileSkuData]:
        """
        모델명으로 SKU 데이터 조회
        
        Args:
            model_name: 모델명
            
        Returns:
            List[SmileSkuData]: 모델명별 SKU 데이터 리스트
        """
        try:
            query = select(SmileSkuData).where(SmileSkuData.model_name == model_name)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"모델명으로 SKU 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def get_sku_data_by_sku_name(self, sku_name: str) -> List[SmileSkuData]:
        """
        SKU명으로 SKU 데이터 조회
        
        Args:
            sku_name: SKU명
            
        Returns:
            List[SmileSkuData]: SKU명별 데이터 리스트
        """
        try:
            query = select(SmileSkuData).where(SmileSkuData.sku_name == sku_name)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"SKU명으로 SKU 데이터 조회 중 오류: {str(e)}")
            return []
    
    async def search_sku_data_by_keyword(self, keyword: str) -> List[SmileSkuData]:
        """
        키워드로 SKU 데이터 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            List[SmileSkuData]: 검색 결과 리스트
        """
        try:
            query = select(SmileSkuData).where(
                (SmileSkuData.sku_number.contains(keyword)) |
                (SmileSkuData.model_name.contains(keyword)) |
                (SmileSkuData.sku_name.contains(keyword))
            )
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"키워드로 SKU 데이터 검색 중 오류: {str(e)}")
            return []
    
    async def create_sku_data(self, sku_data: SmileSkuData) -> SmileSkuData:
        """
        SKU 데이터 생성
        
        Args:
            sku_data: 생성할 SKU 데이터
            
        Returns:
            SmileSkuData: 생성된 SKU 데이터
        """
        try:
            self.session.add(sku_data)
            await self.session.commit()
            await self.session.refresh(sku_data)
            return sku_data
        except Exception as e:
            await self.session.rollback()
            logger.error(f"SKU 데이터 생성 중 오류: {str(e)}")
            raise
    
    async def bulk_create_sku_data(self, sku_data_list: List[SmileSkuData]) -> List[SmileSkuData]:
        """
        SKU 데이터 일괄 생성
        
        Args:
            sku_data_list: 생성할 SKU 데이터 리스트
            
        Returns:
            List[SmileSkuData]: 생성된 SKU 데이터 리스트
        """
        try:
            self.session.add_all(sku_data_list)
            await self.session.commit()
            
            # 생성된 데이터들을 refresh
            for sku_data in sku_data_list:
                await self.session.refresh(sku_data)
            
            return sku_data_list
        except Exception as e:
            await self.session.rollback()
            logger.error(f"SKU 데이터 일괄 생성 중 오류: {str(e)}")
            raise
    
    async def delete_all_sku_data(self) -> bool:
        """
        모든 SKU 데이터 삭제
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            await self.session.execute("DELETE FROM smile_sku_data")
            await self.session.commit()
            logger.info("모든 SKU 데이터가 삭제되었습니다.")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"SKU 데이터 삭제 중 오류: {str(e)}")
            return False
    
    async def update_sku_data(self, sku_data: SmileSkuData) -> SmileSkuData:
        """
        SKU 데이터 수정
        
        Args:
            sku_data: 수정할 SKU 데이터
            
        Returns:
            SmileSkuData: 수정된 SKU 데이터
        """
        try:
            await self.session.commit()
            await self.session.refresh(sku_data)
            return sku_data
        except Exception as e:
            await self.session.rollback()
            logger.error(f"SKU 데이터 수정 중 오류: {str(e)}")
            raise
    
    async def delete_sku_data(self, sku_data: SmileSkuData) -> bool:
        """
        SKU 데이터 삭제
        
        Args:
            sku_data: 삭제할 SKU 데이터
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            await self.session.delete(sku_data)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"SKU 데이터 삭제 중 오류: {str(e)}")
            return False 