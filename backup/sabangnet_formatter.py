import re
import requests
import pandas as pd
from pathlib import Path
from lxml import etree as ET
from datetime import datetime
from core.settings import SETTINGS
from typing import Iterator, Tuple, Any
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.product_create_field_mapping_xml import PRODUCT_CREATE_FIELD_MAPPING


class SabangNetFormatter:
    def __init__(self):
        self.xlsx_base_path = SabangNetPathUtils.get_xlsx_file_path()
        self.xml_base_path = SabangNetPathUtils.get_xml_file_path()
        self.xml_template_path = SabangNetPathUtils.get_xml_template_path()

    def __sanitize_tag(self, tag: str) -> str:
        tag = str(tag).strip().split("\n")[0]
        tag = re.sub(r"[^\w가-힣]", "_", tag)
        if not tag or tag[0].isdigit():
            tag = f"col_{tag}"
        return tag

    def __render_element_to_string(self, et_element: ET.Element) -> str:
        xml_bytes: bytes = ET.tostring(
            et_element,
            encoding="euc-kr",
            pretty_print=True,
            xml_declaration=False,
            with_tail=False
        )
        xml_str: str = xml_bytes.decode("euc-kr")
        return xml_str

    def xlsx_to_xml(self, file_name: str, api_type: str) -> str | Path:
        """
        excel 파일을 xml 파일로 변환
        Args:
            file_name: 엑셀 파일 이름
            api_type: 지원하는 API 타입
        Returns:
            xml 파일 경로
        """
        if api_type == "product_create_request":
            field_mapping = PRODUCT_CREATE_FIELD_MAPPING
            xml_template = self.xml_template_path / f"{api_type}.xml"
        else:
            raise ValueError(f"사방넷에서 지원하지 않는 API 타입입니다. {api_type}")

        # 1. xlsx 파일 읽기
        xlsx_file_path = self.xlsx_base_path / file_name
        if not file_name.endswith(".xlsx"):  # 확장자가 없으면...
            xlsx_file_path = self.xlsx_base_path / f"{file_name}.xlsx"
        if not xlsx_file_path.exists():
            raise FileNotFoundError(f"해당 파일을 찾을 수 없습니다. (파일명: {file_name}.xlsx)")
        df_xlsx: pd.DataFrame = pd.read_excel(xlsx_file_path).fillna("")

        # 2. 숫자로 시작하는 행 선택
        st_row = 0
        for idx, row in df_xlsx.iterrows():
            first_cell = str(row.iloc[0]).strip()
            if first_cell.isdigit():
                st_row = idx
                break
        hdr_row = df_xlsx.iloc[0]  # 순번 | 대표이미지확인 | ... | 속성값37 | 속성값38
        headers = [self.__sanitize_tag(col) for col in hdr_row]
        df_xlsx = df_xlsx.iloc[st_row:]
        df_xlsx.columns = headers
        df_xlsx.reset_index(drop=True, inplace=True)

        # 3. 필드 매핑 적용 및 XML 생성 -> 하드코딩 된 부분은 추후 마스터/전문몰/1+1 작업시 개선 예정
        data_list = []
        idx = 1 # 자체상품코드 번호
        for _, row in df_xlsx.iterrows():
            already_exist_model_nm = False
            data = ET.Element("DATA")
            row_items: Iterator[Tuple[str, str | Any]] = row.items()
            # 3-1. 엑셀 헤더와 엑셀 값을 가져옴.
            for excel_header, excel_value in row_items:
                # 3-2. 필드 매핑 적용 (mapped_value: 사방넷 XML에 적용될 태그명)
                xml_tag_name = field_mapping.get(excel_header) 
                # 3-3. 매핑 딕셔너리에 있는 것들만 처리 ('구분', '대표이미지확인' 이런것들은 매핑 안되기 때문에 그냥 지나감...)
                if xml_tag_name:
                    if excel_header == "마이카테고리":
                        # 마이카테고리가 비어있으면 모두 A01 ~ A04로 채움.
                        if excel_value == "":
                            # 여기서 xml_tag_name 은 ("CLASS_CD1", "CLASS_CD2", "CLASS_CD3", "CLASS_CD4" -> 마지막 건은 없을수도 있음) 가 됨.
                            for i in range(1, len(xml_tag_name) + 1):
                                child: ET.Element = ET.SubElement(data, self.__sanitize_tag(f"{xml_tag_name[i - 1]}"))
                                child.text = ET.CDATA(f"A0{i}")
                            continue
                        else:
                            values = [val.strip() for val in excel_value.split(">")] # 3 or 4개의 값이 있음.
                            for i, category_code in enumerate(values):
                                if category_code:
                                    child = ET.SubElement(data, xml_tag_name[i])
                                    child.text = ET.CDATA(category_code)
                            continue
                    # 이 부분은 임의로 이렇게 처리했지만 나중에 마스터/전문몰/1+1 다 처리해야됨.
                    if excel_header == "모델명" and already_exist_model_nm:
                        continue
                    child: ET.Element = ET.SubElement(data, self.__sanitize_tag(xml_tag_name))
                    already_exist_model_nm = True
                    if excel_header == "상품명":
                        child.text = ET.CDATA(f"[TEST]{str(excel_value)}")
                    elif excel_header == "자체상품코드":
                        child.text = ET.CDATA(f"TEST_backend_test_{idx}")
                    elif excel_header == "원가" or excel_header == "판매가" or excel_header == "TAG가":
                        child.text = ET.CDATA(f"999999999")
                    elif excel_header == "재고관리사용여부":
                        child.text = ET.CDATA("N")
                    else:
                        child.text = ET.CDATA(str(excel_value))
            data_list.append(data)
            idx += 1

        # 4. XML 문자열 반환
        xml_str: str = "\t\n".join(
            [self.__render_element_to_string(data) for data in data_list])

        xml_file_path = self.xml_base_path / f"{api_type}.xml"

        with open(xml_template, "r", encoding="euc-kr") as t:
            xml_template = t.read()
            xml_template = xml_template.format(
                company_id=SETTINGS.SABANG_COMPANY_ID,
                auth_key=SETTINGS.SABANG_AUTH_KEY,
                send_date=datetime.now().strftime('%Y%m%d'),
                send_goods_cd_rt=SETTINGS.SABANG_SEND_GOODS_CD_RT,
                result_type=SETTINGS.SABANG_RESULT_TYPE,
                xml_str=xml_str
            )

        with open(xml_file_path, "w", encoding="euc-kr") as f:
            f.write(xml_template)

        print(f"XML 파일이 생성되었습니다. {xml_file_path}")
        with open(xml_file_path, "r", encoding="euc-kr") as f:
            xml_content = f.read()

        return xml_file_path


if __name__ == "__main__":
    target = "OK_test_디자인업무일지"
    formatter = SabangNetFormatter()
    xml_file_path = formatter.xlsx_to_xml(target, "product_create_request")
    # 웹훅 방식
    with open(xml_file_path, 'rb') as f:
        files = {
            'file': (f'{xml_file_path.stem}_n8n_test.xml', f, 'application/xml')}
        data = {'filename': f'{xml_file_path.stem}_n8n_test.xml'}
        response = requests.post(
            f"{SETTINGS.N8N_WEBHOOK_BASE_URL}{"-test" if SETTINGS.N8N_TEST == "TRUE" else ""}/{SETTINGS.N8N_WEBHOOK_PATH}",
            files=files,
            data=data
        )
        response.raise_for_status()
        result: dict = response.json()
        print(result)