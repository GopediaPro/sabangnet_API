import requests
from urllib.parse import urljoin
from core.settings import SETTINGS
from pathlib import Path
from utils.logs.sabangnet_logger import get_logger
from utils.make_xml.product_create_xml import ProductCreateXml


logger = get_logger(__name__)


class ProductCreateService:

    @staticmethod
    def request_product_create_via_url(xml_url: str) -> str:
        try:
            api_url = urljoin(SETTINGS.SABANG_ADMIN_URL, '/RTL_API/xml_goods_info.html')
            # post 방식은 됐다 안됐다 함.
            # payload = {
            #     'xml_url': xml_url
            # }
            # response = requests.post(
            #     api_url,
            #     data=payload,
            #     timeout=30
            # )
            # response.raise_for_status()
            # return response.text
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")
            response = requests.get(full_url, timeout=30)
            response_text = str(response.text)
            if len(response_text) > 1000:
                response_text = response_text[:1000] + "..."
            logger.info(f"API 요청 결과: {response_text}")
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise

    @staticmethod
    def excel_to_xml_file(file_name: str, sheet_name: str, dst_path_name: str = None) -> Path:
        return ProductCreateXml(file_name, sheet_name).make_product_create_xml(dst_path_name=dst_path_name)