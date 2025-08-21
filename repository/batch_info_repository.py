from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.macro_batch_processing.batch_process import BatchProcess
from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto


class BatchInfoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_batch_info_paginated(self, page: int, page_size: int):
        """
        배치 프로세스 정보를 페이지네이션하여 반환
        :param session: 비동기 세션
        :param page: 페이지 번호 (1부터 시작)
        :param page_size: 페이지 당 개수
        :return: (BatchProcess 리스트, 전체 개수)
        """
        offset = (page - 1) * page_size
        stmt = select(BatchProcess).offset(offset).limit(page_size)
        total_stmt = select(func.count()).select_from(BatchProcess)
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()
        return items, total
    
    async def save_batch_info(self, batch_dto: BatchProcessDto) -> BatchProcess:
        """
        배치 프로세스 정보를 DB에 저장하는 함수
        :param session: 비동기 세션
        :param batch_dto: BatchProcessDto 객체
        :return: 저장된 BatchProcess ORM 객체
        """
        batch_obj = batch_dto.to_orm(BatchProcess)
        self.session.add(batch_obj)
        await self.session.commit()
        await self.session.refresh(batch_obj)
        return batch_obj
    
    async def update_batch_info(self, batch_dto: BatchProcessDto) -> bool:
        """
        배치 프로세스 정보를 업데이트하는 함수
        :param batch_dto: BatchProcessDto 객체 (batch_id 필수)
        :return: 업데이트 성공 여부
        """
        try:
            if not batch_dto.batch_id:
                raise ValueError("batch_id is required for update")
            
            # 업데이트할 필드들만 추출
            update_data = {}
            if batch_dto.file_url is not None:
                update_data['file_url'] = batch_dto.file_url
            if batch_dto.file_size is not None:
                update_data['file_size'] = batch_dto.file_size
            if batch_dto.file_name is not None:
                update_data['file_name'] = batch_dto.file_name
            
            if not update_data:
                return True  # 업데이트할 데이터가 없으면 성공으로 처리
            
            stmt = (
                update(BatchProcess)
                .where(BatchProcess.batch_id == batch_dto.batch_id)
                .values(**update_data)
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def get_batch_info_latest(self, page: int, page_size: int):
        """
        최근 배치 프로세스 정보를 각 original_filename별 가장 최근 created_at 기준 페이지네이션하여 반환
        :param session: 비동기 세션
        :param page: 페이지 번호 (1부터 시작)
        :param page_size: 페이지 당 개수
        :return: (BatchProcess 리스트, 전체 개수)
        """
        offset = (page - 1) * page_size
        # 1. Get subquery for latest created_at per original_filename
        from sqlalchemy import distinct, desc
        from sqlalchemy.orm import aliased
        
        subq = (
            select(
                BatchProcess.original_filename,
                func.max(BatchProcess.created_at).label("max_created_at")
            )
            .group_by(BatchProcess.original_filename)
            .subquery()
        )
        
        # 2. Join with main table to get full row
        stmt = (
            select(BatchProcess)
            .join(
                subq,
                (BatchProcess.original_filename == subq.c.original_filename) &
                (BatchProcess.created_at == subq.c.max_created_at)
            )
            .order_by(BatchProcess.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()
        # 3. Get total count of unique original_filename
        total_stmt = select(func.count(distinct(BatchProcess.original_filename)))
        total_result = await self.session.execute(total_stmt)
        total = total_result.scalar_one()
        return items, total

