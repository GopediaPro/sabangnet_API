"""
한진 API 인증 서비스
"""
import aiohttp
from utils.logs.sabangnet_logger import get_logger
from schemas.hanjin.hanjin_auth_schemas import HmacResponse
from services.hanjin.adapter.hanjin_auth_adapter import HanjinAuthAdapter


logger = get_logger(__name__)


class HanjinAuthService(HanjinAuthAdapter):
    """한진 API 인증 서비스"""
    
    def __init__(self):
        super().__init__()
    
    async def request_hmac_from_hanjin_api(self, request_client_id: str, request_x_api_key: str) -> HmacResponse:
        """
        한진 API의 /v1/util/hmacgen 엔드포인트에 직접 요청하여 Authorization을 받아옵니다.
        
        Args:
            client_id: 고객사 코드
            x_api_key: API 키
            
        Returns:
            한진 API에서 받은 HMAC 응답 데이터
        """
        try:
            url = f"{self.api_base_url}{self.hmac_endpoint}"
            headers = {
                "x-api-key": request_x_api_key,
                "Content-Type": "application/json",
                "client_id": request_client_id
            }

            logger.info(f"한진 API 요청: {url}, client_id={request_client_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        logger.info(f"한진 API 응답 성공: {response_data}")
                        return HmacResponse(**response_data)
                    else:
                        error_text = await response.text()
                        logger.error(f"한진 API 요청 실패: {response.status}, {error_text}")
                        raise ValueError(f"한진 API 요청 실패: {response.status} - {error_text}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"한진 API 네트워크 오류: {str(e)}")
            raise ValueError(f"네트워크 오류: {str(e)}")
        except Exception as e:
            logger.error(f"한진 API 요청 중 예외 발생: {str(e)}")
            raise
    
    async def generate_hmac_with_env_vars_from_api(self) -> HmacResponse:
        """
        환경변수에서 x-api-key와 client_id를 가져와서 한진 API에 직접 요청합니다.
        
        Returns:
            한진 API에서 받은 HMAC 응답 데이터
        """
        try:
            # 환경변수 검증
            if not self.x_api_key:
                raise ValueError("환경변수 HANJIN_API가 설정되지 않았습니다.")
            
            if not self.default_client_id:
                raise ValueError("환경변수 HANJIN_CLIENT_ID가 설정되지 않았습니다.")
            
            # 한진 API에 직접 요청
            response = await self.request_hmac_from_hanjin_api(
                self.default_client_id,
                self.x_api_key
            )
            
            logger.info(f"환경변수로 한진 API HMAC 인증 생성 완료: client_id={self.default_client_id}")
            return response
            
        except Exception as e:
            logger.error(f"환경변수 한진 API HMAC 인증 생성 실패: {str(e)}")
            raise
