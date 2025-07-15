import requests
from urllib.parse import urljoin
from core.settings import SETTINGS
from pathlib import Path
from utils.sabangnet_logger import get_logger
from utils.make_xml.product_create_xml import ProductCreateXml


logger = get_logger(__name__)


class ProductCreateService:

    # CLI 상품 등록 요청
    @staticmethod
    def request_product_create_via_url(xml_url: str) -> str:
        try:
            api_url = urljoin(SETTINGS.SABANG_ADMIN_URL, '/RTL_API/xml_goods_info.html')
            payload = {
                'xml_url': xml_url
            }
            response = requests.post(
                api_url,
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            # 요청 결과를 확인 후 변경 필요
            return response.text
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise

    @staticmethod
    def excel_to_xml_file(file_name: str, sheet_name: str, dst_path_name: str = None) -> Path:
        return ProductCreateXml(file_name, sheet_name).make_product_create_xml(dst_path_name=dst_path_name)