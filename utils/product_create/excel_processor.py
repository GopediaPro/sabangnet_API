from pathlib import Path
import pandas as pd
from lxml import etree as ET
from utils.excel_reader import ExcelReader
from utils.product_create_field_mapping_to_xml import PRODUCT_CREATE_FIELD_MAPPING
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.product_create.template_renderer import TemplateRenderer
from core.settings import SETTINGS

class ExcelProcessor:
    """
    상품 등록 요청을 위한 excel 파일 처리 클래스
    """

    @classmethod
    def excel_to_xml_file(cls, file_name: str, sheet_name: str) -> str | Path:
        """
        품번코드대량등록툴 excel 파일을 xml 파일로 변환
        Args:
            file_name: 엑셀 파일 이름
        Returns:
            xml 파일 경로
        """
        # 1. 파일 읽기
        df: pd.DataFrame = ExcelReader.read_excel_file(file_name, sheet_name)

        # 2. '순번' 행 및 실제 값 시작 위치 설정
        st_idx = 0
        hdr_idx = 0
        for idx, row in df.iterrows():
            first_cell = str(row.iloc[0]).strip()
            if not hdr_idx and ("순번" in first_cell):
                hdr_idx = idx
                continue
            if first_cell.isdigit():
                st_idx = idx
                break
        hdr_row = df.iloc[hdr_idx]  # 순번 | 대표이미지확인 | ... | 속성값37 | 속성값38
        headers = [str(tag).strip().split("\n")[0] for tag in hdr_row]
        df = df.iloc[st_idx:]
        df.columns = headers
        df.reset_index(drop=True, inplace=True)

        # 3. XML 렌더링
        xml_element_list = cls.__generate_xml_element_list(df)

        # 4. XML 파일 저장
        xml_file_path = SabangNetPathUtils.get_xml_file_path() / "product_create_request.xml"
        if SETTINGS.CONPANY_GOODS_CD_TEST_MODE:
            xml_file_path = SabangNetPathUtils.get_xml_file_path() / "product_create_request_n8n_test.xml"
        TemplateRenderer.render_to_xml_template(
            xml_element_list,
            SabangNetPathUtils.get_xml_template_path() / "product_create_request.xml",
            xml_file_path)
        return xml_file_path

    @classmethod
    def excel_to_xml_string(cls, file_name: str, sheet_name: str) -> str:
        """
        품번코드대량등록툴 excel 파일을 xml 문자열로 변환
        """
        df: pd.DataFrame = ExcelReader.read_excel_file(file_name, sheet_name)
        xml_element_list = cls.__generate_xml_element_list(df)
        return TemplateRenderer.render_to_xml_string(xml_element_list)

    @classmethod
    def __generate_xml_element_list(cls, df: pd.DataFrame) -> list[ET.Element]:
        """
        엑셀 데이터를 XML 엘리먼트 리스트로 변환
        Args:
            df: 엑셀 데이터
        Returns:
            XML 엘리먼트 리스트
        """
        xml_element_list = []
        for idx, row in df.iterrows():
            data_element = ET.Element("DATA")
            cls.__convert_excel_row_to_xml_element(row, data_element, idx)
            xml_element_list.append(data_element)
        return xml_element_list
    
    @classmethod
    def __convert_excel_row_to_xml_element(cls, row: pd.Series, data_element: ET.Element, row_idx: int) -> None:
        # 1. 엑셀 헤더와 엑셀 값을 가져옴.
        for column_idx, (excel_header, excel_value) in enumerate(row.items()):
            # 2. 필드 매핑 적용 (mapped_value: 사방넷 XML에 적용될 태그명)
            xml_tag_name = PRODUCT_CREATE_FIELD_MAPPING.get(excel_header)
            # 3. 매핑 딕셔너리에 있는 것들만 처리
            if xml_tag_name:
                if column_idx < 7:
                    continue
                elif SETTINGS.CONPANY_GOODS_CD_TEST_MODE:
                    cls.__make_test_xml_element(xml_tag_name, excel_header, excel_value, data_element, row_idx)
                else:
                    if isinstance(xml_tag_name, tuple):
                        values = [val.strip() for val in excel_value.split(">")] # 3 or 4개의 값이 있음.
                        for i, category_code in enumerate(values):
                            if category_code:
                                child = ET.SubElement(data_element, xml_tag_name[i])
                                child.text = ET.CDATA(category_code)
                        continue
                    child: ET.Element = ET.SubElement(data_element, xml_tag_name)
                    child.text = ET.CDATA(str(excel_value))
    
    @classmethod
    def __make_test_xml_element(cls, xml_tag_name: str, excel_header: str, excel_value: str, data_element: ET.Element, row_idx: int) -> None:
        convert_dict = {
            "상품명": f"[TEST]{str(excel_value)}",
            "자체상품코드": f"TEST_backend_test_{row_idx}",
            "표준카테고리": "S000002",
            "상품구분": "5",
            "원가": "999999999",
            "판매가": "999999999",
            "TAG가": "999999999",
            "재고관리사용여부": "N",
        }
        if isinstance(xml_tag_name, tuple):
            # "마이카테고리" 인 경우 xml_tag_name 은 ("CLASS_CD1", "CLASS_CD2", "CLASS_CD3", "CLASS_CD4") 처럼 글자가 아니고 튜플이 됨.
            for i in range(1, len(xml_tag_name) + 1):
                child: ET.Element = ET.SubElement(data_element, xml_tag_name[i - 1])
                child.text = ET.CDATA(f"A0{i}") # 모두 A01 ~ A04로 채움.
            return
        child: ET.Element = ET.SubElement(data_element, xml_tag_name)
        child.text = ET.CDATA(convert_dict.get(excel_header, str(excel_value)))