"""
EcountPurchase Repository
이카운트 구매 데이터 저장소
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.dialects.postgresql import insert

from models.ecount.ecount_models import EcountPurchase
from schemas.ecount.erp_data_processing_dto import EcountPurchaseData
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class EcountPurchaseRepository:
    """EcountPurchase 데이터 저장소"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def upsert_purchase_data(
        self, 
        purchase_data_list: List[EcountPurchaseData]
    ) -> Tuple[int, int]:
        """
        구매 데이터 upsert (prod_des 기준으로 중복 체크)
        
        Args:
            purchase_data_list: 구매 데이터 리스트
            
        Returns:
            (생성된 레코드 수, 업데이트된 레코드 수)
        """
        try:
            created_count = 0
            updated_count = 0
            
            for purchase_data in purchase_data_list:
                # prod_des 기준으로 기존 데이터 조회
                existing_purchase = await self._find_by_prod_des(purchase_data.prod_des)
                
                if existing_purchase:
                    # 업데이트
                    await self._update_purchase(existing_purchase.id, purchase_data)
                    updated_count += 1
                    logger.debug(f"Updated EcountPurchase: {purchase_data.prod_des}")
                else:
                    # 생성
                    await self._create_purchase(purchase_data)
                    created_count += 1
                    logger.debug(f"Created EcountPurchase: {purchase_data.prod_des}")
            
            await self.session.commit()
            logger.info(f"EcountPurchase upsert completed: {created_count} created, {updated_count} updated")
            
            return created_count, updated_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"EcountPurchase upsert failed: {str(e)}")
            raise e
    
    async def _find_by_prod_des(self, prod_des: Optional[str]) -> Optional[EcountPurchase]:
        """
        prod_des 기준으로 기존 데이터 조회
        """
        if not prod_des:
            return None
        
        try:
            query = select(EcountPurchase).where(
                and_(
                    EcountPurchase.prod_des == prod_des,
                    EcountPurchase.is_test == True  # 테스트 데이터만
                )
            ).limit(1)
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error finding EcountPurchase by prod_des {prod_des}: {str(e)}")
            return None
    
    async def _create_purchase(self, purchase_data: EcountPurchaseData) -> EcountPurchase:
        """
        새로운 구매 데이터 생성
        """
        try:
            purchase = EcountPurchase(
                com_code=purchase_data.com_code,
                user_id=purchase_data.user_id,
                emp_cd=purchase_data.emp_cd,
                io_date=purchase_data.io_date,
                upload_ser_no=purchase_data.upload_ser_no,
                cust=purchase_data.cust,
                cust_des=purchase_data.cust_des,
                wh_cd=purchase_data.wh_cd,
                io_type=purchase_data.io_type,
                exchange_type=purchase_data.exchange_type,
                exchange_rate=purchase_data.exchange_rate,
                u_memo1=purchase_data.u_memo1,
                u_memo2=purchase_data.u_memo2,
                u_memo3=purchase_data.u_memo3,
                u_txt1=purchase_data.u_txt1,
                prod_cd=purchase_data.prod_cd,
                prod_des=purchase_data.prod_des,
                qty=purchase_data.qty,
                price=purchase_data.price,
                exchange_cost=purchase_data.exchange_cost,
                supply_amt=purchase_data.supply_amt,
                vat_amt=purchase_data.vat_amt,
                remarks=purchase_data.remarks,
                is_test=purchase_data.is_test,
                work_status=purchase_data.work_status,
                batch_id=purchase_data.batch_id,
                template_code=purchase_data.template_code
            )
            
            self.session.add(purchase)
            return purchase
            
        except Exception as e:
            logger.error(f"Error creating EcountPurchase: {str(e)}")
            raise e
    
    async def _update_purchase(self, purchase_id: str, purchase_data: EcountPurchaseData) -> None:
        """
        기존 구매 데이터 업데이트
        """
        try:
            update_data = {
                'com_code': purchase_data.com_code,
                'user_id': purchase_data.user_id,
                'emp_cd': purchase_data.emp_cd,
                'io_date': purchase_data.io_date,
                'upload_ser_no': purchase_data.upload_ser_no,
                'cust': purchase_data.cust,
                'cust_des': purchase_data.cust_des,
                'wh_cd': purchase_data.wh_cd,
                'io_type': purchase_data.io_type,
                'exchange_type': purchase_data.exchange_type,
                'exchange_rate': purchase_data.exchange_rate,
                'u_memo1': purchase_data.u_memo1,
                'u_memo2': purchase_data.u_memo2,
                'u_memo3': purchase_data.u_memo3,
                'u_txt1': purchase_data.u_txt1,
                'prod_cd': purchase_data.prod_cd,
                'prod_des': purchase_data.prod_des,
                'qty': purchase_data.qty,
                'price': purchase_data.price,
                'exchange_cost': purchase_data.exchange_cost,
                'supply_amt': purchase_data.supply_amt,
                'vat_amt': purchase_data.vat_amt,
                'remarks': purchase_data.remarks,
                'is_test': purchase_data.is_test,
                'work_status': purchase_data.work_status,
                'batch_id': purchase_data.batch_id,
                'template_code': purchase_data.template_code
            }
            
            query = update(EcountPurchase).where(
                EcountPurchase.id == purchase_id
            ).values(**update_data)
            
            await self.session.execute(query)
            
        except Exception as e:
            logger.error(f"Error updating EcountPurchase {purchase_id}: {str(e)}")
            raise e
    
    async def get_by_batch_id(self, batch_id: str) -> List[EcountPurchase]:
        """
        배치 ID로 구매 데이터 조회
        """
        try:
            query = select(EcountPurchase).where(
                EcountPurchase.batch_id == batch_id
            ).order_by(EcountPurchase.upload_ser_no)
            
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting EcountPurchase by batch_id {batch_id}: {str(e)}")
            raise e
    
    async def get_by_template_code(self, template_code: str) -> List[EcountPurchase]:
        """
        템플릿 코드로 구매 데이터 조회
        """
        try:
            query = select(EcountPurchase).where(
                EcountPurchase.template_code == template_code
            ).order_by(EcountPurchase.upload_ser_no)
            
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting EcountPurchase by template_code {template_code}: {str(e)}")
            raise e
