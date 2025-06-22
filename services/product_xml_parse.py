import xml.etree.ElementTree as ET
from decimal import Decimal


class ProductXmlParser:
    """
    xml 파일을 파싱하여 list[dict]형태로 반환하는 클래스
    """

    # 필수 항목 목록
    NOT_NULL_FIELDS: set[str] = {
        'goods_nm', 'compayny_goods_cd', 'goods_gubun', 'class_cd1', 'class_cd2', 'class_cd3',
        'origin', 'goods_season', 'sex', 'status', 'tax_yn', 'delv_type',
        'goods_cost', 'goods_price', 'goods_consumer_price',
        'img_path', 'img_path1', 'img_path3', 'opt_type',
    }

    # 필수 항목 검증
    def validate_fields(self, key: str, value: str | None) -> None:
        if key in self.NOT_NULL_FIELDS and not value:
            raise ValueError(f"[{key}] 필수 항목이 비어 있습니다.")

    # xml 파일을 파싱하여 데이터 리스트로 반환
    def xml_parse(self, xml_content: str) -> list[dict]:
        """
        xml_content : 파싱할 xml 파일 경로
        return : dict 형태의 데이터 리스트
        """
        # 문자열을 정수로 변환
        def to_int(value: str) -> int:
            return int(value) if value else None

        # 문자열을 소수점 이하 2자리 실수로 변환
        def to_decimal(value: str) -> Decimal:
            return Decimal(value) if value else None

        # 변환 대상 필드 목록
        int_fields = {
            "goods_gubun", "goods_season", "sex", "status",
            "deliv_able_region", "tax_yn", "delv_type",
            "banpum_area", "opt_type"
        }
        decimal_fields = {
            "delv_cost", "goods_cost", "goods_price",
            "goods_consumer_price", "goods_cost2"
        }

        # xml 파일 읽기
        with open(xml_content, "r", encoding="utf-8") as f:
            xml_str = f.read()
        root = ET.fromstring(xml_str)

        # <DATA> 태그 찾기
        data_list: list[dict] = []
        for data in root.findall(".//DATA"):
            row = {}
            for child in data:
                key = child.tag.lower()
                value = child.text.strip() if child.text else None
                self.validate_fields(key, value)

                # 필드 타입 변환
                if key in int_fields:
                    row[key] = to_int(value)
                elif key in decimal_fields:
                    row[key] = to_decimal(value)
                else:
                    row[key] = value
            data_list.append(row)
        return data_list
