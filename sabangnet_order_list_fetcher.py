import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin
import logging
import json
from pathlib import Path

SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')
SABANG_SEND_DATE = os.getenv('SABANG_SEND_DATE', None)
SABANG_ORD_ST_DATE = os.getenv('SABANG_ORD_ST_DATE', None)
SABANG_ORD_ED_DATE = os.getenv('SABANG_ORD_ED_DATE', None)
SABANG_ORDER_STATUS = os.getenv('SABANG_ORDER_STATUS', None)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SabangNetOrderListFetcher:
    def __init__(
            self,
            ord_st_date: str = None,
            ord_ed_date: str = None,
            order_status: str = None,
            send_date: str = None,
            company_id: str = None,
            auth_key: str = None,
            admin_url: str = None
            ):
        self.ord_st_date = ord_st_date or SABANG_ORD_ST_DATE
        self.ord_ed_date = ord_ed_date or SABANG_ORD_ED_DATE
        self.order_status = order_status or SABANG_ORDER_STATUS
        self.send_date = send_date or SABANG_SEND_DATE
        self.company_id = company_id or SABANG_COMPANY_ID
        self.auth_key = auth_key or SABANG_AUTH_KEY
        self.admin_url = admin_url or SABANG_ADMIN_URL
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")

    def create_request_xml(self) -> str:
        if not self.send_date:
            self.send_date = datetime.now().strftime('%Y%m%d')
        xml_content = f"""\
<?xml version="1.0" encoding="EUC-KR"?>
<SABANG_ORDER_LIST>
    <HEADER>
        <SEND_COMPAYNY_ID>{self.company_id}</SEND_COMPAYNY_ID>
        <SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>
        <SEND_DATE>{self.send_date}</SEND_DATE>
    </HEADER>
    <DATA>
		<ORD_ST_DATE>{self.ord_st_date}</ORD_ST_DATE>
		<ORD_ED_DATE>{self.ord_ed_date}</ORD_ED_DATE>
		<ORD_FIELD><![CDATA[IDX|ORDER_ID|MALL_ID|MALL_USER_ID|MALL_USER_ID2|ORDER_STATUS|USER_ID|USER_NAME|USER_TEL|USER_CEL|USER_EMAIL|RECEIVE_TEL|RECEIVE_CEL|RECEIVE_EMAIL|DELV_MSG|RECEIVE_NAME|RECEIVE_ZIPCODE|RECEIVE_ADDR|TOTAL_COST|PAY_COST|ORDER_DATE|PARTNER_ID|DPARTNER_ID|MALL_PRODUCT_ID|PRODUCT_ID|SKU_ID|P_PRODUCT_NAME|P_SKU_VALUE|PRODUCT_NAME|SALE_COST|MALL_WON_COST|WON_COST|SKU_VALUE|SALE_CNT|DELIVERY_METHOD_STR|DELV_COST|COMPAYNY_GOODS_CD|SKU_ALIAS|BOX_EA|JUNG_CHK_YN|MALL_ORDER_SEQ|MALL_ORDER_ID|ETC_FIELD3|ORDER_GUBUN|P_EA|REG_DATE|ORDER_ETC_1|ORDER_ETC_2|ORDER_ETC_3|ORDER_ETC_4|ORDER_ETC_5|ORDER_ETC_6|ORDER_ETC_7|ORDER_ETC_8|ORDER_ETC_9|ORDER_ETC_10|ORDER_ETC_11|ORDER_ETC_12|ORDER_ETC_13|ORDER_ETC_14|ord_field2|copy_idx|GOODS_NM_PR|GOODS_KEYWORD|ORD_CONFIRM_DATE|RTN_DT|CHNG_DT|DELIVERY_CONFIRM_DATE|CANCEL_DT|CLASS_CD1|CLASS_CD2|CLASS_CD3|CLASS_CD4|BRAND_NM|DELIVERY_ID|INVOICE_NO|HOPE_DELV_DATE|FLD_DSP|INV_SEND_MSG|MODEL_NO|SET_GUBUN|ETC_MSG|DELV_MSG1|MUL_DELV_MSG|BARCODE|INV_SEND_DM|DELIVERY_METHOD_STR2|FREE_GIFT|ACNT_REGS_SRNO|MODEL_NAME]]></ORD_FIELD>
		<ORDER_STATUS>{self.order_status}</ORDER_STATUS>
	</DATA>
</SABANG_ORDER_LIST>"""
        return xml_content

    def parse_response_xml(self, xml_content: str) -> List[Dict[str, str]]:
        try:
            root = ET.fromstring(xml_content)
            order_list = []
            for data_node in root.findall('DATA'):
                order_dict = {}
                order_detail = {}
                mall_id_node = data_node.find('MALL_ID')
                for elem in data_node.findall('*'):
                    elem_tag = elem.tag.strip() if elem.tag else ''
                    elem_text = elem.text.strip() if elem.text else ''
                    if elem.tag is not None and elem.text is not None:
                        # 개별 주문 정보 추출
                        order_detail[elem_tag] = elem_text
                order_dict[mall_id_node.text.strip()] = order_detail
                order_list.append(order_dict)
            logger.info(f"총 {len(order_list)}개의 주문을 수집했습니다.")
            json_dir = Path("./files/json")
            json_dir.mkdir(exist_ok=True)
            json_path = json_dir / "order_list.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(order_list, f, ensure_ascii=False, indent=4)
            return order_list
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise

    def get_order_list_via_url(self, xml_url: str) -> List[Dict[str, str]]:
        try:
            api_url = urljoin(self.admin_url, '/RTL_API/xml_order_info.html')
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")
            print(f"최종 요청 URL: {full_url}")
            response = requests.get(full_url, timeout=30)
            print(f"API 요청 결과: {response.text}")
            response.raise_for_status()
            response_xml = self.parse_response_xml(response.text)
            return response_xml
        except requests.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise