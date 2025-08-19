from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from models.smile.smile_macro import SmileMacro
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class SmileMacroRepository:
    """
    스마일배송 매크로 데이터 리포지토리
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_smile_macro(self, smile_macro_data: dict) -> SmileMacro:
        """
        스마일배송 매크로 데이터 생성
        
        Args:
            smile_macro_data: 스마일배송 매크로 데이터
            
        Returns:
            SmileMacro: 생성된 스마일배송 매크로 데이터
        """
        try:
            smile_macro = SmileMacro(**smile_macro_data)
            self.session.add(smile_macro)
            await self.session.commit()
            await self.session.refresh(smile_macro)
            
            logger.info(f"스마일배송 매크로 데이터 생성 완료: ID {smile_macro.id}")
            return smile_macro
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스마일배송 매크로 데이터 생성 중 오류: {str(e)}")
            raise
    
    async def create_multiple_smile_macro(self, smile_macro_data_list: List[dict]) -> List[SmileMacro]:
        """
        여러 스마일배송 매크로 데이터 생성
        
        Args:
            smile_macro_data_list: 스마일배송 매크로 데이터 리스트
            
        Returns:
            List[SmileMacro]: 생성된 스마일배송 매크로 데이터 리스트
        """
        try:
            smile_macro_list = []
            for data in smile_macro_data_list:
                smile_macro = SmileMacro(**data)
                smile_macro_list.append(smile_macro)
            
            self.session.add_all(smile_macro_list)
            await self.session.commit()
            
            # 생성된 객체들을 refresh
            for smile_macro in smile_macro_list:
                await self.session.refresh(smile_macro)
            
            logger.info(f"스마일배송 매크로 데이터 {len(smile_macro_list)}개 생성 완료")
            return smile_macro_list
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스마일배송 매크로 데이터 일괄 생성 중 오류: {str(e)}")
            raise
    
    async def get_all_smile_macro(self) -> List[SmileMacro]:
        """
        모든 스마일배송 매크로 데이터 조회
        
        Returns:
            List[SmileMacro]: 스마일배송 매크로 데이터 리스트
        """
        try:
            stmt = select(SmileMacro)
            result = await self.session.execute(stmt)
            smile_macro_list = result.scalars().all()
            
            logger.info(f"스마일배송 매크로 데이터 {len(smile_macro_list)}개 조회 완료")
            return smile_macro_list
            
        except Exception as e:
            logger.error(f"스마일배송 매크로 데이터 조회 중 오류: {str(e)}")
            raise
    
    async def get_smile_macro_by_id(self, smile_macro_id: int) -> Optional[SmileMacro]:
        """
        ID로 스마일배송 매크로 데이터 조회
        
        Args:
            smile_macro_id: 스마일배송 매크로 데이터 ID
            
        Returns:
            Optional[SmileMacro]: 스마일배송 매크로 데이터 또는 None
        """
        try:
            stmt = select(SmileMacro).where(SmileMacro.id == smile_macro_id)
            result = await self.session.execute(stmt)
            smile_macro = result.scalar_one_or_none()
            
            if smile_macro:
                logger.info(f"스마일배송 매크로 데이터 조회 완료: ID {smile_macro_id}")
            else:
                logger.warning(f"스마일배송 매크로 데이터를 찾을 수 없음: ID {smile_macro_id}")
            
            return smile_macro
            
        except Exception as e:
            logger.error(f"스마일배송 매크로 데이터 조회 중 오류: {str(e)}")
            raise
    
    async def delete_smile_macro_by_id(self, smile_macro_id: int) -> bool:
        """
        ID로 스마일배송 매크로 데이터 삭제
        
        Args:
            smile_macro_id: 스마일배송 매크로 데이터 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            smile_macro = await self.get_smile_macro_by_id(smile_macro_id)
            if smile_macro:
                await self.session.delete(smile_macro)
                await self.session.commit()
                logger.info(f"스마일배송 매크로 데이터 삭제 완료: ID {smile_macro_id}")
                return True
            else:
                logger.warning(f"삭제할 스마일배송 매크로 데이터를 찾을 수 없음: ID {smile_macro_id}")
                return False
                
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스마일배송 매크로 데이터 삭제 중 오류: {str(e)}")
            raise
