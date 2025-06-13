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

class SabangNetOrderAPI:
    def __init__(self, company_id: str = None, auth_key: str = None, admin_url: str = None):
        self.company_id = company_id or SABANG_COMPANY_ID
        self.auth_key = auth_key or SABANG_AUTH_KEY
        self.admin_url = admin_url or SABANG_ADMIN_URL
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")

    def create_request_xml(self, send_date: str = None, ord_st_date: str = None, ord_ed_date: str = None, order_status: str = None) -> str:
        if not send_date:
            send_date = datetime.now().strftime('%Y%m%d')
        xml_content = f"""
<?xml version="1.0" encoding="EUC-KR"?>
<SABANG_ORDER_LIST>
    <HEADER>
        <SEND_COMPAYNY_ID>{self.company_id}</SEND_COMPAYNY_ID>
        <SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>
        <SEND_DATE>{send_date}</SEND_DATE>
    </HEADER>
    <DATA>
		<ORD_ST_DATE>{ord_st_date}</ORD_ST_DATE>
		<ORD_ED_DATE>{ord_ed_date}</ORD_ED_DATE>
		<ORD_FIELD><![CDATA[IDX|ORDER_ID|MALL_ID|MALL_USER_ID|MALL_USER_ID2|ORDER_STATUS|USER_ID|USER_NAME|USER_TEL|USER_CEL|USER_EMAIL|RECEIVE_TEL|RECEIVE_CEL|RECEIVE_EMAIL|DELV_MSG|RECEIVE_NAME|RECEIVE_ZIPCODE|RECEIVE_ADDR|TOTAL_COST|PAY_COST|ORDER_DATE|PARTNER_ID|DPARTNER_ID|MALL_PRODUCT_ID|PRODUCT_ID|SKU_ID|P_PRODUCT_NAME|P_SKU_VALUE|PRODUCT_NAME|SALE_COST|MALL_WON_COST|WON_COST|SKU_VALUE|SALE_CNT|DELIVERY_METHOD_STR|DELV_COST|COMPAYNY_GOODS_CD|SKU_ALIAS|BOX_EA|JUNG_CHK_YN|MALL_ORDER_SEQ|MALL_ORDER_ID|ETC_FIELD3|ORDER_GUBUN|P_EA|REG_DATE|ORDER_ETC_1|ORDER_ETC_2|ORDER_ETC_3|ORDER_ETC_4|ORDER_ETC_5|ORDER_ETC_6|ORDER_ETC_7|ORDER_ETC_8|ORDER_ETC_9|ORDER_ETC_10|ORDER_ETC_11|ORDER_ETC_12|ORDER_ETC_13|ORDER_ETC_14|ord_field2|copy_idx|GOODS_NM_PR|GOODS_KEYWORD|ORD_CONFIRM_DATE|RTN_DT|CHNG_DT|DELIVERY_CONFIRM_DATE|CANCEL_DT|CLASS_CD1|CLASS_CD2|CLASS_CD3|CLASS_CD4|BRAND_NM|DELIVERY_ID|INVOICE_NO|HOPE_DELV_DATE|FLD_DSP|INV_SEND_MSG|MODEL_NO|SET_GUBUN|ETC_MSG|DELV_MSG1|MUL_DELV_MSG|BARCODE|INV_SEND_DM|DELIVERY_METHOD_STR2|FREE_GIFT|ACNT_REGS_SRNO|MODEL_NAME]]></ORD_FIELD>
		<ORDER_STATUS>{order_status}</ORDER_STATUS>
	</DATA>
</SABANG_ORDER_LIST>"""
        return xml_content

    # def parse_response_xml(self, xml_content: str) -> List[Dict[str, str]]:
    #     try:
    #         root = ET.fromstring(xml_content)
    #         mall_list = []
    #         for data_node in root.findall('DATA'):
    #             mall_id_node = data_node.find('MALL_ID')
    #             mall_name_node = data_node.find('MALL_NAME')
    #             if mall_id_node is not None and mall_name_node is not None:
    #                 mall_info = {
    #                     'mall_id': mall_id_node.text.strip() if mall_id_node.text else '',
    #                     'mall_name': mall_name_node.text.strip() if mall_name_node.text else ''
    #                 }
    #                 mall_list.append(mall_info)
    #         logger.info(f"총 {len(mall_list)}개의 쇼핑몰 정보를 파싱했습니다.")
    #         return mall_list
    #     except ET.ParseError as e:
    #         logger.error(f"XML 파싱 오류: {e}")
    #         raise
    #     except Exception as e:
    #         logger.error(f"응답 파싱 중 오류: {e}")
    #         raise

    # def get_mall_list_via_url(self, xml_url: str) -> List[Dict[str, str]]:
    #     try:
    #         api_url = urljoin(self.admin_url, '/RTL_API/xml_mall_info.html')
    #         full_url = f"{api_url}?xml_url={xml_url}"
    #         logger.info(f"최종 요청 URL: {full_url}")
    #         print(f"최종 요청 URL: {full_url}")
    #         response = requests.get(full_url, timeout=30)
    #         print(f"API 요청 결과: {response.text}")
    #         response.raise_for_status()
    #         response_xml = self.parse_response_xml(response.text)
    #         return response_xml
    #     except requests.RequestException as e:
    #         logger.error(f"API 요청 실패: {e}")
    #         raise
    #     except Exception as e:
    #         logger.error(f"예상치 못한 오류: {e}")
    #         raise

    # def display_mall_list(self, mall_list: List[Dict[str, str]]):
    #     if not mall_list:
    #         print("조회된 쇼핑몰이 없습니다.")
    #         return
    #     print(f"\n{'='*50}")
    #     print(f"{'쇼핑몰 목록':^20}")
    #     print(f"{'='*50}")
    #     print(f"{'몰 ID':<15} {'몰 이름'}")
    #     print(f"{'-'*50}")
    #     for mall in mall_list:
    #         print(f"{mall['mall_id']:<15} {mall['mall_name']}")
    #     print(f"{'-'*50}")
    #     print(f"총 {len(mall_list)}개 쇼핑몰") 