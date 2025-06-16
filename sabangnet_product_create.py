import os
import requests
from datetime import datetime
from urllib.parse import urljoin
import logging

SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SabangNetProductAPI:
    def __init__(self, company_id: str = None, auth_key: str = None, admin_url: str = None):
        self.company_id = company_id or SABANG_COMPANY_ID
        self.auth_key = auth_key or SABANG_AUTH_KEY
        self.admin_url = admin_url or SABANG_ADMIN_URL
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")
    
    # 필수 값 검증
    def validate_required_fields(self, product_data: dict) -> None:
        required_fields = ['goods_nm', 'compayny_goods_cd', 'goods_gubun', 'class_cd1', 'class_cd2', 'class_cd3', 'goods_season', 'sex', 'status', 'tax_yn', 'delv_type', 'goods_cost', 'goods_price', 'goods_consumer_price', 'img_path', 'img_path1', 'img_path2', 'img_path3', 'img_path4', 'img_path5', 'img_path6', 'img_path7', 'img_path8', 'img_path9', 'img_path10', 'img_path11', 'img_path12', 'img_path13', 'img_path14', 'img_path15', 'img_path16', 'img_path17', 'img_path18', 'img_path19', 'img_path20', 'img_path21', 'img_path22', 'img_path23', 'img_path24']
        for key in required_fields:
            if not product_data.get(key):
                raise Exception(f"{key}는 필수 입력 항목입니다.")

    # 상품 등록 요청 XML 생성
    def create_request_xml(self, send_date: str = None, product_data: dict = {},
                           send_goods_cd_rt: str = None, result_type: str = None
                           ) -> str:
        if not send_date:
            send_date = datetime.now().strftime('%Y%m%d')
        # 기본값 HTML 설정, XML 결과 타입 변경 가능.
        if not result_type: 
            result_type = 'HTML'
        # 필수 값 검증
        self.validate_required_fields(product_data)
        
        # 실제 테스트시 [사방넷]API 가이드&명세서 -> 상품등록&수정 -> Requst 사용. 
        xml_content = f"""<?xml version="1.0" encoding="EUC-KR"?>
<SABANG_GOODS_REGI>
    <HEADER>
        <SEND_COMPAYNY_ID>{self.company_id}</SEND_COMPAYNY_ID>
        <SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>
        <SEND_DATA>{send_date}</SEND_DATA>
        <SEND_GOODS_CD_RT>{send_goods_cd_rt}</SEND_GOODS_CD_RT>
        <RESULT_TYPE>{result_type}</RESULT_TYPE>
    </HEADER>
    <DATA>
		<GOODS_NM><![CDATA[{product_data['goods_nm']}]]></GOODS_NM>
        <GOODS_KEYWORD><![CDATA[{product_data.get('goods_keyword', '')}]]></GOODS_KEYWORD>
        <MODEL_NM><![CDATA[{product_data.get('model_nm', '')}]]></MODEL_NM>
        <MODEL_NO><![CDATA[{product_data.get('model_no', '')}]]></MODEL_NO>
        <BRAND_NM><![CDATA[{product_data.get('brand_nm', '')}]]></BRAND_NM>
        <COMPAYNY_GOODS_CD><![CDATA[{product_data['compayny_goods_cd']}]]></COMPAYNY_GOODS_CD>
        <GOODS_SEARCH><![CDATA[{product_data.get('goods_search', '')}]]></GOODS_SEARCH>
        <GOODS_GUBUN><![CDATA[{product_data['goods_gubun']}]]></GOODS_GUBUN>
        <CLASS_CD1><![CDATA[{product_data['class_cd1']}]]></CLASS_CD1>
        <CLASS_CD2><![CDATA[{product_data['class_cd2']}]]></CLASS_CD2>
        <CLASS_CD3><![CDATA[{product_data['class_cd3']}]]></CLASS_CD3>
        <CLASS_CD4><![CDATA[{product_data.get('class_cd4', '')}]]></CLASS_CD4>
        <PARTNER_ID><![CDATA[{product_data.get('partner_id', '')}]]></PARTNER_ID>
        <DPARTNER_ID><![CDATA[{product_data.get('dpartner_id', '')}]]></DPARTNER_ID>
        <MAKER><![CDATA[{product_data.get('maker', '')}]]></MAKER>
        <ORIGIN><![CDATA[{product_data['origin']}]]></ORIGIN>
        <MAKE_YEAR><![CDATA[{product_data.get('make_year', '')}]]></MAKE_YEAR>
        <MAKE_DM><![CDATA[{product_data.get('make_dm', '')}]]></MAKE_DM>
        <GOODS_SEASON><![CDATA[{product_data['goods_season']}]]></GOODS_SEASON>
        <SEX><![CDATA[{product_data['sex']}]]></SEX>
        <STATUS><![CDATA[{product_data['status']}]]></STATUS>
        <DELIV_ABLE_REGION><![CDATA[{product_data.get('deliv_able_region', '')}]]></DELIV_ABLE_REGION>
        <TAX_YN><![CDATA[{product_data['tax_yn']}]]></TAX_YN>
        <DELV_TYPE><![CDATA[{product_data['delv_type']}]]></DELV_TYPE>
        <DELV_COST><![CDATA[{product_data.get('delv_cost', '')}]]></DELV_COST>
        <BANPUM_AREA><![CDATA[{product_data.get('banpum_area', '')}]]></BANPUM_AREA>
        <GOODS_COST><![CDATA[{product_data['goods_cost']}]]></GOODS_COST>
        <GOODS_PRICE><![CDATA[{product_data['goods_price']}]]></GOODS_PRICE>
        <GOODS_CONSUMER_PRICE><![CDATA[{product_data['goods_consumer_price']}]]></GOODS_CONSUMER_PRICE>
        <CHAR_1_NM><![CDATA[{product_data.get('char_1_nm', '')}]]></CHAR_1_NM>
        <CHAR_1_VAL><![CDATA[{product_data.get('char_1_val', '')}]]></CHAR_1_VAL>
        <CHAR_2_NM><![CDATA[{product_data.get('char_2_nm', '')}]]></CHAR_2_NM>
        <CHAR_2_VAL><![CDATA[{product_data.get('char_2_val', '')}]]></CHAR_2_VAL>
        <IMG_PATH><![CDATA[{product_data['img_path']}]]></IMG_PATH>
        <IMG_PATH1><![CDATA[{product_data['img_path1']}]]></IMG_PATH1>
        <IMG_PATH2><![CDATA[{product_data.get('img_path2', '')}]]></IMG_PATH2>
        <IMG_PATH3><![CDATA[{product_data['img_path3']}]]></IMG_PATH3>
        <IMG_PATH4><![CDATA[{product_data.get('img_path4', '')}]]></IMG_PATH4>
        <IMG_PATH5><![CDATA[{product_data.get('img_path5', '')}]]></IMG_PATH5>
        <IMG_PATH6><![CDATA[{product_data.get('img_path6', '')}]]></IMG_PATH6>
        <IMG_PATH7><![CDATA[{product_data.get('img_path7', '')}]]></IMG_PATH7>
        <IMG_PATH8><![CDATA[{product_data.get('img_path8', '')}]]></IMG_PATH8>
        <IMG_PATH9><![CDATA[{product_data.get('img_path9', '')}]]></IMG_PATH9>
        <IMG_PATH10><![CDATA[{product_data.get('img_path10', '')}]]></IMG_PATH10>
        <IMG_PATH11><![CDATA[{product_data.get('img_path11', '')}]]></IMG_PATH11>
        <IMG_PATH12><![CDATA[{product_data.get('img_path12', '')}]]></IMG_PATH12>
        <IMG_PATH13><![CDATA[{product_data.get('img_path13', '')}]]></IMG_PATH13>
        <IMG_PATH14><![CDATA[{product_data.get('img_path14', '')}]]></IMG_PATH14>
        <IMG_PATH15><![CDATA[{product_data.get('img_path15', '')}]]></IMG_PATH15>
        <IMG_PATH16><![CDATA[{product_data.get('img_path16', '')}]]></IMG_PATH16>
        <IMG_PATH17><![CDATA[{product_data.get('img_path17', '')}]]></IMG_PATH17>
        <IMG_PATH18><![CDATA[{product_data.get('img_path18', '')}]]></IMG_PATH18>
        <IMG_PATH19><![CDATA[{product_data.get('img_path19', '')}]]></IMG_PATH19>
        <IMG_PATH20><![CDATA[{product_data.get('img_path20', '')}]]></IMG_PATH20>
        <IMG_PATH21><![CDATA[{product_data.get('img_path21', '')}]]></IMG_PATH21>
        <IMG_PATH22><![CDATA[{product_data.get('img_path22', '')}]]></IMG_PATH22>
        <IMG_PATH23><![CDATA[{product_data.get('img_path23', '')}]]></IMG_PATH23>
        <IMG_PATH24><![CDATA[{product_data.get('img_path24', '')}]]></IMG_PATH24>
        <GOODS_REMARKS><![CDATA[{product_data.get('goods_remarks', '')}]]></GOODS_REMARKS>
        <CERTNO><![CDATA[{product_data.get('certno', '')}]]></CERTNO>
        <AVLST_DM><![CDATA[{product_data.get('avlst_dm', '')}]]></AVLST_DM>
        <AVLED_DM><![CDATA[{product_data.get('avled_dm', '')}]]></AVLED_DM>
        <ISSUEDATE><![CDATA[{product_data.get('issuedate', '')}]]></ISSUEDATE>
        <CERTDATE><![CDATA[{product_data.get('certdate', '')}]]></CERTDATE>
        <CERT_AGENCY><![CDATA[{product_data.get('cert_agency', '')}]]></CERT_AGENCY>
        <CERTFIELD><![CDATA[{product_data.get('certfield', '')}]]></CERTFIELD>
        <MATERIAL><![CDATA[{product_data.get('material', '')}]]></MATERIAL>
        <STOCK_USE_YN><![CDATA[{product_data.get('stock_use_yn', '')}]]></STOCK_USE_YN>
        <OPT_TYPE><![CDATA[{product_data.get('opt_type', '')}]]></OPT_TYPE>
        <PROP_EDIT_YN><![CDATA[{product_data.get('prop_edit_yn', '')}]]></PROP_EDIT_YN>
        <PROP1_CD><![CDATA[{product_data.get('prop1_cd', '')}]]></PROP1_CD>
        <PROP_VAL1><![CDATA[{product_data.get('prop_val1', '')}]]></PROP_VAL1>
        <PROP_VAL2><![CDATA[{product_data.get('prop_val2', '')}]]></PROP_VAL2>
        <PROP_VAL3><![CDATA[{product_data.get('prop_val3', '')}]]></PROP_VAL3>
        <PROP_VAL4><![CDATA[{product_data.get('prop_val4', '')}]]></PROP_VAL4>
        <PROP_VAL5><![CDATA[{product_data.get('prop_val5', '')}]]></PROP_VAL5>
        <PROP_VAL6><![CDATA[{product_data.get('prop_val6', '')}]]></PROP_VAL6>
        <PROP_VAL7><![CDATA[{product_data.get('prop_val7', '')}]]></PROP_VAL7>
        <PROP_VAL8><![CDATA[{product_data.get('prop_val8', '')}]]></PROP_VAL8>
        <PROP_VAL9><![CDATA[{product_data.get('prop_val9', '')}]]></PROP_VAL9>
        <PROP_VAL10><![CDATA[{product_data.get('prop_val10', '')}]]></PROP_VAL10>
        <PROP_VAL11><![CDATA[{product_data.get('prop_val11', '')}]]></PROP_VAL11>
        <PROP_VAL12><![CDATA[{product_data.get('prop_val12', '')}]]></PROP_VAL12>
        <PROP_VAL13><![CDATA[{product_data.get('prop_val13', '')}]]></PROP_VAL13>
        <PROP_VAL14><![CDATA[{product_data.get('prop_val14', '')}]]></PROP_VAL14>
        <PROP_VAL15><![CDATA[{product_data.get('prop_val15', '')}]]></PROP_VAL15>
        <PROP_VAL16><![CDATA[{product_data.get('prop_val16', '')}]]></PROP_VAL16>
        <PROP_VAL17><![CDATA[{product_data.get('prop_val17', '')}]]></PROP_VAL17>
        <PROP_VAL18><![CDATA[{product_data.get('prop_val18', '')}]]></PROP_VAL18>
        <PROP_VAL19><![CDATA[{product_data.get('prop_val19', '')}]]></PROP_VAL19>
        <PROP_VAL20><![CDATA[{product_data.get('prop_val20', '')}]]></PROP_VAL20>
        <PROP_VAL21><![CDATA[{product_data.get('prop_val21', '')}]]></PROP_VAL21>
        <PROP_VAL22><![CDATA[{product_data.get('prop_val22', '')}]]></PROP_VAL22>
        <PROP_VAL23><![CDATA[{product_data.get('prop_val23', '')}]]></PROP_VAL23>
        <PROP_VAL24><![CDATA[{product_data.get('prop_val24', '')}]]></PROP_VAL24>
        <PROP_VAL25><![CDATA[{product_data.get('prop_val25', '')}]]></PROP_VAL25>
        <PROP_VAL26><![CDATA[{product_data.get('prop_val26', '')}]]></PROP_VAL26>
        <PROP_VAL27><![CDATA[{product_data.get('prop_val27', '')}]]></PROP_VAL27>
        <PROP_VAL28><![CDATA[{product_data.get('prop_val28', '')}]]></PROP_VAL28>
        <PROP_VAL29><![CDATA[{product_data.get('prop_val29', '')}]]></PROP_VAL29>
        <PROP_VAL30><![CDATA[{product_data.get('prop_val30', '')}]]></PROP_VAL30>
        <PROP_VAL31><![CDATA[{product_data.get('prop_val31', '')}]]></PROP_VAL31>
        <PROP_VAL32><![CDATA[{product_data.get('prop_val32', '')}]]></PROP_VAL32>
        <PROP_VAL33><![CDATA[{product_data.get('prop_val33', '')}]]></PROP_VAL33>
        <PACK_CODE_STR><![CDATA[{product_data.get('pack_code_str', '')}]]></PACK_CODE_STR>
        <GOODS_NM_EN><![CDATA[{product_data.get('goods_nm_en', '')}]]></GOODS_NM_EN>
        <GOODS_NM_PR><![CDATA[{product_data.get('goods_nm_pr', '')}]]></GOODS_NM_PR>
        <GOODS_REMARKS2><![CDATA[{product_data.get('goods_remarks2', '')}]]></GOODS_REMARKS2>
        <GOODS_REMARKS3><![CDATA[{product_data.get('goods_remarks3', '')}]]></GOODS_REMARKS3>
        <GOODS_REMARKS4><![CDATA[{product_data.get('goods_remarks4', '')}]]></GOODS_REMARKS4>
        <IMPORTNO><![CDATA[{product_data.get('importno', '')}]]></IMPORTNO>
        <GOODS_COST2><![CDATA[{product_data.get('goods_cost2', '')}]]></GOODS_COST2>
        <ORIGIN2><![CDATA[{product_data.get('origin2', '')}]]></ORIGIN2>
        <EXPIRE_DM><![CDATA[{product_data.get('expire_dm', '')}]]></EXPIRE_DM>
        <SUPPLY_SAVE_YN><![CDATA[{product_data.get('supply_save_yn', '')}]]></SUPPLY_SAVE_YN>
        <DESCRITION><![CDATA[{product_data.get('descrition', '')}]]></DESCRITION>    
    </DATA>
</SABANG_GOODS_REGI>"""
        return xml_content
    
    # 상품 등록 요청
    def create_product_via_url(self, xml_url: str) -> str:
        try:
            api_url = urljoin(self.admin_url, '/RTL_API/xml_goods_regi.html')
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")
            print(f"최종 요청 URL: {full_url}")
            response = requests.post(full_url, timeout=30)
            response.raise_for_status()
            # 요청 결과를 확인 후 변경 필요
            return response.text
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise