from pathlib import Path
from typing import List, Optional
from lxml import etree as ET
from datetime import datetime

from models.product.product_raw_data import ProductRawData
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.product_create.template_renderer import TemplateRenderer
from core.settings import SETTINGS
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)


class DbProcessor:
    """
    DB 데이터를 XML로 변환하는 프로세서 클래스
    test_product_raw_data 테이블의 데이터를 사방넷 XML 형식으로 변환
    """

    @classmethod
    def db_to_xml_file(cls, product_data_list: List[ProductRawData]) -> str | Path:
        """
        DB 데이터를 XML 파일로 변환
        Args:
            product_data_list: ProductRawData 리스트
        Returns:
            xml 파일 경로
        """
        logger.info(f"DB to XML 변환 시작 - {len(product_data_list)}개 상품")
        
        # 1. XML 엘리먼트 리스트 생성
        xml_element_list = cls.__generate_xml_element_list(product_data_list)

        # 2. XML 파일 저장
        xml_file_path = SabangNetPathUtils.get_xml_file_path() / "product_create_request_db.xml"
        if SETTINGS.TEST_MODE:
            xml_file_path = SabangNetPathUtils.get_xml_file_path() / "product_create_request_db_test.xml"
            
        TemplateRenderer.render_to_xml_template(
            xml_element_list,
            SabangNetPathUtils.get_xml_template_path() / "product_create_request.xml",
            xml_file_path
        )
        
        logger.info(f"DB to XML 변환 완료 - 파일 저장: {xml_file_path}")
        return xml_file_path

    @classmethod
    def db_to_xml_string(cls, product_data_list: List[ProductRawData]) -> str:
        """
        DB 데이터를 XML 문자열로 변환
        Args:
            product_data_list: ProductRawData 리스트
        Returns:
            XML 문자열
        """
        xml_element_list = cls.__generate_xml_element_list(product_data_list)
        return TemplateRenderer.render_to_xml_string(xml_element_list)

    @classmethod
    def __generate_xml_element_list(cls, product_data_list: List[ProductRawData]) -> List[ET.Element]:
        """
        DB 데이터를 XML 엘리먼트 리스트로 변환
        Args:
            product_data_list: ProductRawData 리스트
        Returns:
            XML 엘리먼트 리스트
        """
        xml_element_list = []
        for idx, product_data in enumerate(product_data_list):
            data_element = ET.Element("DATA")
            cls.__convert_db_row_to_xml_element(product_data, data_element, idx)
            xml_element_list.append(data_element)
        return xml_element_list
    
    @classmethod
    def __convert_db_row_to_xml_element(cls, product_data: ProductRawData, data_element: ET.Element, row_idx: int) -> None:
        """
        DB 레코드를 XML 엘리먼트로 변환
        Args:
            product_data: ProductRawData 인스턴스
            data_element: XML 엘리먼트
            row_idx: 행 인덱스
        """
        # DB 필드와 XML 태그 매핑 처리
        for db_field, xml_tag_name in cls.__get_db_to_xml_mapping().items():
            if xml_tag_name:
                db_value = getattr(product_data, db_field, None)
                
                if SETTINGS.TEST_MODE:
                    cls.__make_test_xml_element(xml_tag_name, db_field, db_value, data_element, row_idx)
                else:
                    # 마이카테고리 (CLASS_CD1, CLASS_CD2, CLASS_CD3, CLASS_CD4) 특별 처리
                    if isinstance(xml_tag_name, tuple):
                        for i, tag in enumerate(xml_tag_name):
                            category_value = getattr(product_data, f"class_cd{i+1}", None)
                            if category_value:
                                child = ET.SubElement(data_element, tag)
                                child.text = ET.CDATA(str(category_value))
                        continue
                    
                    # 일반 필드 처리
                    child: ET.Element = ET.SubElement(data_element, xml_tag_name)
                    child.text = ET.CDATA(str(db_value) if db_value is not None else "")
    
    @classmethod
    def __make_test_xml_element(cls, xml_tag_name: str, db_field: str, db_value: any, data_element: ET.Element, row_idx: int) -> None:
        """
        테스트 모드용 XML 엘리먼트 생성
        """
        convert_dict = {
            "goods_nm": f"[TEST]{str(db_value) if db_value else 'TEST_상품명'}",
            "compayny_goods_cd": f"TEST_backend_db_{row_idx}",
            "class_cd1": "S000002",  # 표준카테고리
            "goods_gubun": "5",
            "goods_cost": "999999999",
            "goods_price": "999999999",
            "goods_consumer_price": "999999999",
            "stock_use_yn": "N",
        }
        
        if isinstance(xml_tag_name, tuple):
            # 마이카테고리인 경우 모두 A01 ~ A04로 채움
            for i in range(1, len(xml_tag_name) + 1):
                child: ET.Element = ET.SubElement(data_element, xml_tag_name[i - 1])
                child.text = ET.CDATA(f"A0{i}")
            return
        
        child: ET.Element = ET.SubElement(data_element, xml_tag_name)
        test_value = convert_dict.get(db_field, str(db_value) if db_value is not None else "")
        child.text = ET.CDATA(test_value)

    @classmethod
    def __get_db_to_xml_mapping(cls) -> dict:
        """
        DB 필드명과 XML 태그명 매핑 반환
        Returns:
            {db_field_name: xml_tag_name} 딕셔너리
        """
        return {
            # 기본 상품 정보
            "goods_nm": "GOODS_NM",
            "goods_keyword": "GOODS_KEYWORD",
            "model_nm": "MODEL_NM",
            "model_no": "MODEL_NO",
            "brand_nm": "BRAND_NM",
            "compayny_goods_cd": "COMPAYNY_GOODS_CD",
            "goods_search": "GOODS_SEARCH",

            # 분류·구분 코드
            "goods_gubun": "GOODS_GUBUN",
            "class_cd1": ("CLASS_CD1", "CLASS_CD2", "CLASS_CD3", "CLASS_CD4"),  # 특별 처리 - 마이카테고리
            "gubun": "GUBUN",

            # 거래처
            "partner_id": "PARTNER_ID",
            "dpartner_id": "DPARTNER_ID",

            # 제조·원산지
            "maker": "MAKER",
            "origin": "ORIGIN",
            "make_year": "MAKE_YEAR",
            "make_dm": "MAKE_DM",

            # 시즌·성별·상태
            "goods_season": "GOODS_SEASON",
            "sex": "SEX",
            "status": "STATUS",

            # 배송·세금
            "deliv_able_region": "DELIV_ABLE_REGION",
            "tax_yn": "TAX_YN",
            "delv_type": "DELV_TYPE",
            "delv_cost": "DELV_COST",

            # 반품·가격
            "banpum_area": "BANPUM_AREA",
            "goods_cost": "GOODS_COST",
            "goods_price": "GOODS_PRICE",
            "goods_consumer_price": "GOODS_CONSUMER_PRICE",
            "goods_cost2": "GOODS_COST2",

            # 옵션
            "char_1_nm": "CHAR_1_NM",
            "char_1_val": "CHAR_1_VAL",
            "char_2_nm": "CHAR_2_NM",
            "char_2_val": "CHAR_2_VAL",

            # 이미지 - 대표 + 1-24
            "img_path": "IMG_PATH",
            "img_path1": "IMG_PATH1",
            "img_path2": "IMG_PATH2",
            "img_path3": "IMG_PATH3",
            "img_path4": "IMG_PATH4",
            "img_path5": "IMG_PATH5",
            "img_path6": "IMG_PATH6",
            "img_path7": "IMG_PATH7",
            "img_path8": "IMG_PATH8",
            "img_path9": "IMG_PATH9",
            "img_path10": "IMG_PATH10",
            "img_path11": "IMG_PATH11",
            "img_path12": "IMG_PATH12",
            "img_path13": "IMG_PATH13",
            "img_path14": "IMG_PATH14",
            "img_path15": "IMG_PATH15",
            "img_path16": "IMG_PATH16",
            "img_path17": "IMG_PATH17",
            "img_path18": "IMG_PATH18",
            "img_path19": "IMG_PATH19",
            "img_path20": "IMG_PATH20",
            "img_path21": "IMG_PATH21",
            "img_path22": "IMG_PATH22",
            "img_path23": "IMG_PATH23",
            "img_path24": "IMG_PATH24",

            # 상세/인증
            "goods_remarks": "GOODS_REMARKS",
            "certno": "CERTNO",
            "avlst_dm": "AVLST_DM",
            "avled_dm": "AVLED_DM",
            "issuedate": "ISSUEDATE",
            "certdate": "CERTDATE",
            "cert_agency": "CERT_AGENCY",
            "certfield": "CERTFIELD",

            # 식품·재고
            "material": "MATERIAL",
            "stock_use_yn": "STOCK_USE_YN",

            # 옵션·속성 제어
            "opt_type": "OPT_TYPE",
            "prop1_cd": "PROP1_CD",

            # 속성값 1-33
            "prop_val1": "PROP_VAL1",
            "prop_val2": "PROP_VAL2",
            "prop_val3": "PROP_VAL3",
            "prop_val4": "PROP_VAL4",
            "prop_val5": "PROP_VAL5",
            "prop_val6": "PROP_VAL6",
            "prop_val7": "PROP_VAL7",
            "prop_val8": "PROP_VAL8",
            "prop_val9": "PROP_VAL9",
            "prop_val10": "PROP_VAL10",
            "prop_val11": "PROP_VAL11",
            "prop_val12": "PROP_VAL12",
            "prop_val13": "PROP_VAL13",
            "prop_val14": "PROP_VAL14",
            "prop_val15": "PROP_VAL15",
            "prop_val16": "PROP_VAL16",
            "prop_val17": "PROP_VAL17",
            "prop_val18": "PROP_VAL18",
            "prop_val19": "PROP_VAL19",
            "prop_val20": "PROP_VAL20",
            "prop_val21": "PROP_VAL21",
            "prop_val22": "PROP_VAL22",
            "prop_val23": "PROP_VAL23",
            "prop_val24": "PROP_VAL24",
            "prop_val25": "PROP_VAL25",
            "prop_val26": "PROP_VAL26",
            "prop_val27": "PROP_VAL27",
            "prop_val28": "PROP_VAL28",
            "prop_val29": "PROP_VAL29",
            "prop_val30": "PROP_VAL30",
            "prop_val31": "PROP_VAL31",
            "prop_val32": "PROP_VAL32",
            "prop_val33": "PROP_VAL33",

            # 기타
            "pack_code_str": "PACK_CODE_STR",
            "goods_nm_en": "GOODS_NM_EN",
            "goods_nm_pr": "GOODS_NM_PR",
            "goods_remarks2": "GOODS_REMARKS2",
            "goods_remarks3": "GOODS_REMARKS3",
            "goods_remarks4": "GOODS_REMARKS4",
            "importno": "IMPORTNO",
            "origin2": "ORIGIN2",
            "expire_dm": "EXPIRE_DM",
            "supply_save_yn": "SUPPLY_SAVE_YN",
            "descrition": "DESCRITION",
        } 