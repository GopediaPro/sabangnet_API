import io
import urllib.parse
import pandas as pd
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from utils.sabangnet_logger import get_logger
from fastapi.responses import StreamingResponse
from utils.make_xml.sabangnet_xml import SabangnetXml
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.make_xml.file_name_for_xml import sanitize_filename


logger = get_logger(__name__)


class OrderCreateXml(SabangnetXml):
    """
    주문수집용 XML 템플릿 렌더링 클래스
    """

    _PATH: Path = SabangNetPathUtils.get_xml_request_path() / "order"
    _ORD_FIELD = """IDX|ORDER_ID|MALL_ID|MALL_USER_ID|MALL_USER_ID2|ORDER_STATUS|USER_ID|USER_NAME|USER_TEL|USER_CEL|USER_EMAIL|RECEIVE_TEL|RECEIVE_CEL|RECEIVE_EMAIL|DELV_MSG|RECEIVE_NAME|RECEIVE_ZIPCODE|RECEIVE_ADDR|TOTAL_COST|PAY_COST|ORDER_DATE|PARTNER_ID|DPARTNER_ID|MALL_PRODUCT_ID|PRODUCT_ID|SKU_ID|P_PRODUCT_NAME|P_SKU_VALUE|PRODUCT_NAME|SALE_COST|MALL_WON_COST|WON_COST|SKU_VALUE|SALE_CNT|DELIVERY_METHOD_STR|DELV_COST|COMPAYNY_GOODS_CD|SKU_ALIAS|BOX_EA|JUNG_CHK_YN|MALL_ORDER_SEQ|MALL_ORDER_ID|ETC_FIELD3|ORDER_GUBUN|P_EA|REG_DATE|ORDER_ETC_1|ORDER_ETC_2|ORDER_ETC_3|ORDER_ETC_4|ORDER_ETC_5|ORDER_ETC_6|ORDER_ETC_7|ORDER_ETC_8|ORDER_ETC_9|ORDER_ETC_10|ORDER_ETC_11|ORDER_ETC_12|ORDER_ETC_13|ORDER_ETC_14|ord_field2|copy_idx|GOODS_NM_PR|GOODS_KEYWORD|ORD_CONFIRM_DATE|RTN_DT|CHNG_DT|DELIVERY_CONFIRM_DATE|CANCEL_DT|CLASS_CD1|CLASS_CD2|CLASS_CD3|CLASS_CD4|BRAND_NM|DELIVERY_ID|INVOICE_NO|HOPE_DELV_DATE|FLD_DSP|INV_SEND_MSG|MODEL_NO|SET_GUBUN|ETC_MSG|DELV_MSG1|MUL_DELV_MSG|BARCODE|INV_SEND_DM|DELIVERY_METHOD_STR2|FREE_GIFT|ACNT_REGS_SRNO|MODEL_NAME"""

    def __init__(self, ord_st_date: str, ord_ed_date: str, order_status: str):
        self.ord_st_date = ord_st_date
        self.ord_ed_date = ord_ed_date
        self.order_status = order_status

    def _create_body(self, root: ET.Element) -> None:
        # 1. root에 대해 DATA subelement 생성
        data_element: ET.Element = ET.SubElement(root, "DATA")
        ord_st_date_element = ET.SubElement(data_element, "ORD_ST_DATE")
        ord_st_date_element.text = self.ord_st_date
        ord_ed_date_element = ET.SubElement(data_element, "ORD_ED_DATE")
        ord_ed_date_element.text = self.ord_ed_date
        ord_field_element = ET.SubElement(data_element, "ORD_FIELD")
        ord_field_element.text = self._ORD_FIELD
        order_status_element = ET.SubElement(data_element, "ORDER_STATUS")
        order_status_element.text = self.order_status

    def make_order_create_xml(self) -> ET.ElementTree:
        """
        주문 수집용 XML 파일 생성
        """

        # XML 루트 엘리먼트 생성
        root = ET.Element("SABANG_ORDER_LIST")
        
        # 헤더 생성
        self._create_order_header(root=root)
        
        # body 생성
        self._create_body(root=root)
        
        # XML 생성
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        return tree
    
    def save_order_create_xml_to_local(self, tree: ET.ElementTree, dst_path_name: str = None) -> Path:

        # 파일명 생성
        if not dst_path_name:
            now_str = datetime.now().strftime("%m%d%H%M")
            file_name = f"order_create_request_{now_str}.xml"
            dst_path_name = f"{self._PATH}/" + sanitize_filename(file_name)
        else:
            dst_path_name = f"{self._PATH}/" + sanitize_filename(dst_path_name)

        # 파일 경로 객체 생성
        file_path = Path(dst_path_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
            tree.write(f, encoding='EUC-KR', xml_declaration=False)

        return file_path
    
    def save_order_create_xml_to_stream(self, tree: ET.ElementTree, file_name: str = None) -> StreamingResponse:
        """
        주문 수집용 XML을 스트림으로 반환
        """
        stream = io.BytesIO()
        stream.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
        tree.write(stream, encoding='EUC-KR', xml_declaration=False)
        stream.seek(0)

        if not file_name:
            now_str = datetime.now().strftime("%m%d%H%M")
            file_name = f"order_create_request_{now_str}.xml"
        
        return StreamingResponse(
            io.BytesIO(stream.read()),
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename={file_name}",
                "Content-Type": "application/xml; charset=euc-kr"
            }
        )