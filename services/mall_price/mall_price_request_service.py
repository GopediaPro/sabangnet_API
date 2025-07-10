import requests
from urllib.parse import urljoin
from core.settings import SETTINGS
from utils.sabangnet_logger import get_logger



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
            response = requests.post(
                api_url,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            # response.text 파싱
            return response.text
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise
