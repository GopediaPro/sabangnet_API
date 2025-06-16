from lxml import etree as ET 
import pandas as pd
import os
from datetime import datetime


SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')

class XlsxToXml:
    def __init__(self, company_id: str = None, auth_key: str = None, admin_url: str = None):
        self.company_id = company_id or SABANG_COMPANY_ID
        self.auth_key = auth_key or SABANG_AUTH_KEY
        self.admin_url = admin_url or SABANG_ADMIN_URL
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")

    def xlsx_to_xml(self, xml_path: str) -> str:
        # 1. 엑셀 파일 읽기
        df_xlsx:pd.DataFrame = pd.read_excel(xml_path).fillna("")
        # 2. 엑셀 파일을 XML 문자열로 변환
        dummy = ET.Element("dummy")
        for _, row in df_xlsx.iterrows():
            data = ET.SubElement(dummy, "DATA")
            for key, value in row.items():
                child = ET.SubElement(data, key)
                child.text = ET.CDATA(str(value))

        xml_str: bytes = ET.tostring(dummy, encoding="euc-kr", pretty_print=True, xml_declaration=False, with_tail=False)
        return"\n".join(xml_str.decode("euc-kr").splitlines()[1:-1])

    def create_request_xml(self, xml_path: str = "", send_date: str = None, send_goods_cd_rt: str = "", result_type: str = "") -> str:
        if not send_date:
            send_date = datetime.now().strftime('%Y%m%d')
        
        if xml_path:
            xml_str = self.xlsx_to_xml(xml_path) 
        else:
            xml_str = ""

        # 3. XML 문자열을 사방넷 형식에 맞게 변환
        xml_content = f"""<?xml version="1.0" encoding="EUC-KR"?>
                            <SABANG_GOODS_REGI>
                                <HEADER>
                                    <SEND_COMPAYNY_ID>{self.company_id}</SEND_COMPAYNY_ID>
                                    <SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>
                                    <SEND_DATA>{send_date}</SEND_DATA>
                                    <SEND_GOODS_CD_RT>{send_goods_cd_rt}</SEND_GOODS_CD_RT>
                                    <RESULT_TYPE>{result_type}</RESULT_TYPE>
                                </HEADER>
                                {xml_str}
                            </SABANG_GOODS_REGI>"""
        return xml_content