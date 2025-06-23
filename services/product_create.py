import os
import requests
from datetime import datetime
from urllib.parse import urljoin
import logging
from core.settings import SETTINGS
from utils.sabangnet_path_utils import SabangNetPathUtils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductCreateService:

    def __init__(self):
        self.xml_base_path = SabangNetPathUtils.get_xml_file_path()
        self.xml_file_path = self.xml_base_path / "product_create_request.xml"

    def read_xml_content(self) -> str:
        with open(self.xml_file_path, "r", encoding="euc-kr") as f:
            xml_content = f.read()
        return xml_content

    # 상품 등록 요청
    def create_product_via_url(self, xml_url: str) -> str:
        try:
            api_url = urljoin(SETTINGS.SABANG_ADMIN_URL,
                              '/RTL_API/xml_goods_info.html')
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")
            print(f"최종 요청 URL: {full_url}")
            # Form-data 형식으로 전송
            # payload = {
            #     'xml_url': xml_url
            # }
            # response = requests.post(
            #     api_url,
            #     data=payload,
            #     timeout=30
            # )
            response = requests.get(full_url, timeout=30)
            response.raise_for_status()
            # 요청 결과를 확인 후 변경 필요
            return response.text
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise
