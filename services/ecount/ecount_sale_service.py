"""
이카운트 판매 서비스
"""
import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from utils.logs.sabangnet_logger import get_logger
from schemas.ecount.sale_schemas import (
    EcountSaleDto, 
    EcountApiRequest, 
    EcountApiResponse,
    convert_dto_to_ecount_api_request,
    snake_to_upper_snake
)
from schemas.ecount.auth_schemas import EcountAuthInfo
from .ecount_auth_service import EcountAuthManager
from utils.api_client import aiohttp_post


logger = get_logger(__name__)


class EcountSaleService:
    """이카운트 판매 서비스"""
    
    def __init__(self):
        self.test_sale_base_url = "https://sboapi{}.ecount.com/OAPI/V2/Sale/SaveSale"
        self.prod_sale_base_url = "https://oapi{}.ecount.com/OAPI/V2/Sale/SaveSale"
        self.session_timeout = 60  # seconds
        self.auth_manager = EcountAuthManager()
    
    def _build_sale_url(self, auth_info: EcountAuthInfo, is_test: bool = True) -> str:
        """판매 API URL을 구성합니다."""
        base_url = self.test_sale_base_url if is_test else self.prod_sale_base_url
        url = base_url.format(auth_info.zone + auth_info.domain)
        return f"{url}?SESSION_ID={auth_info.session_id}"
    
    def _convert_simple_to_full_request(self, simple_request: EcountSaleDto) -> EcountSaleDto:
        """간단한 요청을 전체 요청 형식으로 변환합니다."""
        # 현재 날짜를 기본값으로 사용
        io_date = simple_request.io_date or datetime.now().strftime("%Y%m%d")
        
        bulk_data = EcountSaleDto(
            UPLOAD_SER_NO=simple_request.upload_ser_no,
            IO_DATE=io_date,
            CUST=simple_request.cust,
            CUST_DES=simple_request.cust_des,
            WH_CD=simple_request.wh_cd,
            PROD_CD=simple_request.prod_cd,
            PROD_DES=simple_request.prod_des,
            QTY=simple_request.qty,
            PRICE=simple_request.price,
            SUPPLY_AMT=simple_request.supply_amt,
            VAT_AMT=simple_request.vat_amt,
            REMARKS=simple_request.remarks
        )
        
        sale_item = EcountSaleDto(BulkDatas=bulk_data)
        return EcountSaleDto(SaleList=[sale_item])
    
    async def create_sale(self, sale_request: EcountSaleDto, auth_info: EcountAuthInfo, is_test: bool = True) -> Optional[EcountApiResponse]:
        """판매를 생성합니다."""
        try:
            # DTO를 API 요청 형식으로 변환
            sale_dtos = [sale_request]
            api_request = convert_dto_to_ecount_api_request(sale_dtos)
            
            url = self._build_sale_url(auth_info, is_test)
            request_data = api_request.model_dump(exclude_unset=True)
            
            data, status, error = await aiohttp_post(url, request_data, timeout=self.session_timeout, logger=logger)
            
            if status == 200 and data:
                try:
                    api_response = EcountApiResponse(**data)
                    if api_response.Status == "200":
                        logger.info(f"판매 생성 성공: {api_response.Data.SuccessCnt}건 성공, {api_response.Data.FailCnt}건 실패")
                    else:
                        logger.warning(f"판매 생성 부분 실패: {api_response.Error}")
                    return api_response
                except Exception as e:
                    logger.error(f"응답 파싱 실패: {e}")
                    return None
            else:
                logger.error(f"판매 생성 실패: {error or status}")
                return None
        except Exception as e:
            logger.error(f"판매 생성 중 예외 발생: {e}")
            return None
    
    async def create_simple_sale(self, simple_request: EcountSaleDto, is_test: bool = True) -> Optional[EcountSaleDto]:
        """간단한 판매 요청으로 판매를 생성합니다."""
        auth_dict = simple_request.auth_info
        com_code = auth_dict["com_code"]
        user_id = auth_dict["user_id"]
        api_cert_key = auth_dict["api_cert_key"]
        auth_info = await self.auth_manager.get_authenticated_info(
            com_code, user_id, api_cert_key, is_test
        )
        if not auth_info:
            logger.error("인증 실패")
            return None
        sale_request = self._convert_simple_to_full_request(simple_request)
        return await self.create_sale(sale_request, auth_info, is_test)
    
    async def create_bulk_sales(self, sale_items: List[EcountSaleDto], auth_info: EcountAuthInfo, is_test: bool = True) -> Optional[EcountApiResponse]:
        """여러 판매를 일괄 생성합니다."""
        try:
            # DTO를 API 요청 형식으로 변환
            api_request = convert_dto_to_ecount_api_request(sale_items)
            
            url = self._build_sale_url(auth_info, is_test)
            request_data = api_request.model_dump(exclude_unset=True)
            
            data, status, error = await aiohttp_post(url, request_data, timeout=self.session_timeout, logger=logger)
            
            if status == 200 and data:
                try:
                    api_response = EcountApiResponse(**data)
                    if api_response.Status == "200":
                        logger.info(f"배치 판매 생성 성공: {api_response.Data.SuccessCnt}건 성공, {api_response.Data.FailCnt}건 실패")
                    else:
                        logger.warning(f"배치 판매 생성 부분 실패: {api_response.Error}")
                    return api_response
                except Exception as e:
                    logger.error(f"응답 파싱 실패: {e}")
                    return None
            else:
                logger.error(f"배치 판매 생성 실패: {error or status}")
                return None
        except Exception as e:
            logger.error(f"배치 판매 생성 중 예외 발생: {e}")
            return None
    
    def validate_sale_data(self, sale_data: EcountSaleDto) -> List[str]:
        """판매 데이터를 검증하고 오류 목록을 반환합니다."""
        errors = []
        logger.info(f"판매 데이터 검증: {sale_data}")
        # 필수 필드 검증
        if not sale_data.wh_cd:
            errors.append("출하창고코드는 필수입니다.")
        
        if not sale_data.prod_cd:
            errors.append("품목코드는 필수입니다.")
        
        if not sale_data.qty or sale_data.qty <= 0:
            errors.append("수량은 0보다 큰 값이어야 합니다.")
        
        # 날짜 형식 검증
        if sale_data.io_date:
            try:
                datetime.strptime(sale_data.io_date, "%Y%m%d")
            except ValueError:
                errors.append("판매일자는 YYYYMMDD 형식이어야 합니다.")
        
        # 금액 검증
        if sale_data.price and sale_data.price < 0:
            errors.append("단가는 음수일 수 없습니다.")
        
        if sale_data.supply_amt and sale_data.supply_amt < 0:
            errors.append("공급가액은 음수일 수 없습니다.")
        
        if sale_data.vat_amt and sale_data.vat_amt < 0:
            errors.append("부가세는 음수일 수 없습니다.")
        
        return errors
    
    def calculate_amounts(self, qty: Decimal, price: Decimal, vat_rate: Decimal = Decimal('0.1')) -> tuple[Decimal, Decimal]:
        """수량과 단가로 공급가액과 부가세를 계산합니다."""
        # float를 Decimal로 변환
        if isinstance(qty, float):
            qty = Decimal(str(qty))
        if isinstance(price, float):
            price = Decimal(str(price))
        if isinstance(vat_rate, float):
            vat_rate = Decimal(str(vat_rate))
        
        supply_amt = qty * price
        vat_amt = supply_amt * vat_rate
        return supply_amt, vat_amt
    
    async def create_sales_with_validation(
        self, 
        sale_dtos: List[EcountSaleDto], 
        auth_info: EcountAuthInfo, 
        is_test: bool = True,
        batch_size: int = 100
    ) -> tuple[Optional[EcountApiResponse], List[str]]:
        """
        검증과 함께 판매를 생성합니다. (단일 또는 배치)
        
        Args:
            sale_dtos: 판매 데이터 DTO 리스트 (단일 데이터도 리스트로 전달)
            auth_info: 인증 정보
            is_test: 테스트 환경 여부
            batch_size: 배치 크기 (기본값: 100)
            
        Returns:
            tuple: (API 응답, 오류 메시지 리스트)
        """
        try:
            if not sale_dtos:
                return None, ["판매 데이터가 없습니다."]
            
            # 1. 모든 데이터 검증
            all_errors = []
            valid_dtos = []
            
            for i, sale_dto in enumerate(sale_dtos):
                errors = self.validate_sale_data(sale_dto)
                if errors:
                    all_errors.append(f"데이터 {i+1}: {', '.join(errors)}")
                else:
                    valid_dtos.append(sale_dto)
            
            if not valid_dtos:
                logger.error(f"모든 판매 데이터 검증 실패: {all_errors}")
                return None, all_errors
            
            # 2. 금액 자동 계산
            for sale_dto in valid_dtos:
                if sale_dto.price and not sale_dto.supply_amt:
                    qty = Decimal(str(sale_dto.qty)) if sale_dto.qty else Decimal('0')
                    price = Decimal(str(sale_dto.price)) if sale_dto.price else Decimal('0')
                    supply_amt, vat_amt = self.calculate_amounts(qty, price)
                    sale_dto.supply_amt = float(supply_amt)
                    if not sale_dto.vat_amt:
                        sale_dto.vat_amt = float(vat_amt)
            
            # 3. 배치 크기로 분할
            batches = [valid_dtos[i:i + batch_size] for i in range(0, len(valid_dtos), batch_size)]
            
            # 4. 각 배치별로 API 요청
            all_responses = []
            batch_errors = []
            
            for batch_idx, batch in enumerate(batches):
                try:
                    # DTO를 API 요청 형식으로 변환
                    api_request = convert_dto_to_ecount_api_request(batch)
                    
                    # API 요청 URL 구성
                    url = self._build_sale_url(auth_info, is_test)
                    
                    # API 요청 데이터 준비
                    request_data = api_request.model_dump(exclude_unset=True)
                    
                    logger.info(f"배치 {batch_idx + 1}/{len(batches)} API 요청 전송: {len(batch)}건")
                    logger.debug(f"배치 {batch_idx + 1} 요청 데이터: {request_data}")
                    
                    # API 요청 전송
                    response_data, status, error = await aiohttp_post(
                        url=url, 
                        json=request_data, 
                        timeout=self.session_timeout, 
                        logger=logger
                    )
                    
                    # 응답 처리
                    if error:
                        batch_errors.append(f"배치 {batch_idx + 1} API 요청 실패: {error}")
                        continue
                    
                    if not response_data:
                        batch_errors.append(f"배치 {batch_idx + 1} API 응답 없음: HTTP {status}")
                        continue
                    
                    # 응답 데이터 파싱
                    try:
                        # 응답 데이터 로깅 (디버깅용)
                        logger.debug(f"배치 {batch_idx + 1} 응답 데이터: {response_data}")
                        
                        api_response = EcountApiResponse(**response_data)
                        all_responses.append(api_response)
                        
                        logger.info(f"배치 {batch_idx + 1} 성공: {api_response.Data.SuccessCnt}건 성공, {api_response.Data.FailCnt}건 실패")
                        
                        # 성공한 경우 응답 데이터를 DTO에 업데이트
                        if api_response.Data.SuccessCnt > 0 and api_response.Data.SlipNos:
                            for i, sale_dto in enumerate(batch):
                                if i < len(api_response.Data.SlipNos):
                                    sale_dto.slip_no = api_response.Data.SlipNos[i]
                                sale_dto.trace_id = api_response.Data.TRACE_ID
                                sale_dto.is_success = True
                        
                    except Exception as e:
                        logger.error(f"배치 {batch_idx + 1} 응답 파싱 실패: {str(e)}")
                        logger.error(f"응답 데이터: {response_data}")
                        batch_errors.append(f"배치 {batch_idx + 1} 응답 파싱 실패: {str(e)}")
                        continue
                        
                except Exception as e:
                    batch_errors.append(f"배치 {batch_idx + 1} 처리 중 오류: {str(e)}")
                    continue
            
            # 5. 전체 결과 정리
            if not all_responses:
                return None, batch_errors + all_errors
            
            # 마지막 응답을 대표 응답으로 사용
            final_response = all_responses[-1]
            
            # 모든 오류 메시지 합치기
            all_error_messages = all_errors + batch_errors
            
            return final_response, all_error_messages
            
        except Exception as e:
            logger.error(f"판매 생성 중 예외 발생: {e}")
            return None, [f"처리 중 오류 발생: {str(e)}"]

    async def create_sale_with_validation(self, sale_data: EcountSaleDto, auth_info: EcountAuthInfo, is_test: bool = True) -> tuple[Optional[EcountApiResponse], List[str]]:
        """
        단일 판매 데이터를 검증하고 생성합니다. (기존 메서드와의 호환성을 위해 유지)
        
        Args:
            sale_data: 판매 데이터 DTO
            auth_info: 인증 정보
            is_test: 테스트 환경 여부
            
        Returns:
            tuple: (API 응답, 오류 메시지 리스트)
        """
        return await self.create_sales_with_validation([sale_data], auth_info, is_test, batch_size=1)

    async def create_bulk_sales_with_validation(
        self, 
        sale_dtos: List[EcountSaleDto], 
        auth_info: EcountAuthInfo, 
        is_test: bool = True,
        batch_size: int = 100
    ) -> tuple[Optional[EcountApiResponse], List[str]]:
        """
        여러 판매 데이터를 배치로 검증하고 생성합니다. (기존 메서드와의 호환성을 위해 유지)
        
        Args:
            sale_dtos: 판매 데이터 DTO 리스트
            auth_info: 인증 정보
            is_test: 테스트 환경 여부
            batch_size: 배치 크기
            
        Returns:
            tuple: (API 응답, 오류 메시지 리스트)
        """
        return await self.create_sales_with_validation(sale_dtos, auth_info, is_test, batch_size)
