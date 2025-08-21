from typing import Any, Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from sqlalchemy import select, delete, func, update, text
from models.down_form_orders.down_form_order import BaseDownFormOrder
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto, DownFormOrdersInvoiceNoUpdateDto


logger = get_logger(__name__)


class DownFormOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_down_form_orders(self, skip: int = None, limit: int = None) -> list[BaseDownFormOrder]:
        query = select(BaseDownFormOrder).order_by(BaseDownFormOrder.id.desc())
        if skip is not None:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return rows

    async def get_down_form_order_by_id(self, down_form_order_id: int) -> BaseDownFormOrder:
        try:
            query = select(BaseDownFormOrder).where(
                BaseDownFormOrder.id == down_form_order_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_order_by_idx(self, idx: str) -> BaseDownFormOrder:
        try:
            query = select(BaseDownFormOrder).where(
                BaseDownFormOrder.idx == idx)
            result = await self.session.execute(query)
            return result.scalars().first()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_orders_by_template_code(
            self,
            skip: int = None,
            limit: int = None,
            template_code: str = None
    ) -> list[BaseDownFormOrder]:
        try:
            query = select(BaseDownFormOrder).order_by(BaseDownFormOrder.id)
            if template_code == 'all':
                pass  # no filter, fetch all
            elif template_code is None or template_code == '':
                query = query.where((BaseDownFormOrder.form_name == None) | (
                    BaseDownFormOrder.form_name == ''))
            else:
                query = query.where(
                    BaseDownFormOrder.form_name == template_code)
            if skip:
                query = query.offset(skip)
            if limit:
                query = query.limit(limit)

            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_orders_by_pagination(
            self,
            page: int = 1,
            page_size: int = 20,
            template_code: str = "all"
    ) -> list[BaseDownFormOrder]:
        skip = (page - 1) * page_size
        limit = page_size
        return await self.get_down_form_orders_by_template_code(skip, limit, template_code)
    
    async def get_down_form_orders_by_pagination_with_date_range(
            self,
            date_from: date,
            date_to: date,
            page: int = 1,
            page_size: int = 20,
            template_code: str = "all"
    ) -> list[BaseDownFormOrder]:
        skip = (page - 1) * page_size
        limit = page_size
        
        try:
            query = select(BaseDownFormOrder).where(
                BaseDownFormOrder.created_at >= date_from,
                BaseDownFormOrder.created_at <= date_to
            )
            
            if template_code == 'all':
                pass
            elif template_code is None or template_code == '':
                query = query.where((BaseDownFormOrder.form_name == None) | (
                    BaseDownFormOrder.form_name == ''))
            else:
                query = query.where(BaseDownFormOrder.form_name == template_code)
            
            if skip:
                query = query.offset(skip)
            if limit:
                query = query.limit(limit)
                
            query = query.order_by(BaseDownFormOrder.id.desc())
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_down_form_orders_by_work_status(self, work_status: str) -> list[BaseDownFormOrder]:
        try:
            query = select(BaseDownFormOrder).where(
                BaseDownFormOrder.work_status == work_status)
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def create_down_form_order(self, obj_in: DownFormOrderDto) -> BaseDownFormOrder:
        obj_in = BaseDownFormOrder(**obj_in.model_dump())
        try:
            self.session.add(obj_in)
            await self.session.commit()
            await self.session.refresh(obj_in)
            return obj_in
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def bulk_insert(self, objects: list[BaseDownFormOrder]) -> int:
        try:
            self.session.add_all(objects)
            await self.session.commit()
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during bulk_insert: {e}")
            raise e
        finally:
            await self.session.close()

    async def bulk_update(self, objects: list[BaseDownFormOrder]) -> int:
        try:
            for obj in objects:
                values = obj.__dict__.copy()
                values.pop('_sa_instance_state', None)
                idx = values.pop('idx', None)
                values.pop('created_at', None)
                values.pop('process_dt', None)
                if idx is None:
                    continue  # idx 없으면 skip
                values['updated_at'] = func.now()
                stmt = update(BaseDownFormOrder).where(
                    BaseDownFormOrder.idx == idx).values(**values)
                await self.session.execute(stmt)
            await self.session.commit()
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def bulk_delete(self, ids: list[int]) -> dict[int, str]:
        result = {}
        try:
            for id in ids:
                db_obj = await self.session.get(BaseDownFormOrder, id)
                if db_obj:
                    result[id] = "success"
                    await self.session.delete(db_obj)
                else:
                    result[id] = "not_found"
            await self.session.commit()
            return result
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def delete_all(self):
        try:
            await self.session.execute(delete(BaseDownFormOrder))
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()

    async def delete_duplicate(self):
        try:
            # 중복 제거 쿼리
            stmt = text("""
            DELETE FROM down_form_orders
            WHERE id IN (
                SELECT id FROM (
                    SELECT id,
                        ROW_NUMBER() OVER (
                            PARTITION BY idx
                            ORDER BY updated_at DESC, id DESC
                        ) as row_num
                    FROM down_form_orders
                ) ranked
                WHERE row_num > 1
            )
        """)

            result = await self.session.execute(stmt)
            deleted_count = result.rowcount
            await self.session.commit()

            logger.info(f"중복 제거 완료: {deleted_count}개 행 삭제됨")
            return deleted_count

        except Exception as e:
            await self.session.rollback()
            logger.error(f"중복 제거 실패: {e}")
            raise e

    async def count_all(self, template_code: str = None) -> int:
        try:
            query = select(func.count()).select_from(BaseDownFormOrder)
            if template_code == 'all':
                pass  # no filter, fetch all
            elif template_code is None or template_code == '':
                query = query.where((BaseDownFormOrder.form_name == None) | (
                    BaseDownFormOrder.form_name == ''))
            else:
                query = query.where(
                    BaseDownFormOrder.form_name == template_code)
            result = await self.session.execute(query)
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_orders_without_invoice_no(self, limit: int = 100) -> list[BaseDownFormOrder]:
        """
        invoice_no가 없는 주문 데이터를 조회합니다.
        
        Args:
            limit: 조회할 최대 건수 (기본값: 100)
            
        Returns:
            invoice_no가 없는 주문 데이터 리스트
        """
        try:
            query = select(BaseDownFormOrder).where(
                (BaseDownFormOrder.invoice_no == None) | 
                (BaseDownFormOrder.invoice_no == '') |
                (BaseDownFormOrder.invoice_no == 'null')
            ).order_by(BaseDownFormOrder.id.desc()).limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"invoice_no가 없는 주문 조회 실패: {str(e)}")
            raise e
        finally:
            await self.session.close()

    async def save_to_down_form_orders(self, processed_data: list[dict[str, Any]], template_code: str, batch_id: Optional[int] = None) -> int:
        logger.info(
            f"[START] save_to_down_form_orders | processed_data_count={len(processed_data)} | template_code={template_code} | batch_id={batch_id}")
        if not processed_data:
            logger.warning("No processed data to save.")
            return 0
        try:
            # batch_id가 있는 경우 각 데이터에 추가
            if batch_id:
                for data in processed_data:
                    data['batch_id'] = batch_id
            
            objects = [BaseDownFormOrder(**row) for row in processed_data]
            self.session.add_all(objects)
            await self.session.commit()
            logger.info(
                f"[END] save_to_down_form_orders | saved_count={len(objects)}")
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during save_to_down_form_orders: {e}")
            raise

    async def bulk_update_invoice_no_by_idx(self, idx_invoice_no_dict_list: list[dict[str, str]]) -> list[DownFormOrdersInvoiceNoUpdateDto]:
        try:

            invoice_no_updated_down_form_orders: list[DownFormOrdersInvoiceNoUpdateDto] = []

            for item in idx_invoice_no_dict_list:
                idx_list: list[str] = []
                invoice_no: str = item['invoice_no']

                # idx 가 중첩되어있는 경우 (2083194955/2083194989/2083195004/2083195011 같은 경우)
                if '/' in item['idx']:
                    idx_list = item['idx'].split('/')
                else:
                    idx_list.append(item['idx'])

                # invoice no 가 없는 경우
                if not invoice_no:
                    invoice_no_updated_down_form_orders.append(DownFormOrdersInvoiceNoUpdateDto(
                        idx=", ".join(idx_list),
                        invoice_no=invoice_no,
                        message=f"invoice no is empty"
                    ))
                    continue

                for idx in idx_list:
                    # down form orders 에서 idx 로 검색
                    if not await self.get_down_form_order_by_idx(idx):
                        invoice_no_updated_down_form_orders.append(DownFormOrdersInvoiceNoUpdateDto(
                            idx=idx,
                            invoice_no=invoice_no,
                            message=f"idx not found"
                        ))
                        continue

                    # invoice_no 업데이트
                    try:
                        stmt = (
                            update(BaseDownFormOrder)
                            .where(BaseDownFormOrder.idx == idx)
                            .values(invoice_no=invoice_no)
                        )
                        await self.session.execute(stmt)
                        invoice_no_updated_down_form_orders.append(DownFormOrdersInvoiceNoUpdateDto(
                            idx=idx,
                            invoice_no=invoice_no,
                            message=f"success"
                        ))
                    except Exception as e:
                        invoice_no_updated_down_form_orders.append(DownFormOrdersInvoiceNoUpdateDto(
                            idx=idx,
                            invoice_no=invoice_no,
                            message=f"error: {e}"
                        ))
                        continue
            await self.session.commit()
            return invoice_no_updated_down_form_orders
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_orders_by_form_name_without_invoice_no(
        self, 
        form_names: list[str], 
        limit: int = 100,
        order_date_from: Optional[str] = None,
        order_date_to: Optional[str] = None
    ) -> list[BaseDownFormOrder]:
        """
        특정 form_name을 가진 주문 중 invoice_no가 없는 데이터를 조회합니다.
        
        Args:
            form_names: 조회할 form_name 리스트
            limit: 조회할 최대 건수 (기본값: 100)
            order_date_from: 주문 시작 날짜 (YYYY-MM-DD)
            order_date_to: 주문 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            invoice_no가 없는 주문 데이터 리스트
        """
        try:
            from datetime import datetime
            
            query = select(BaseDownFormOrder).where(
                BaseDownFormOrder.form_name.in_(form_names),
                (BaseDownFormOrder.invoice_no == None) | 
                (BaseDownFormOrder.invoice_no == '') |
                (BaseDownFormOrder.invoice_no == 'null')
            )
            
            # 날짜 범위 필터 추가
            if order_date_from:
                try:
                    date_from = datetime.strptime(order_date_from, "%Y-%m-%d")
                    query = query.where(BaseDownFormOrder.order_date >= date_from)
                except ValueError:
                    logger.warning(f"잘못된 날짜 형식: {order_date_from}")
            
            if order_date_to:
                try:
                    date_to = datetime.strptime(order_date_to, "%Y-%m-%d")
                    query = query.where(BaseDownFormOrder.order_date <= date_to)
                except ValueError:
                    logger.warning(f"잘못된 날짜 형식: {order_date_to}")
            
            query = query.order_by(BaseDownFormOrder.id.desc()).limit(limit)
            
            result = await self.session.execute(query)
            return result.scalars().all()
        except Exception as e:
            await self.session.rollback()
            logger.error(f"form_name {form_names} 중 invoice_no가 없는 주문 조회 실패: {str(e)}")
            raise e
        finally:
            await self.session.close()

    async def update_invoice_no_by_idx(self, idx: str, invoice_no: str, batch_id: Optional[int] = None, process_dt: Optional[datetime] = None) -> bool:
        """
        특정 idx의 주문에 invoice_no, batch_id, process_dt를 업데이트합니다.
        
        Args:
            idx: 주문번호
            invoice_no: 운송장번호
            batch_id: 배치 ID (선택사항)
            process_dt: 처리 날짜 (선택사항)
            
        Returns:
            업데이트 성공 여부
        """
        try:
            update_values = {"invoice_no": invoice_no}
            
            if batch_id is not None:
                update_values["batch_id"] = batch_id
            if process_dt is not None:
                update_values["process_dt"] = process_dt
            
            stmt = (
                update(BaseDownFormOrder)
                .where(BaseDownFormOrder.idx == idx)
                .values(**update_values)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"주문번호 {idx}의 invoice_no를 {invoice_no}로 업데이트 완료 (batch_id: {batch_id})")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"주문번호 {idx}의 invoice_no 업데이트 실패: {str(e)}")
            raise e