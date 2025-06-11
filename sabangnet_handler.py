import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin
import logging

SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SabangNetMallAPI:
    def __init__(self, company_id: str = None, auth_key: str = None, admin_url: str = None):
        self.company_id = company_id or SABANG_COMPANY_ID
        self.auth_key = auth_key or SABANG_AUTH_KEY
        self.admin_url = admin_url or SABANG_ADMIN_URL
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")

    def create_request_xml(self, send_date: str = None) -> str:
        if not send_date:
            send_date = datetime.now().strftime('%Y%m%d')
        xml_content = f"""<?xml version=\"1.0\" encoding=\"EUC-KR\"?>\n<SABANG_MALL_LIST>\n    <HEADER>\n        <SEND_COMPANY_ID>{self.company_id}</SEND_COMPANY_ID>\n        <SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>\n        <SEND_DATE>{send_date}</SEND_DATE>\n    </HEADER>\n</SABANG_MALL_LIST>"""
        return xml_content

    def parse_response_xml(self, xml_content: str) -> List[Dict[str, str]]:
        try:
            root = ET.fromstring(xml_content.encode('euc-kr'))
            mall_list = []
            for data_node in root.findall('DATA'):
                mall_id_node = data_node.find('MALL_ID')
                mall_name_node = data_node.find('MALL_NAME')
                if mall_id_node is not None and mall_name_node is not None:
                    mall_info = {
                        'mall_id': mall_id_node.text.strip() if mall_id_node.text else '',
                        'mall_name': mall_name_node.text.strip() if mall_name_node.text else ''
                    }
                    mall_list.append(mall_info)
            logger.info(f"총 {len(mall_list)}개의 쇼핑몰 정보를 파싱했습니다.")
            return mall_list
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise

    def get_mall_list_via_url(self, xml_url: str) -> List[Dict[str, str]]:
        try:
            api_url = urljoin(self.admin_url, '/RTL_API/xml_mall_info.html')
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")
            print(f"최종 요청 URL: {full_url}")
            response = requests.get(full_url, timeout=30)
            print(f"API 요청 결과: {response.text}")
            response.raise_for_status()
            return self.parse_response_xml(response.text)
        except requests.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise

    def display_mall_list(self, mall_list: List[Dict[str, str]]):
        if not mall_list:
            print("조회된 쇼핑몰이 없습니다.")
            return
        print(f"\n{'='*50}")
        print(f"{'쇼핑몰 목록':^20}")
        print(f"{'='*50}")
        print(f"{'몰 ID':<15} {'몰 이름'}")
        print(f"{'-'*50}")
        for mall in mall_list:
            print(f"{mall['mall_id']:<15} {mall['mall_name']}")
        print(f"{'-'*50}")
        print(f"총 {len(mall_list)}개 쇼핑몰") 