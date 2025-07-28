"""
한진 API 인증 서비스
"""
from typing import Optional
import aiohttp
from utils.logs.sabangnet_logger import get_logger
from schemas.hanjin.hanjin_auth_schemas import HmacResponse
from core.settings import SETTINGS


logger = get_logger(__name__)


class HanjinAuthService:
    """한진 API 인증 서비스"""
    
    def __init__(self):
        self.api_base_url = "https://api-stg.hanjin.com"
        self.hmac_endpoint = "/v1/util/hmacgen"
        # 환경변수에서 한진 API 설정 가져오기
        self.x_api_key = SETTINGS.HANJIN_API
        self.default_client_id = SETTINGS.HANJIN_CLIENT_ID


    def get_x_api_key(self) -> Optional[str]:
        """
        환경변수에서 x-api-key를 가져옵니다.
        """
        return self.x_api_key
    
    def get_default_client_id(self) -> Optional[str]:
        """
        환경변수에서 기본 client_id를 가져옵니다.
        
        Returns:
            client_id 값 또는 None
        """
        return self.default_client_id
    
    def validate_env_vars(self) -> bool:
        """
        환경변수가 올바르게 설정되었는지 검증합니다.
        
        Returns:
            유효성 여부
        """
        if not self.x_api_key:
            logger.error("환경변수 HANJIN_API가 설정되지 않았습니다.")
            return False
        
        if not self.default_client_id:
            logger.error("환경변수 HANJIN_CLIENT_ID가 설정되지 않았습니다.")
            return False
    
        
        logger.info("환경변수 검증 성공")
        return True
    
    async def request_hmac_from_hanjin_api(self, client_id: str, x_api_key: str) -> HmacResponse:
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
                "x-api-key": x_api_key,
                "Content-Type": "application/json",
                "client_id": client_id
            }

            logger.info(f"한진 API 요청: {url}, client_id={client_id}")
            
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
