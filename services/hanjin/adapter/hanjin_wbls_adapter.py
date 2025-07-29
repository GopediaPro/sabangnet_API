import aiohttp
from utils.logs.sabangnet_logger import get_logger
from services.hanjin.adapter.hanjin_base_adapter import HanjinBaseAdapter
from schemas.hanjin.hanjin_printWbls_dto import AddressItem, PrintWblsRequest, PrintWblsResponse


logger = get_logger(__name__)


class HanjinWblsAdapter(HanjinBaseAdapter):
    """한진 API 어댑터"""
    
    def __init__(self):
        super().__init__()
        self.api_base_url = "https://ebbapd.hjt.co.kr"
        self.print_wbls_endpoint = "/v1/wbl/{client_id}/print-wbls"

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
    
    def validate_address_list(self, address_list: list[AddressItem]) -> bool:
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