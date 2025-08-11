from typing import Any
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
import html
from core.settings import SETTINGS
from utils.logs.sabangnet_logger import get_logger
from utils.make_xml.sabangnet_xml import SabangnetXml
from models.product.product_raw_data import ProductRawData
from utils.make_xml.file_name_for_xml import sanitize_filename
from schemas.product.product_raw_data_dto import ProductRawDataDto
from utils.mappings.product_create_field_eng_mapping import get_db_to_xml_mapping


logger = get_logger(__name__, level="DEBUG")


class ProductRegistrationXml(SabangnetXml):

    _PATH = "./files/xml/request/product"

    def create_body_product_registration(self, root, product_raw_data_dto: ProductRawDataDto, row_idx: int):
        """
        상품 등록용 XML body 생성
        Args:
            root: XML 루트 엘리먼트
            product_raw_data_dto: ProductRawDataDto
            row_idx: 행 인덱스
        Returns:
            생성된 DATA 엘리먼트
        """
        data = ET.SubElement(root, "DATA")
        
        product_raw_data = ProductRawData(**product_raw_data_dto.model_dump())
        # DB 필드와 XML 태그 매핑 처리
        for db_field, xml_tag_name in get_db_to_xml_mapping().items():
            if xml_tag_name:
                db_value = getattr(product_raw_data, db_field, None)
                if SETTINGS.CONPANY_GOODS_CD_TEST_MODE:
                    self._make_test_xml_element(xml_tag_name, db_field, db_value, data, row_idx)
                else:
                    child = ET.SubElement(data, xml_tag_name)
                    # HTML 엔티티가 인코딩된 경우 디코딩하여 원본 텍스트로 복원
                    if db_value is not None:
                        # HTML 엔티티 디코딩 (예: &lt; -> <, &gt; -> >)
                        decoded_value = html.unescape(str(db_value))
                        child.text = decoded_value
                    else:
                        child.text = ""
        
        return data

    def make_product_registration_xml(
            self,
            product_raw_data_dto_list: list[ProductRawDataDto],
            product_create_db_count: int,
            file_name: str = None,
            dst_path_name: str = None
        ) -> Path:
        """
        상품 등록용 XML 파일 생성
        Args:
            product_data_list: ProductRawDataDto 리스트
            product_create_db_count: 이미 증가된 product_create_db 카운터 값
            file_name: 파일명 (선택사항)
        Returns:
            생성된 XML 파일 경로
        """
        # 파일명 생성
        if not file_name:
            now_str = datetime.now().strftime("%m%d%H%M")
            base_name = f"product_create_request_db_{now_str}_{product_create_db_count}.xml"
            if SETTINGS.CONPANY_GOODS_CD_TEST_MODE:
                base_name = f"product_create_request_db_test_{now_str}_{product_create_db_count}.xml"
            file_name = f"{self._PATH}/" + sanitize_filename(base_name)

        # XML 루트 엘리먼트 생성
        root = ET.Element("SABANGNET_GOODS_REGI")
        
        # 헤더 생성
        self._create_product_header(root=root)
        
        # 각 상품 데이터에 대해 body 생성
        for idx, product_raw_data_dto in enumerate(product_raw_data_dto_list):
            self.create_body_product_registration(
                root=root,
                product_raw_data_dto=product_raw_data_dto,
                row_idx=idx
            )
        
        # XML 파일 저장
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        # 파일 경로 객체 생성
        file_path = Path(file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 임시로 메모리에 XML 문자열 생성
        xml_string = ET.tostring(root, encoding='unicode')
        
        # HTML 엔티티를 원본으로 복원 (XML 라이브러리가 자동으로 인코딩한 것을 되돌림)
        xml_string = xml_string.replace('&lt;', '<').replace('&gt;', '>')
        
        with open(file_path, "wb") as f:
            f.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
            f.write(xml_string.encode("EUC-KR"))
        
        return file_path

    def _make_test_xml_element(self, xml_tag_name: str, db_field: str, db_value: Any, data_element: ET.Element, row_idx: int) -> None:
        """
        테스트 모드용 XML 엘리먼트 생성
        """
        convert_dict = {
            "goods_nm": f"[TEST]{str(db_value) if db_value else 'TEST_상품명'}",
            "compayny_goods_cd": f"TEST_backend_db_{row_idx}",
            "class_cd1": "S000002",  # 마이카테고리
            "goods_gubun": "5",
            "goods_cost": "999999999",
            "goods_price": "999999999",
            "goods_consumer_price": "999999999",
            "stock_use_yn": "N",
        }
        
        if isinstance(xml_tag_name, tuple):
            # 마이카테고리인 경우 모두 A01 ~ A04로 채움
            for i in range(1, len(xml_tag_name) + 1):
                child = ET.SubElement(data_element, xml_tag_name[i - 1])
                child.text = f"A0{i}"
            return
        
        child = ET.SubElement(data_element, xml_tag_name)
        test_value = convert_dict.get(db_field, str(db_value) if db_value is not None else "")
        child.text = test_value

    def input_product_id_to_db(self, response_xml: str) -> list[tuple[str, int]]:
        """
        사방넷 상품등록 결과 XML에서 PRODUCT_ID와 COMPAYNY_GOODS_CD를 추출해 DB에 저장
        Args:
            response_xml: 사방넷에서 받은 결과 XML 문자열
            session: DB 세션 (AsyncSession)
        Returns:
            저장된 (compayny_goods_cd, product_id) 리스트
        """
        # 1. XML 파싱하여 (COMPAYNY_GOODS_CD, PRODUCT_ID) 쌍 추출
        compayny_goods_cd_and_product_ids = []
        try:
            root = ET.fromstring(response_xml)
            for data_elem in root.findall("DATA"):
                product_id_elem = data_elem.find("PRODUCT_ID")
                compayny_goods_cd_elem = data_elem.find("COMPAYNY_GOODS_CD")
                if (
                    product_id_elem is not None and product_id_elem.text and
                    compayny_goods_cd_elem is not None and compayny_goods_cd_elem.text
                ):
                    try:
                        product_id = int(product_id_elem.text.strip())
                        compayny_goods_cd = compayny_goods_cd_elem.text.strip()
                        compayny_goods_cd_and_product_ids.append((compayny_goods_cd, product_id))
                    except Exception:
                        pass
            return compayny_goods_cd_and_product_ids
        except Exception as e:
            # 오류 메시지에 XML 내용 전체 포함 (최대 2000자)
            xml_preview = response_xml[:2000] + "..." if len(response_xml) > 2000 else response_xml
            error_message = f"상품등록 결과 XML 파싱 오류: {e} (XML 내용: {xml_preview})"
            raise RuntimeError(error_message)

        # 2. DB에 PRODUCT_ID update (compayny_goods_cd 기준)
        # >>> product_update_service로 옮겼음