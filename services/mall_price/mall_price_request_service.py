import requests
from urllib.parse import urljoin
from core.settings import SETTINGS
from utils.logs.sabangnet_logger import get_logger



logger = get_logger(__name__)


class MallPriceRequestService:

    # 상품 등록 요청
    @staticmethod
    def request_sabangnet_product_update(xml_url: str) -> str:
        try:
            api_url = urljoin(SETTINGS.SABANG_ADMIN_URL, '/RTL_API/xml_goods_info3.html')
            payload = {
                'xml_url': xml_url
            }
            
            logger.info(f"사방넷 API 요청 시작: {api_url}")
            logger.info(f"XML URL: {xml_url}")
            
            response = requests.post(
                api_url,
                data=payload,
                timeout=30
            )
            
            logger.info(f"사방넷 API 응답 상태 코드: {response.status_code}")
            logger.info(f"사방넷 API 응답 내용: {response.text[:500]}...")  # 처음 500자만 로그
            
            if response.status_code != 200:
                logger.error(f"사방넷 API 오류 - 상태 코드: {response.status_code}")
                logger.error(f"사방넷 API 오류 - 응답 내용: {response.text}")
                raise Exception(f"사방넷 API 오류 ({response.status_code}): {response.text}")
            
            # response.text 파싱
            return response.text
        except Exception as e:
            logger.error(f"사방넷 API 요청 중 오류: {e}")
            raise
