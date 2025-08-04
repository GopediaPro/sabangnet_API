from utils.logs.sabangnet_logger import get_logger
from services.hanjin.adapter.hanjin_base_adapter import HanjinBaseAdapter


logger = get_logger(__name__)


class HanjinAuthAdapter(HanjinBaseAdapter):
    """한진 API 인증 어댑터"""
    
    def __init__(self):
        super().__init__()
        self.api_base_url = "https://api-stg.hanjin.com"
        self.hmac_endpoint = "/v1/util/hmacgen"
    
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