from typing import Optional

from core.settings import SETTINGS
from utils.logs.sabangnet_logger import get_logger
from schemas.hanjin.hanjin_printWbls_dto import AddressItem


logger = get_logger(__name__)


class HanjinBaseAdapter:
    """한진 API 어댑터"""
    
    def __init__(self):
        self.x_api_key = SETTINGS.HANJIN_API
        self.hanjin_csr_num = SETTINGS.HANJIN_CSR_NUM
        self.default_client_id = SETTINGS.HANJIN_CLIENT_ID

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