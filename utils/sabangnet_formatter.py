import re
import pandas as pd
from lxml import etree as ET
from datetime import datetime
from core.settings import SETTINGS
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.product_create_field_mapping import PRODUCT_CREATE_FIELD_MAPPING


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

    def xlsx_to_xml(self, file_name: str, api_type: str) -> str:
        """
        excel 파일을 xml 파일로 변환
        Args:
            xlsx_path: 엑셀 파일 경로
            file_name: 저장할 파일 이름
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

        # 3. 필드 매핑 적용 및 XML 생성
        data_list = []
        for _, row in df_xlsx.iterrows():
            already_exist_model_nm = False
            data = ET.Element("DATA")
            for key, value in row.items():
                mapped_key = field_mapping.get(key)
                if mapped_key:
                    if key == "모델명" and already_exist_model_nm:
                        continue
                    child: ET.Element = ET.SubElement(data, self.__sanitize_tag(mapped_key))
                    already_exist_model_nm = True
                    if key == "상품명":
                        child.text = ET.CDATA(f"[TEST]{str(value)}")
                    elif key == "원가" or key == "판매가" or key == "TAG가":
                        child.text = ET.CDATA(f"999999999")
                    elif key == "재고관리사용여부":
                        child.text = ET.CDATA("N")
                    else:
                        child.text = ET.CDATA(str(value))
            data_list.append(data)

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

        return xml_file_path

    # def csv_to_xml(self, csv_path: str) -> str:
    #     df_csv: pd.DataFrame = pd.read_csv(csv_path).fillna("")
    #     dummy = ET.Element("dummy")
    #     for _, row in df_csv.iterrows():
    #         data = ET.SubElement(dummy, "DATA")
    #         for key, value in row.items():
    #             child = ET.SubElement(data, key)
    #             child.text = ET.CDATA(str(value))
    #     xml_str: bytes = ET.tostring(
    #         dummy, encoding="euc-kr", pretty_print=True, xml_declaration=False, with_tail=False)
    #     return "\n".join(xml_str.decode("euc-kr").splitlines()[1:-1])

    # def json_to_xml(self, json_path: str) -> str:
    #     with open(json_path, "r", encoding="euc-kr") as f:
    #         json_data = json.load(f)
    #     dummy = ET.Element("dummy")
    #     for item in json_data:
    #         data = ET.SubElement(dummy, "DATA")
    #         for key, value in item.items():
    #             child = ET.SubElement(data, key)
    #             child.text = ET.CDATA(str(value))


if __name__ == "__main__":
    target = "OK_test_디자인업무일지"
    formatter = SabangNetFormatter()
    xml_content = formatter.xlsx_to_xml(target, "product_create_request")
    print(xml_content)
