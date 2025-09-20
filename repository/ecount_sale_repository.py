"""
EcountSale Repository
이카운트 판매 데이터 저장소
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from models.ecount.ecount_models import EcountSale
from schemas.ecount.erp_data_processing_dto import EcountSaleData
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class EcountSaleRepository:
    """EcountSale 데이터 저장소"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def upsert_sale_data(
        self, 
        sale_data_list: List[EcountSaleData]
    ) -> Tuple[int, int]:
        """
        판매 데이터 upsert (size_des 기준으로 중복 체크)
        
        Args:
            sale_data_list: 판매 데이터 리스트
            
        Returns:
            (생성된 레코드 수, 업데이트된 레코드 수)
        """
        try:
            created_count = 0
            updated_count = 0
            
            for sale_data in sale_data_list:
                # size_des 기준으로 기존 데이터 조회
                existing_sale = await self._find_by_size_des(sale_data.size_des)
                
                if existing_sale:
                    # 업데이트
                    await self._update_sale(existing_sale.id, sale_data)
                    updated_count += 1
                    logger.debug(f"Updated EcountSale: {sale_data.size_des}")
                else:
                    # 생성
                    await self._create_sale(sale_data)
                    created_count += 1
                    logger.debug(f"Created EcountSale: {sale_data.size_des}")
            
            await self.session.commit()
            logger.info(f"EcountSale upsert completed: {created_count} created, {updated_count} updated")
            
            return created_count, updated_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"EcountSale upsert failed: {str(e)}")
            raise e
    
    async def _find_by_size_des(self, size_des: Optional[str]) -> Optional[EcountSale]:
        """
        size_des 기준으로 기존 데이터 조회
        """
        if not size_des:
            return None
        
        try:
            query = select(EcountSale).where(
                and_(
                    EcountSale.size_des == size_des,
                    EcountSale.is_test == True  # 테스트 데이터만
                )
            ).limit(1)
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error finding EcountSale by size_des {size_des}: {str(e)}")
            return None
    
    async def _create_sale(self, sale_data: EcountSaleData) -> EcountSale:
        """
        새로운 판매 데이터 생성
        """
        try:
            sale = EcountSale(
                com_code=sale_data.com_code,
                user_id=sale_data.user_id,
                emp_cd=sale_data.emp_cd,
                io_date=sale_data.io_date,
                upload_ser_no=sale_data.upload_ser_no,
                cust=sale_data.cust,
                cust_des=sale_data.cust_des,
                wh_cd=sale_data.wh_cd,
                io_type=sale_data.io_type,
                exchange_type=sale_data.exchange_type,
                exchange_rate=sale_data.exchange_rate,
                u_memo1=sale_data.u_memo1,
                u_memo2=sale_data.u_memo2,
                u_memo3=sale_data.u_memo3,
                u_txt1=sale_data.u_txt1,
                u_memo4=sale_data.u_memo4,
                u_memo5=sale_data.u_memo5,
                prod_cd=sale_data.prod_cd,
                prod_des=sale_data.prod_des,
                qty=sale_data.qty,
                price=sale_data.price,
                # exchange_cost=sale_data.exchange_cost,
                supply_amt=sale_data.supply_amt,
                vat_amt=sale_data.vat_amt,
                remarks=sale_data.remarks,
                p_remarks2=sale_data.p_remarks2,
                p_remarks1=sale_data.p_remarks1,
                p_remarks3=sale_data.p_remarks3,
                size_des=sale_data.size_des,
                p_amt1=sale_data.p_amt1,
                p_amt2=sale_data.p_amt2,
                item_cd=sale_data.item_cd,
                is_test=sale_data.is_test,
                work_status=sale_data.work_status,
                batch_id=sale_data.batch_id,
                template_code=sale_data.template_code,
                created_at=sale_data.created_at,
                updated_at=sale_data.updated_at
            )
            
            self.session.add(sale)
            return sale
            
        except Exception as e:
            logger.error(f"Error creating EcountSale: {str(e)}")
            raise e
    
    async def _update_sale(self, sale_id: str, sale_data: EcountSaleData) -> None:
        """
        기존 판매 데이터 업데이트
        """
        try:
            update_data = {
                'com_code': sale_data.com_code,
                'user_id': sale_data.user_id,
                'emp_cd': sale_data.emp_cd,
                'io_date': sale_data.io_date,
                'upload_ser_no': sale_data.upload_ser_no,
                'cust': sale_data.cust,
                'cust_des': sale_data.cust_des,
                'wh_cd': sale_data.wh_cd,
                'io_type': sale_data.io_type,
                'exchange_type': sale_data.exchange_type,
                'exchange_rate': sale_data.exchange_rate,
                'u_memo1': sale_data.u_memo1,
                'u_memo2': sale_data.u_memo2,
                'u_memo3': sale_data.u_memo3,
                'u_txt1': sale_data.u_txt1,
                'u_memo4': sale_data.u_memo4,
                'u_memo5': sale_data.u_memo5,
                'prod_cd': sale_data.prod_cd,
                'prod_des': sale_data.prod_des,
                'qty': sale_data.qty,
                'price': sale_data.price,
                # 'exchange_cost': sale_data.exchange_cost,
                'supply_amt': sale_data.supply_amt,
                'vat_amt': sale_data.vat_amt,
                'remarks': sale_data.remarks,
                'p_remarks2': sale_data.p_remarks2,
                'p_remarks1': sale_data.p_remarks1,
                'p_remarks3': sale_data.p_remarks3,
                'size_des': sale_data.size_des,
                'p_amt1': sale_data.p_amt1,
                'p_amt2': sale_data.p_amt2,
                'item_cd': sale_data.item_cd,
                'is_test': sale_data.is_test,
                'work_status': sale_data.work_status,
                'batch_id': sale_data.batch_id,
                'template_code': sale_data.template_code,
                'updated_at': sale_data.updated_at
            }
            
            query = update(EcountSale).where(
                EcountSale.id == sale_id
            ).values(**update_data)
            
            await self.session.execute(query)
            
        except Exception as e:
            logger.error(f"Error updating EcountSale {sale_id}: {str(e)}")
            raise e
    
    async def get_by_batch_id(self, batch_id: str) -> List[EcountSale]:
        """
        배치 ID로 판매 데이터 조회
        """
        try:
            query = select(EcountSale).where(
                EcountSale.batch_id == batch_id
            ).order_by(EcountSale.upload_ser_no)
            
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting EcountSale by batch_id {batch_id}: {str(e)}")
            raise e
    
    async def get_by_template_code(self, template_code: str) -> List[EcountSale]:
        """
        템플릿 코드로 판매 데이터 조회
        """
        try:
            query = select(EcountSale).where(
                EcountSale.template_code == template_code
            ).order_by(EcountSale.upload_ser_no)
            
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting EcountSale by template_code {template_code}: {str(e)}")
            raise e