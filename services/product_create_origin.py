import logging
import requests
from datetime import datetime
from urllib.parse import urljoin
from core.settings import SETTINGS
from utils.product_not_null_fields import PRODUCT_NOT_NULL_FIELDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductCreateService:

    def __init__(self, company_id: str = None, auth_key: str = None, admin_url: str = None):
        self.company_id = company_id or SETTINGS.SABANG_COMPANY_ID
        self.auth_key = auth_key or SETTINGS.SABANG_AUTH_KEY
        self.admin_url = admin_url or SETTINGS.SABANG_ADMIN_URL
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")

    # 필수 값 검증
    def validate_required_fields(self, product_data: dict) -> None:
        for key in PRODUCT_NOT_NULL_FIELDS:
            if not product_data.get(key):
                raise Exception(f"{key}는 필수 입력 항목입니다.")
    
    def dict_to_xml(self, json_data: dict) -> str:
        product_xml = ""
        for key, value in json_data.items():
            product_xml += f"<{key.upper()}><![CDATA[{value if value else ''}]]></{key.upper()}>\n"
        return product_xml

    # 상품 등록 요청 XML 생성
    def create_request_xml(
            self, send_date: str = None,
            product_data: dict = {},
            send_goods_cd_rt: str = None,
            result_type: str = None
    ) -> str:
        if not send_date:
            send_date = datetime.now().strftime('%Y%m%d')
        # 기본값 HTML 설정, XML 결과 타입 변경 가능.
        if not result_type:
            result_type = 'HTML'
        # 필수 값 검증
        self.validate_required_fields(product_data)

        # dict to xml
        product_xml = self.dict_to_xml(product_data)

        # 실제 테스트시 [사방넷]API 가이드&명세서 -> 상품등록&수정 -> Requst 사용.
        xml_content = f"""<?xml version="1.0" encoding="EUC-KR"?>\n<SABANG_GOODS_REGI>\n<HEADER>\n<SEND_COMPAYNY_ID>{self.company_id}</SEND_COMPAYNY_ID>\n<SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>\n<SEND_DATA>{send_date}</SEND_DATA>\n<SEND_GOODS_CD_RT>{send_goods_cd_rt}</SEND_GOODS_CD_RT>\n<RESULT_TYPE>{result_type}</RESULT_TYPE>\n</HEADER>\n<DATA>\n{product_xml}\n</DATA>\n
        </SABANG_GOODS_REGI>"""
        return xml_content
    
    