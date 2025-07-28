"""
한진 API 운송장 출력 서비스
"""
from typing import Optional, List
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from schemas.hanjin.hanjin_printWbls_dto import PrintWblsRequest, PrintWblsResponse, CreatePrintwblsFromDownFormOrdersResponse, ProcessPrintwblsWithApiResponse
from repository.hanjin_printwbls_repository import HanjinPrintwblsRepository
from core.settings import SETTINGS


logger = get_logger(__name__)


class HanjinPrintService:
    """한진 API 운송장 출력 서비스"""
    
    def __init__(self, session: AsyncSession = None):
        self.api_base_url = "https://ebbapd.hjt.co.kr"
        self.print_wbls_endpoint = "/v1/wbl/{client_id}/print-wbls"
        # 환경변수에서 한진 API 설정 가져오기
        self.x_api_key = SETTINGS.HANJIN_API
        self.default_client_id = SETTINGS.HANJIN_CLIENT_ID
        self.hanjin_csr_num = SETTINGS.HANJIN_CSR_NUM
        # 데이터베이스 세션
        self.session = session
    
    def get_x_api_key(self) -> Optional[str]:
        """환경변수에서 x-api-key를 가져옵니다."""
        return self.x_api_key
    
    def get_default_client_id(self) -> Optional[str]:
        """환경변수에서 기본 client_id를 가져옵니다."""
        return self.default_client_id
    
    def get_hanjin_csr_num(self) -> Optional[str]:
        """환경변수에서 한진 계약번호를 가져옵니다."""
        return self.hanjin_csr_num
    
    def validate_env_vars(self) -> bool:
        """환경변수가 올바르게 설정되었는지 검증합니다."""
        if not self.x_api_key:
            logger.error("환경변수 HANJIN_API가 설정되지 않았습니다.")
            return False
        
        if not self.default_client_id:
            logger.error("환경변수 HANJIN_CLIENT_ID가 설정되지 않았습니다.")
            return False
        
        if not self.hanjin_csr_num:
            logger.error("환경변수 HANJIN_CSR_NUM이 설정되지 않았습니다.")
            return False
        
        logger.info("환경변수 검증 성공")
        return True
    
    def validate_address_list(self, address_list: List) -> bool:
        """주소 목록의 유효성을 검증합니다."""
        if not address_list:
            logger.error("주소 목록이 비어있습니다.")
            return False
        
        if len(address_list) > 100:
            logger.error(f"주소 목록이 최대 건수(100건)를 초과했습니다: {len(address_list)}건")
            return False
        
        for i, address in enumerate(address_list):
            if not address.address:
                logger.error(f"주소 목록 {i+1}번째 항목에 배송지 주소가 없습니다.")
                return False
            
            if not address.snd_zip:
                logger.error(f"주소 목록 {i+1}번째 항목에 출발지 우편번호가 없습니다.")
                return False
        
        logger.info(f"주소 목록 검증 성공: {len(address_list)}건")
        return True
    
    async def request_print_wbls_from_hanjin_api(
        self, 
        client_id: str, 
        x_api_key: str, 
        print_request: PrintWblsRequest
    ) -> PrintWblsResponse:
        """
        한진 API의 print-wbls 엔드포인트에 직접 요청하여 운송장 분류정보를 받아옵니다.
        
        Args:
            client_id: 고객사 코드
            x_api_key: API 키
            print_request: 운송장 출력 요청 데이터
            
        Returns:
            한진 API에서 받은 운송장 출력 응답 데이터
        """
        try:
            url = f"{self.api_base_url}{self.print_wbls_endpoint.format(client_id=client_id)}"
            headers = {
                "x-api-key": x_api_key,
                "Content-Type": "application/json"
            }
            
            # 요청 데이터 준비
            request_data = {
                "client_id": self.default_client_id,
                "address_list": [
                    {
                        "csr_num": address.csr_num or self.hanjin_csr_num,
                        "address": address.address,
                        "snd_zip": address.snd_zip,
                        "rcv_zip": address.rcv_zip or "",
                        "msg_key": address.msg_key or ""
                    }
                    for address in print_request.address_list
                ]
            }
            
            logger.info(f"한진 API print-wbls 요청: {url}, client_id={client_id}, 건수={len(print_request.address_list)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_data, headers=headers) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"한진 API print-wbls 응답 성공: {response_data}")
                        
                        # 응답 데이터 검증 및 변환
                        try:
                            return PrintWblsResponse(**response_data)
                        except Exception as validation_error:
                            logger.error(f"응답 데이터 검증 실패: {validation_error}")
                            # 원본 데이터를 그대로 반환하되 로그는 남김
                            return response_data
                    else:
                        error_text = await response.text()
                        logger.error(f"한진 API print-wbls 요청 실패: {response.status}, {error_text}")
                        raise ValueError(f"한진 API print-wbls 요청 실패: {response.status} - {error_text}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"한진 API print-wbls 네트워크 오류: {str(e)}")
            raise ValueError(f"네트워크 오류: {str(e)}")
        except Exception as e:
            logger.error(f"한진 API print-wbls 요청 중 예외 발생: {str(e)}")
            raise
    
    async def generate_print_wbls_with_env_vars_from_api(
        self, 
        print_request: PrintWblsRequest
    ) -> PrintWblsResponse:
        """
        환경변수에서 설정을 가져와서 한진 API에 print-wbls 요청합니다.
        
        Args:
            print_request: 운송장 출력 요청 데이터
            
        Returns:
            한진 API에서 받은 운송장 출력 응답 데이터
        """
        try:
            # 환경변수 검증
            if not self.x_api_key:
                raise ValueError("환경변수 HANJIN_API가 설정되지 않았습니다.")
            
            if not self.default_client_id:
                raise ValueError("환경변수 HANJIN_CLIENT_ID가 설정되지 않았습니다.")
            
            if not self.hanjin_csr_num:
                raise ValueError("환경변수 HANJIN_CSR_NUM이 설정되지 않았습니다.")
            
            # 주소 목록 검증
            if not self.validate_address_list(print_request.address_list):
                raise ValueError("주소 목록 검증에 실패했습니다.")
            
            # csr_num이 없는 경우 환경변수에서 가져와서 설정
            for address in print_request.address_list:
                if not address.csr_num:
                    address.csr_num = self.hanjin_csr_num
            
            # 한진 API에 직접 요청
            response = await self.request_print_wbls_from_hanjin_api(
                self.default_client_id,
                self.x_api_key,
                print_request
            )
            
            logger.info(f"환경변수로 한진 API print-wbls 요청 완료: client_id={self.default_client_id}")
            return response
            
        except Exception as e:
            logger.error(f"환경변수 한진 API print-wbls 요청 실패: {str(e)}")
            raise
    
    async def save_printwbls_to_database(
        self, 
        print_response: PrintWblsResponse, 
        idx: Optional[str] = None
    ) -> List:
        """
        운송장 출력 응답 결과를 데이터베이스에 저장합니다.
        
        Args:
            print_response: 한진 API 응답 데이터
            idx: 주문번호 (선택사항)
            
        Returns:
            저장된 레코드 리스트
        """
        if not self.session:
            logger.warning("데이터베이스 세션이 없어 저장을 건너뜁니다.")
            return []
        
        if not print_response.address_list:
            logger.warning("저장할 주소 목록이 없습니다.")
            return []
        
        try:
            repository = HanjinPrintwblsRepository(self.session)
            saved_records = await repository.create_multiple_printwbls_records(
                print_response.address_list, 
                idx
            )
            
            logger.info(f"운송장 출력 결과 {len(saved_records)}건을 데이터베이스에 저장했습니다.")
            return saved_records
            
        except Exception as e:
            logger.error(f"데이터베이스 저장 실패: {str(e)}")
            raise
    
    async def generate_print_wbls_with_env_vars_from_api_and_save(
        self, 
        print_request: PrintWblsRequest,
        idx: Optional[str] = None
    ) -> PrintWblsResponse:
        """
        환경변수에서 설정을 가져와서 한진 API에 print-wbls 요청하고 결과를 데이터베이스에 저장합니다.
        
        Args:
            print_request: 운송장 출력 요청 데이터
            idx: 주문번호 (선택사항)
            
        Returns:
            한진 API에서 받은 운송장 출력 응답 데이터
        """
        # API 요청
        response = await self.generate_print_wbls_with_env_vars_from_api(print_request)
        
        # 데이터베이스 저장
        if self.session:
            await self.save_printwbls_to_database(response, idx)
        
        return response

    async def create_hanjin_printwbls_from_down_form_orders(
        self, 
        limit: int = 100
    ) -> CreatePrintwblsFromDownFormOrdersResponse:
        """
        down_form_orders 테이블에서 invoice_no가 없는 데이터를 조회하여
        hanjin_printwbls 테이블에 입력합니다.
        
        Args:
            limit: 조회할 최대 건수 (기본값: 100)
            
        Returns:
            처리 결과 정보
        """
        if not self.session:
            logger.warning("데이터베이스 세션이 없어 처리를 건너뜁니다.")
            return CreatePrintwblsFromDownFormOrdersResponse(error="데이터베이스 세션이 없습니다.")
        
        try:
            from repository.down_form_order_repository import DownFormOrderRepository
            from repository.hanjin_printwbls_repository import HanjinPrintwblsRepository
            
            # down_form_orders 리포지토리 생성
            down_form_repo = DownFormOrderRepository(self.session)
            
            # invoice_no가 없는 주문 데이터 조회
            orders_without_invoice = await down_form_repo.get_orders_without_invoice_no(limit)
            
            if not orders_without_invoice:
                logger.info("invoice_no가 없는 주문 데이터가 없습니다.")
                return CreatePrintwblsFromDownFormOrdersResponse(
                    message="invoice_no가 없는 주문 데이터가 없습니다.",
                    processed_count=0
                )
            
            # hanjin_printwbls 리포지토리 생성
            printwbls_repo = HanjinPrintwblsRepository(self.session)
            
            # hanjin_printwbls 테이블에 데이터 입력
            created_records = await printwbls_repo.create_from_down_form_orders(orders_without_invoice)
            
            logger.info(f"down_form_orders에서 {len(created_records)}건의 hanjin_printwbls 레코드 생성 완료")
            
            return CreatePrintwblsFromDownFormOrdersResponse(
                message=f"성공적으로 {len(created_records)}건의 레코드를 생성했습니다.",
                processed_count=len(created_records),
                created_records=[
                    {
                        "id": record.id,
                        "idx": record.idx,
                        "prt_add": record.prt_add,
                        "zip_cod": record.zip_cod,
                        # TODO: 임시 send_zip 값 추가. 추후 수정 필요. 
                        "snd_zip": "123456"
                    }
                    for record in created_records
                ]
            )
            
        except Exception as e:
            logger.error(f"down_form_orders에서 hanjin_printwbls 생성 실패: {str(e)}")
            raise

    async def process_hanjin_printwbls_from_db(
        self, 
        limit: int = 100
    ) -> ProcessPrintwblsWithApiResponse:
        """
        hanjin_printwbls 테이블의 데이터를 기반으로 한진 API를 호출하고 응답을 업데이트합니다.
        
        Args:
            limit: 처리할 최대 건수 (기본값: 100)
            
        Returns:
            처리 결과 정보
        """
        if not self.session:
            logger.warning("데이터베이스 세션이 없어 처리를 건너뜁니다.")
            return ProcessPrintwblsWithApiResponse(error="데이터베이스 세션이 없습니다.")
        
        try:
            from repository.hanjin_printwbls_repository import HanjinPrintwblsRepository
            from datetime import datetime
            import random
            
            # hanjin_printwbls 리포지토리 생성
            printwbls_repo = HanjinPrintwblsRepository(self.session)
            
            # API 요청을 위한 레코드 조회
            records = await printwbls_repo.get_records_for_api_request(limit)
            
            if not records:
                logger.info("API 요청을 위한 데이터가 있는 레코드가 없습니다.")
                return ProcessPrintwblsWithApiResponse(
                    message="API 요청을 위한 데이터가 있는 레코드가 없습니다.",
                    processed_count=0
                )
            
            # 현재 날짜로 YYMMDD 형식 생성
            current_date = datetime.now().strftime("%y%m%d")
            
            # API 요청 데이터 준비
            address_list = []
            for i, record in enumerate(records, 1):
                # msg_key 생성: YYMMDD + random num(XX) + 요청개수순서(1,2,3,4,5,...)
                random_num = random.randint(10, 99)
                msg_key = f"{current_date}{random_num:02d}{i:02d}"
                
                address_item = {
                    "csr_num": self.hanjin_csr_num,
                    "address": record.prt_add,
                    "snd_zip": record.snd_zip,
                    "rcv_zip": record.zip_cod,
                    "msg_key": msg_key
                }
                address_list.append(address_item)
            
            # PrintWblsRequest 객체 생성
            from schemas.hanjin.hanjin_printWbls_dto import AddressItem, PrintWblsRequest
            print_request = PrintWblsRequest(
                address_list=[AddressItem(**item) for item in address_list]
            )
            
            # 한진 API 호출
            api_response = await self.generate_print_wbls_with_env_vars_from_api(print_request)
            
            # 응답 데이터로 레코드 업데이트
            updated_records = []
            if api_response.address_list:
                for i, address_result in enumerate(api_response.address_list):
                    if i < len(records):
                        record = records[i]
                        # API 응답 데이터를 딕셔너리로 변환
                        response_data = address_result.model_dump()
                        # 레코드 업데이트
                        updated_record = await printwbls_repo.update_with_api_response(record.id, response_data)
                        updated_records.append(updated_record)
            
            logger.info(f"hanjin_printwbls {len(updated_records)}건 API 처리 및 업데이트 완료")
            
            return ProcessPrintwblsWithApiResponse(
                message=f"성공적으로 {len(updated_records)}건의 레코드를 API 처리하고 업데이트했습니다.",
                processed_count=len(updated_records),
                api_response={
                    "total_cnt": api_response.total_cnt,
                    "error_cnt": api_response.error_cnt
                },
                updated_records=[
                    {
                        "id": record.id,
                        "idx": record.idx,
                        "msg_key": record.msg_key,
                        "result_code": record.result_code,
                        "wbl_num": record.wbl_num
                    }
                    for record in updated_records
                ]
            )
            
        except Exception as e:
            logger.error(f"hanjin_printwbls API 처리 실패: {str(e)}")
            raise
