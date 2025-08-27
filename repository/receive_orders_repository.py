from typing import Any
from sqlalchemy import select, and_
from datetime import date, datetime
from utils.logs.sabangnet_logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from models.receive_orders.receive_orders import ReceiveOrders
from sqlalchemy.dialects.postgresql import insert as pg_insert


logger = get_logger(__name__)


class ReceiveOrdersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_orders(self, obj_in: ReceiveOrders) -> ReceiveOrders:
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

    async def get_order_by_idx(self, idx: str) -> ReceiveOrders:
        try:
            query = select(ReceiveOrders).where(ReceiveOrders.idx == idx)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_orders(self, skip: int = None, limit: int = None) -> list[ReceiveOrders]:
        """
        주문 데이터 전체 조회
        Args:
            skip: 건너뛸 개수
            limit: 조회할 개수
        Returns:
            ReceiveOrders 리스트
        """
        try:
            stmt = select(ReceiveOrders).order_by(ReceiveOrders.id)
            if skip is not None:
                stmt = stmt.offset(skip)
            if limit is not None:
                stmt = stmt.limit(limit)
            result = await self.session.execute(stmt)
            content = result.scalars().all()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_orders_pagination(self, page: int = 1, page_size: int = 20) -> list[ReceiveOrders]:
        """
        주문 데이터 페이징 조회
        Args:
            page: 페이지 번호
            page_size: 페이지 당 조회할 개수
        Returns:
            ReceiveOrders 리스트
        """
        try:
            query = select(ReceiveOrders).offset(
                (page - 1) * page_size).limit(page_size).order_by(ReceiveOrders.id)
            result = await self.session.execute(query)
            content = result.scalars().all()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_orders_by_receive_zipcode_and_receive_addr_and_receive_name(
            self,
            receive_zipcode: str,
            receive_addr: str,
            receive_name: str
        ) -> list[ReceiveOrders]:
        """
        배송지 정보로 합포장용 주문 데이터 조회
        Args:
            receive_zipcode: 배송지 우편번호
            receive_addr: 배송지 주소
            receive_name: 배송지 이름
        Returns:
            ReceiveOrders 리스트
        """
        try:
            query = select(ReceiveOrders).where(
                ReceiveOrders.receive_zipcode == receive_zipcode,
                ReceiveOrders.receive_addr == receive_addr,
                ReceiveOrders.receive_name == receive_name
            )
            result = await self.session.execute(query)
            content = result.scalars().all()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def get_orders_by_receive_zipcode_and_receive_addr_and_receive_name_and_mall_user_id(
            self,
            receive_zipcode: str,
            receive_addr: str,
            receive_name: str,
            mall_user_id: str
        ) -> list[ReceiveOrders]:
        """
        배송지 정보와 유저 쇼핑몰 아이디로 합포장용 주문 데이터 조회
        Args:
            receive_zipcode: 배송지 우편번호
            receive_addr: 배송지 주소
            receive_name: 배송지 이름
            mall_user_id: 유저 쇼핑몰 아이디
        Returns:
            ReceiveOrders 리스트
        """
        try:
            query = select(ReceiveOrders).where(
                ReceiveOrders.receive_zipcode == receive_zipcode,
                ReceiveOrders.receive_addr == receive_addr,
                ReceiveOrders.receive_name == receive_name,
                ReceiveOrders.mall_user_id == mall_user_id
            )
            result = await self.session.execute(query)
            content = result.scalars().all()
            return content
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def query_create_orders(self, obj_in: dict) -> dict:
        try:
            query = pg_insert(ReceiveOrders).values(obj_in)
            query = query.on_conflict_do_update(
                index_elements=['idx'], set_=obj_in)
            await self.session.execute(query)
            await self.session.commit()
            return obj_in
        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await self.session.close()

    async def bulk_insert_orders(self, orders: list[dict]) -> list[ReceiveOrders]:
        """
        주문 데이터 배치 삽입 (중복 시 무시)
        Args:
            orders: 주문 데이터 dict 리스트
        Returns:
            저장된 ReceiveOrders 모델 리스트
        """
        try:
            order_model_list = [ReceiveOrders(**order) for order in orders]
            order_dict_list = []
            for order_model in order_model_list:
                # 누락된 필드를 None으로 채워 넣기
                order_dict_list.append(order_model.to_dict(exclude_fields={"id"}))
            
            # 배치 크기 제한 (PostgreSQL 파라미터 한계 고려)
            # receive_orders 테이블은 컬럼이 많아서 배치 크기를 작게 설정
            # 100개 × 100컬럼 = 10,000 파라미터 (안전한 범위)
            batch_size = 50  # 한 번에 50개씩 처리 (더 안전하게)
            all_success_models = []
            
            total_attempted = len(order_dict_list)
            total_batches = (total_attempted + batch_size - 1) // batch_size
            
            for i in range(0, len(order_dict_list), batch_size):
                batch = order_dict_list[i:i + batch_size]
                batch_num = i // batch_size + 1
                logger.info(f"배치 처리 중: {batch_num}/{total_batches} ({len(batch)}개 시도)")
                
                # PostgreSQL bulk insert
                stmt = pg_insert(ReceiveOrders).values(batch)
                stmt = stmt.on_conflict_do_nothing(index_elements=['idx'])
                stmt = stmt.returning(ReceiveOrders)
                result = await self.session.execute(stmt)
                
                # 배치별 결과 수집
                returned_rows = result.fetchall()
                batch_success_models = [row[0] for row in returned_rows]
                all_success_models.extend(batch_success_models)
                
                # 배치별 통계 로그
                batch_attempted = len(batch)
                batch_success = len(batch_success_models)
                batch_duplicated = batch_attempted - batch_success
                
                if batch_duplicated > 0:
                    # 중복된 idx 값들 찾기 (선택적으로 로그 출력)
                    success_idx_set = {model.idx for model in batch_success_models}
                    attempted_idx_list = [item.get('idx') for item in batch]
                    duplicated_idx_list = [idx for idx in attempted_idx_list if idx not in success_idx_set]
                    
                    logger.info(f"배치 {batch_num} 완료: {batch_success}개 성공, {batch_duplicated}개 중복값 무시")
                    logger.debug(f"중복된 idx: {duplicated_idx_list[:5]}{'...' if len(duplicated_idx_list) > 5 else ''}")
                else:
                    logger.info(f"배치 {batch_num} 완료: {batch_success}개 성공, {batch_duplicated}개 중복값 무시")
            
            await self.session.commit()
            
            # 전체 결과 요약
            total_success = len(all_success_models)
            total_duplicated = total_attempted - total_success
            
            logger.info(f"전체 결과: {total_attempted}개 시도, {total_success}개 성공, {total_duplicated}개 중복값 무시")
            return all_success_models
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"배치 삽입 실패: {e}")
            raise e
        finally:
            await self.session.close()


    def _parse_date_to_string(self, val):
        """날짜를 reg_date 필드에 맞는 문자열 형식으로 변환 (YYYYMMDD 형식)"""
        if isinstance(val, date):
            return val.strftime("%Y%m%d")
        if isinstance(val, str):
            # YYYY-MM-DD 형식을 YYYYMMDD 형식으로 변환
            return datetime.strptime(val, "%Y-%m-%d").strftime("%Y%m%d")
        return val


    async def get_receive_orders_by_filters(self, filters: dict[str, Any]) -> list[ReceiveOrders]:
        query = select(ReceiveOrders)
        conditions = []
        if filters:
            if 'date_from' in filters and filters['date_from']:
                # reg_date는 String 타입이므로 문자열 비교 사용
                date_from_str = self._parse_date_to_string(filters['date_from'])
                conditions.append(ReceiveOrders.reg_date >= date_from_str)
            if 'date_to' in filters and filters['date_to']:
                # reg_date는 String 타입이므로 문자열 비교 사용
                date_to_str = self._parse_date_to_string(filters['date_to'])
                conditions.append(ReceiveOrders.reg_date <= date_to_str)
            if 'mall_id' in filters and filters['mall_id']:
                conditions.append(ReceiveOrders.mall_id == filters['mall_id'])
            if 'order_status' in filters and filters['order_status']:
                conditions.append(ReceiveOrders.order_status == filters['order_status'])
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(ReceiveOrders.id)
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return rows
        # # dict 변환 (기존 asyncpg와 유사하게)
        # return [row.__dict__ for row in rows]
