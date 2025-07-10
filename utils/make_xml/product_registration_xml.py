from utils.make_xml.sabangnet_xml import SabangnetXml
from models.product.product_raw_data import ProductRawData
from typing import List
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from core.settings import SETTINGS
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.product_create_field_eng_mapping import get_db_to_xml_mapping
from utils.make_xml.file_name_for_xml import sanitize_filename

class ProductRegistrationXml(SabangnetXml):

    _PATH = "./files/xml/request/product"

    def create_body_product_registration(self, root, product_data: ProductRawData, row_idx: int):
        """
        상품 등록용 XML body 생성
        Args:
            root: XML 루트 엘리먼트
            product_data: ProductRawData 인스턴스
            row_idx: 행 인덱스
        Returns:
            생성된 DATA 엘리먼트
        """
        data = ET.SubElement(root, "DATA")
        
        # DB 필드와 XML 태그 매핑 처리
        for db_field, xml_tag_name in get_db_to_xml_mapping().items():
            if xml_tag_name:
                db_value = getattr(product_data, db_field, None)
                if SETTINGS.CONPANY_GOODS_CD_TEST_MODE:
                    self._make_test_xml_element(xml_tag_name, db_field, db_value, data, row_idx)
                else:
                    child = ET.SubElement(data, xml_tag_name)
                    child.text = str(db_value) if db_value is not None else ""
        
        return data

    def make_product_registration_xml(self, product_data_list: List[ProductRawData], product_create_db_count: int, file_name: str = None) -> Path:
        """
        상품 등록용 XML 파일 생성
        Args:
            product_data_list: ProductRawData 리스트
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
        for idx, product_data in enumerate(product_data_list):
            self.create_body_product_registration(
                root=root,
                product_data=product_data,
                row_idx=idx
            )
        
        # XML 파일 저장
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        # 파일 경로 객체 생성
        file_path = Path(file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
            tree.write(f, encoding='EUC-KR', xml_declaration=False)
        
        return file_path

    def _make_test_xml_element(self, xml_tag_name: str, db_field: str, db_value: any, data_element: ET.Element, row_idx: int) -> None:
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

    async def input_product_id_to_db(self, response_xml: str, session):
        """
        사방넷 상품등록 결과 XML에서 PRODUCT_ID와 COMPAYNY_GOODS_CD를 추출해 DB에 저장
        Args:
            response_xml: 사방넷에서 받은 결과 XML 문자열
            session: DB 세션 (AsyncSession)
        Returns:
            저장된 (compayny_goods_cd, product_id) 리스트
        """
        from repository.product_repository import ProductRepository

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
        except Exception as e:
            raise RuntimeError(f"상품등록 결과 XML 파싱 오류: {e}")

        # 2. DB에 PRODUCT_ID update (compayny_goods_cd 기준)
        repo = ProductRepository(session)
        for compayny_goods_cd, product_id in compayny_goods_cd_and_product_ids:
            await repo.update_product_id_by_compayny_goods_cd(compayny_goods_cd, product_id)
        return compayny_goods_cd_and_product_ids