"""
이카운트 배치 통합 서비스
"""
import asyncio
import time
import json
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from utils.logs.sabangnet_logger import get_logger
from utils.mappings.down_form_to_ecount_mapping import DownFormOrderToEcountMapper
from repository.ecount_sale_repository import EcountSaleRepository, DownFormOrderRepository
from services.ecount.ecount_auth_service import EcountAuthManager
from services.ecount.ecount_sale_service import EcountSaleService
from schemas.ecount.sale_schemas import (
    EcountBatchProcessRequest, EcountBatchProcessResult, 
    EcountBatchProcessResponse, EcountSaleDto, to_api_dict, from_api_dict
)


logger = get_logger(__name__)


class EcountBatchIntegrationService:
    """이카운트 배치 통합 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ecount_sale_repository = EcountSaleRepository(session)
        self.down_form_order_repository = DownFormOrderRepository(session)
        self.mapper = DownFormOrderToEcountMapper()
        self.auth_manager = EcountAuthManager()
        self.sale_service = EcountSaleService()
        
        # 설정
        self.batch_size = 50  # 한 번에 처리할 배치 크기
        self.max_concurrent = 10  # 최대 동시 처리 수
        self.retry_count = 3  # 재시도 횟수
    
    async def process_orders_by_condition(
        self, 
        request: EcountBatchProcessRequest
    ) -> EcountBatchProcessResponse:
        """조건에 따라 주문을 조회하고 이카운트로 전송하는 배치 처리"""
        start_time = time.time()
        
        try:
            logger.info(f"이카운트 배치 처리 시작: {request.order_from} ~ {request.order_to}")
            
            # 1. 인증 정보 가져오기
            auth_dict = request.auth_info
            com_code = auth_dict["com_code"]
            user_id = auth_dict["user_id"]
            api_cert_key = auth_dict["api_cert_key"]
            
            auth_info = await self.auth_manager.get_authenticated_info(
                com_code, user_id, api_cert_key, request.is_test
            )
            
            if not auth_info:
                raise Exception("이카운트 인증 실패")
            
            # 2. 전체 주문 수 조회
            total_orders = 0
            processed_orders = 0
            success_count = 0
            fail_count = 0
            skipped_count = 0
            ecount_sales = []
            errors = []
            
            page = 1
            
            while True:
                # 3. 페이지별 주문 조회
                orders, total_count = await self.down_form_order_repository.get_orders_by_condition(
                    order_from=request.order_from,
                    order_to=request.order_to,
                    template_code=request.template_code,
                    page=page,
                    page_size=request.page_size,
                    exclude_erp_sent=True
                )
                
                if page == 1:
                    total_orders = total_count
                
                if not orders:
                    break
                
                logger.info(f"페이지 {page}: {len(orders)}건 처리 중...")
                
                # 4. 이미 전송된 주문 확인
                order_ids = [order.idx for order in orders]
                already_sent = await self.down_form_order_repository.get_already_sent_orders(order_ids)
                
                # 5. 전송할 주문만 필터링
                orders_to_process = [order for order in orders if order.idx not in already_sent]
                skipped_count += len(already_sent)
                
                if orders_to_process:
                    # 6. 배치 처리
                    batch_result = await self._process_order_batch(
                        orders_to_process, auth_info, request.is_test, com_code, user_id
                    )
                    
                    processed_orders += batch_result['processed']
                    success_count += batch_result['success']
                    fail_count += batch_result['fail']
                    ecount_sales.extend(batch_result['ecount_sales'])
                    errors.extend(batch_result['errors'])
                
                page += 1
                
                # 너무 많은 페이지 처리 방지 (안전장치)
                if page > 100:
                    logger.warning("100페이지 이상 처리 중단")
                    break
            
            # 7. 결과 생성
            processing_time = time.time() - start_time
            
            result = EcountBatchProcessResult(
                total_orders=total_orders,
                processed_orders=processed_orders,
                success_count=success_count,
                fail_count=fail_count,
                skipped_count=skipped_count,
                ecount_sales=ecount_sales,
                errors=errors,
                processing_time=processing_time
            )
            
            logger.info(f"배치 처리 완료: 총 {total_orders}건 중 {success_count}건 성공, {fail_count}건 실패, {skipped_count}건 건너뜀")
            
            return EcountBatchProcessResponse(
                success=fail_count == 0,
                message=f"배치 처리 완료: {success_count}건 성공, {fail_count}건 실패",
                result=result
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"배치 처리 중 오류: {e}")
            
            result = EcountBatchProcessResult(
                total_orders=0,
                processed_orders=0,
                success_count=0,
                fail_count=0,
                skipped_count=0,
                ecount_sales=[],
                errors=[str(e)],
                processing_time=processing_time
            )
            
            return EcountBatchProcessResponse(
                success=False,
                message=f"배치 처리 실패: {str(e)}",
                result=result
            )
    
    async def _process_order_batch(
        self,
        orders: List,
        auth_info,
        is_test: bool,
        com_code: str,
        user_id: str
    ) -> dict:
        """주문 배치를 처리합니다."""
        processed = 0
        success = 0
        fail = 0
        ecount_sales = []
        errors = []
        successful_order_ids = []
        
        try:
            # 작은 배치로 나누어 처리
            for i in range(0, len(orders), self.batch_size):
                batch_orders = orders[i:i + self.batch_size]
                
                # 동시 처리를 위한 태스크 생성
                tasks = []
                for order in batch_orders:
                    task = self._process_single_order(order, auth_info, is_test, com_code, user_id)
                    tasks.append(task)
                
                # 동시 실행 (제한된 수)
                semaphore = asyncio.Semaphore(self.max_concurrent)
                
                async def process_with_semaphore(task):
                    async with semaphore:
                        return await task
                
                results = await asyncio.gather(
                    *[process_with_semaphore(task) for task in tasks],
                    return_exceptions=True
                )
                
                # 결과 처리
                for order, result in zip(batch_orders, results):
                    processed += 1
                    
                    if isinstance(result, Exception):
                        fail += 1
                        error_msg = f"주문 {order.idx} 처리 실패: {str(result)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                    elif result and result['success']:
                        success += 1
                        ecount_sales.append(result['ecount_sale'])
                        successful_order_ids.append(order.idx)
                    else:
                        fail += 1
                        error_msg = f"주문 {order.idx} 처리 실패: {result.get('error', '알 수 없는 오류')}"
                        errors.append(error_msg)
                
                # 짧은 대기 (API 제한 고려)
                await asyncio.sleep(0.1)
            
            # 성공한 주문들의 상태 업데이트
            if successful_order_ids:
                await self.down_form_order_repository.update_work_status_to_erp_sent(successful_order_ids)
            
        except Exception as e:
            error_msg = f"배치 처리 중 오류: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        return {
            'processed': processed,
            'success': success,
            'fail': fail,
            'ecount_sales': ecount_sales,
            'errors': errors
        }
    
    async def _process_single_order(
        self,
        order,
        auth_info,
        is_test: bool,
        com_code: str,
        user_id: str
    ) -> dict:
        """단일 주문을 처리합니다."""
        try:
            # 1. 매핑
            sale_dto = self.mapper.map_to_ecount_sale_dto(order, com_code, user_id)
            sale_dto = self.mapper.calculate_price_and_vat(sale_dto)
            sale_dto.is_test = is_test
            
            # 2. 검증
            validation_errors = self.mapper.validate_mapped_data(sale_dto)
            if validation_errors:
                return {
                    'success': False,
                    'error': f"데이터 검증 실패: {', '.join(validation_errors)}"
                }
            
            # 3. 이카운트 판매 요청 생성
            simple_request = to_api_dict(sale_dto)
            
            # 4. 이카운트 전송
            sale_response = await self.sale_service.create_simple_sale(simple_request, is_test)
            
            if not sale_response:
                return {
                    'success': False,
                    'error': "이카운트 전송 실패"
                }
            
            # 5. 응답 처리
            api_sale_response = from_api_dict(sale_response, EcountSaleDto)
            
            if api_sale_response.is_success:
                sale_dto.is_success = True
                sale_dto.slip_no = api_sale_response.slip_no
                sale_dto.trace_id = api_sale_response.trace_id
            else:
                sale_dto.is_success = False
                sale_dto.error_message = api_sale_response.error_message
            
            # 6. DB 저장
            await self.ecount_sale_repository.save_ecount_sale(sale_dto)
            
            return {
                'success': sale_dto.is_success,
                'ecount_sale': sale_dto,
                'error': sale_dto.error_message if not sale_dto.is_success else None
            }
            
        except Exception as e:
            logger.error(f"단일 주문 처리 중 오류: {e}")
            return {
                'success': False,
                'error': str(e)
            }
