import pandas as pd
from pathlib import Path
from datetime import datetime
from core.settings import SETTINGS
import xml.etree.ElementTree as ET
from utils.excels.excel_reader import ExcelReader
from utils.logs.sabangnet_logger import get_logger
from utils.make_xml.sabangnet_xml import SabangnetXml
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.make_xml.file_name_for_xml import sanitize_filename
from utils.mappings.product_create_field_xml_mapping import PRODUCT_CREATE_FIELD_MAPPING


logger = get_logger(__name__)


class ProductCreateXml(SabangnetXml):
    """
    상품등록용 XML 템플릿 렌더링 클래스
    """
    
    _PATH: Path = SabangNetPathUtils.get_xml_request_path() / "product"

    def __init__(self, src_file_name: str, src_sheet_name: str):
        self.df = ExcelReader.read_excel_file(src_file_name, src_sheet_name)

    def _set_start_position(self):
        """
        순번 행 및 실제 값 시작 위치 설정
        """
        st_idx = 0
        hdr_idx = 0
        for idx, row in self.df.iterrows():
            first_cell = str(row.iloc[0]).strip()
            if not hdr_idx and ("순번" in first_cell):
                hdr_idx = idx
                continue
            if first_cell.isdigit():
                st_idx = idx
                break
        hdr_row = self.df.iloc[hdr_idx]  # 순번 | 대표이미지확인 | ... | 속성값37 | 속성값38
        headers = [str(tag).strip().split("\n")[0] for tag in hdr_row]
        self.df = self.df.iloc[st_idx:]
        self.df.columns = headers
        self.df.reset_index(drop=True, inplace=True)

    def _create_body(self, root: ET.Element, row: pd.Series, row_idx: int) -> None:
        # 1. root에 대해 DATA subelement 생성
        data_element: ET.Element = ET.SubElement(root, "DATA")
        # 2. 엑셀 헤더와 엑셀 값을 가져옴.
        for column_idx, (excel_header, excel_value) in enumerate(row.items()):
            # 3. 필드 매핑 적용 (mapped_value: 사방넷 XML에 적용될 태그명)
            xml_tag_name = PRODUCT_CREATE_FIELD_MAPPING.get(excel_header)
            if not xml_tag_name or column_idx < 7: # 태그 매핑 딕셔너리에 없거나, 엑셀 7번째 칼럼까지는 무시
                continue
            if isinstance(xml_tag_name, tuple):
                values = [val.strip() for val in excel_value.split(">")] # 3 or 4개의 값이 있음.
                for i, category_code in enumerate(values):
                    if category_code:
                        child: ET.Element = ET.SubElement(data_element, xml_tag_name[i])
                        child.text = category_code
                continue
            child: ET.Element = ET.SubElement(data_element, xml_tag_name)
            child.text = str(excel_value)

    def _make_test_xml_element(self, xml_tag_name: str, excel_header: str, excel_value: str, data_element: ET.Element, row_idx: int) -> None:
        """
        테스트 데이터 생성
        """
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
                child.text = f"A0{i}" # 모두 A01 ~ A04로 채움.
            return
        child: ET.Element = ET.SubElement(data_element, xml_tag_name)
        child.text = convert_dict.get(excel_header, str(excel_value))

    def make_product_create_xml(self, dst_path_name: str = None) -> Path:
        """
        '품번코드대량등록툴' Excel 파일로부터 상품 등록용 XML 파일 생성
        Args:
            dst_path_name: 저장할 경로 + 파일명 (선택사항)
        Returns:
            생성된 XML 파일 경로
        """
        # 파일명 생성
        if not dst_path_name:
            now_str = datetime.now().strftime("%m%d%H%M")
            file_name = f"product_create_request_{now_str}.xml"
            if SETTINGS.CONPANY_GOODS_CD_TEST_MODE:
                file_name = f"product_create_request_n8n_test_{now_str}.xml"
            dst_path_name = str(self._PATH / sanitize_filename(file_name))

        # XML 루트 엘리먼트 생성
        root = ET.Element("SABANG_GOODS_REGI")
        
        # 헤더 생성
        self._create_product_header(root=root)

        # 시작 위치 설정
        self._set_start_position()

        # 각 상품 데이터에 대해 body 생성
        for row_idx, row in self.df.iterrows():
            self._create_body(root=root, row=row, row_idx=row_idx)
        
        # XML 파일 저장
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        # 파일 경로 객체 생성
        file_path = Path(dst_path_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
            tree.write(f, encoding='EUC-KR', xml_declaration=False)
        
        return file_path
