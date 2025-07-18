"""
이카운트 판매 리포지토리
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import json

from models.ecount.ecount_models import EcountSale
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.ecount.sale_schemas import EcountSaleDto
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


class EcountSaleRepository:
    """이카운트 판매 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_ecount_sale(self, sale_dto: EcountSaleDto) -> EcountSale:
        """이카운트 판매 데이터를 저장합니다."""
        try:
            ecount_sale = EcountSale(
                com_code=sale_dto.com_code,
                user_id=sale_dto.user_id,
                upload_ser_no=sale_dto.upload_ser_no,
                io_date=sale_dto.io_date,
                cust=sale_dto.cust,
                cust_des=sale_dto.cust_des,
                wh_cd=sale_dto.wh_cd,
                prod_cd=sale_dto.prod_cd,
                prod_des=sale_dto.prod_des,
                qty=sale_dto.qty,
                price=sale_dto.price,
                supply_amt=sale_dto.supply_amt,
                vat_amt=sale_dto.vat_amt,
                remarks=sale_dto.remarks,
                is_success=sale_dto.is_success,
                slip_no=sale_dto.slip_no,
                trace_id=sale_dto.trace_id,
                error_message=sale_dto.error_message,
                is_test=sale_dto.is_test,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.session.add(ecount_sale)
            await self.session.flush()
            return ecount_sale
            
        except Exception as e:
            logger.error(f"이카운트 판매 데이터 저장 중 오류: {e}")
            raise
    
    async def bulk_save_ecount_sales(self, sale_dtos: List[EcountSaleDto]) -> List[EcountSale]:
        """이카운트 판매 데이터를 일괄 저장합니다."""
        try:
            ecount_sales = []
            
            for sale_dto in sale_dtos:
                ecount_sale = await self.save_ecount_sale(sale_dto)
                ecount_sales.append(ecount_sale)
            
            await self.session.commit()
            logger.info(f"이카운트 판매 데이터 {len(ecount_sales)}건 저장 완료")
            return ecount_sales
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"이카운트 판매 데이터 일괄 저장 중 오류: {e}")
            raise
    
    async def get_ecount_sale_by_id(self, sale_id: str) -> Optional[EcountSale]:
        """ID로 이카운트 판매 데이터를 조회합니다."""
        try:
            stmt = select(EcountSale).where(EcountSale.id == sale_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"이카운트 판매 데이터 조회 중 오류: {e}")
            return None
    
    async def get_ecount_sales_by_trace_id(self, trace_id: str) -> List[EcountSale]:
        """Trace ID로 이카운트 판매 데이터를 조회합니다."""
        try:
            stmt = select(EcountSale).where(EcountSale.trace_id == trace_id)
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"이카운트 판매 데이터 조회 중 오류: {e}")
            return []


class DownFormOrderRepository:
    """다운폼 주문 리포지토리"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_orders_by_condition(
        self, 
        order_from: Optional[str] = None,
        order_to: Optional[str] = None,
        template_code: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        exclude_erp_sent: bool = True
    ) -> Tuple[List[BaseDownFormOrder], int]:
        """조건에 따라 주문을 조회합니다."""
        try:
            # 기본 쿼리
            base_query = select(BaseDownFormOrder)
            count_query = select(func.count()).select_from(BaseDownFormOrder)
            
            # 조건 추가
            conditions = []
            
            # 날짜 범위 조건
            if order_from:
                conditions.append(BaseDownFormOrder.order_date >= datetime.strptime(order_from, "%Y%m%d"))
            
            if order_to:
                end_date = datetime.strptime(order_to, "%Y%m%d")
                # 하루 종료 시점까지 포함
                end_date = end_date.replace(hour=23, minute=59, second=59)
                conditions.append(BaseDownFormOrder.order_date <= end_date)
            
            # 템플릿 코드 조건
            if template_code:
                conditions.append(BaseDownFormOrder.form_name == template_code)
            
            # ERP 전송 완료된 것 제외
            if exclude_erp_sent:
                conditions.append(BaseDownFormOrder.work_status != "ERP_전송완료")
            
            # 조건 적용
            if conditions:
                base_query = base_query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))
            
            # 페이지네이션
            offset = (page - 1) * page_size
            base_query = base_query.offset(offset).limit(page_size)
            
            # 정렬 (최신순)
            base_query = base_query.order_by(BaseDownFormOrder.order_date.desc())
            
            # 실행
            result = await self.session.execute(base_query)
            orders = result.scalars().all()
            
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()
            
            logger.info(f"주문 조회 완료: {len(orders)}건 (전체 {total_count}건)")
            return orders, total_count
            
        except Exception as e:
            logger.error(f"주문 조회 중 오류: {e}")
            return [], 0
    
    async def update_work_status_to_erp_sent(self, order_ids: List[str]) -> int:
        """주문들의 work_status를 'ERP_전송완료'로 업데이트합니다."""
        try:
            stmt = (
                update(BaseDownFormOrder)
                .where(BaseDownFormOrder.idx.in_(order_ids))
                .values(work_status="ERP_전송완료")
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            updated_count = result.rowcount
            logger.info(f"주문 상태 업데이트 완료: {updated_count}건")
            return updated_count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"주문 상태 업데이트 중 오류: {e}")
            raise
    
    async def get_orders_by_ids(self, order_ids: List[str]) -> List[BaseDownFormOrder]:
        """ID 목록으로 주문을 조회합니다."""
        try:
            stmt = select(BaseDownFormOrder).where(BaseDownFormOrder.idx.in_(order_ids))
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"주문 ID별 조회 중 오류: {e}")
            return []
    
    async def get_already_sent_orders(self, order_ids: List[str]) -> List[str]:
        """이미 ERP로 전송된 주문 ID 목록을 반환합니다."""
        try:
            stmt = (
                select(BaseDownFormOrder.idx)
                .where(
                    and_(
                        BaseDownFormOrder.idx.in_(order_ids),
                        BaseDownFormOrder.work_status == "ERP_전송완료"
                    )
                )
            )
            
            result = await self.session.execute(stmt)
            sent_order_ids = [row[0] for row in result.fetchall()]
            
            if sent_order_ids:
                logger.info(f"이미 전송된 주문: {len(sent_order_ids)}건")
            
            return sent_order_ids
            
        except Exception as e:
            logger.error(f"이미 전송된 주문 조회 중 오류: {e}")
            return []
