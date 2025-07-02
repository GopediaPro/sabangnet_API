from typing import List
from pathlib import Path
from datetime import datetime
from lxml import etree as ET

from core.settings import SETTINGS
from utils.sabangnet_logger import get_logger


logger = get_logger(__name__)


class TemplateRenderer:
    """
    XML 템플릿 렌더링 클래스
    """

    @classmethod
    def render_to_xml_string(cls, xml_element_list: List[ET.Element]) -> str:
        """
        XML 엘리먼트 리스트를 받아서 문자열로 변환
        Args:
            xml_element_list: XML 엘리먼트 리스트
        Returns:
            XML 문자열
        """
        xml_fragments: List[str] = []
        for xml_element in xml_element_list:
            xml_bytes: bytes = ET.tostring(
                xml_element,
                encoding="euc-kr",
                pretty_print=True,
                xml_declaration=False
            )
            xml_fragments.append(xml_bytes.decode("euc-kr"))
        return "\t\n".join(xml_fragments)

    @classmethod
    def render_to_xml_template(cls, xml_element_list: List[ET.Element], xml_template_path: Path, xml_dst_path: Path) -> Path:
        """
        excel 데이터 리스트를 받아서 템플릿에 렌더링하여 파일로 저장
        Args:
            xml_element_list: XML 엘리먼트 리스트
            xml_template_path: 템플릿 파일 경로
            xml_dst_path: 저장할 파일 경로
        """
        xml_str: str = cls.render_to_xml_string(xml_element_list)

        with open(xml_template_path, "r", encoding="euc-kr") as t:
            xml_template = t.read()
            xml_template = xml_template.format(
                company_id=SETTINGS.SABANG_COMPANY_ID,
                auth_key=SETTINGS.SABANG_AUTH_KEY,
                send_date=datetime.now().strftime('%Y%m%d'),
                send_goods_cd_rt=SETTINGS.SABANG_SEND_GOODS_CD_RT,
                result_type=SETTINGS.SABANG_RESULT_TYPE,
                xml_str=xml_str
            )

        with open(xml_dst_path, "w", encoding="euc-kr") as f:
            f.write(xml_template)

        logger.info(f"XML 파일이 생성되었습니다. {xml_dst_path}")
        return xml_dst_path