from datetime import datetime
from core.settings import SETTINGS
import xml.etree.ElementTree as ET


class SabangnetXml:
    
    _COMPAYNY_ID = SETTINGS.SABANG_COMPANY_ID
    _AUTH_KEY = SETTINGS.SABANG_AUTH_KEY
    _SEND_GOODS_CD_RT = SETTINGS.SABANG_SEND_GOODS_CD_RT

    
    def _create_product_header(self, root: ET.Element) -> ET.Element:
        
        header = ET.SubElement(root, "HEADER")
        
        send_company_id = ET.SubElement(header, "SEND_COMPAYNY_ID")
        send_company_id.text = self._COMPAYNY_ID
        
        send_auth_key = ET.SubElement(header, "SEND_AUTH_KEY")
        send_auth_key.text = self._AUTH_KEY
        
        send_date = ET.SubElement(header, "SEND_DATA")
        send_date.text = datetime.now().strftime("%Y%m%d")
        
        send_goods_cd_rt = ET.SubElement(header, "SEND_GOODS_CD_RT")
        send_goods_cd_rt.text = self._SEND_GOODS_CD_RT if self._SEND_GOODS_CD_RT else "Y"
        
        result_type = ET.SubElement(header, "RESULT_TYPE")
        result_type.text = "XML"
    
    def _create_order_header(self, root: ET.Element) -> ET.Element:
        
        header = ET.SubElement(root, "HEADER")
        
        send_company_id = ET.SubElement(header, "SEND_COMPAYNY_ID")
        send_company_id.text = self._COMPAYNY_ID
        
        send_auth_key = ET.SubElement(header, "SEND_AUTH_KEY")
        send_auth_key.text = self._AUTH_KEY
        
        send_date = ET.SubElement(header, "SEND_DATE")
        send_date.text = datetime.now().strftime("%Y%m%d")
