from utils.make_xml.sabangnet_xml import SabangnetXml
from schemas.mall_price.mall_price_dto import MallPriceDto
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from utils.make_xml.file_name_for_xml import sanitize_filename

class MallPriceRegistrationXml(SabangnetXml):

    _PATH = "./files/xml/request/mall_price"

    # 쇼핑몰 코드
    SHOP_CODE = {
        # 115% + 3000
        "shop0007", "shop0042", "shop0087", "shop0094", 
        "shop0121", "shop0129", "shop0154", "shop0650",

        # 105% + 3000
        "shop0029", "shop0189", "shop0322", "shop0444",

        # 105%
        "shop0100", "shop0298", "shop0372",

        # +3000
        "shop0381", "shop0416", "shop0449", "shop0498",
        "shop0583", "shop0587", "shop0661",

        # +100
        "shop0055", "shop0067", "shop0068", "shop0273",
        "shop0464",

        # 기본판매가
        "shop0075", "shop0319", "shop0365", "shop0387",
    }

    def create_body(self, root, shop_code: str, compayny_goods_cd: str, price: int, mall_stock_rate: int=None):

        data = ET.SubElement(root, "DATA")

        shop_code_element = ET.SubElement(data, "MALL_CODE")
        shop_code_element.text = shop_code

        compayny_goods_cd_element = ET.SubElement(data, "COMPAYNY_GOODS_CD")
        compayny_goods_cd_element.text = compayny_goods_cd

        mall_price_element = ET.SubElement(data, "MALL_GOODS_PRICE")
        mall_price_element.text = str(price)

        mall_stock_rate_element = ET.SubElement(data, "MALL_GOODS_STOCK_RATE")
        mall_stock_rate_element.text = str(mall_stock_rate) if mall_stock_rate else "0"


        return data
        
    def make_mall_price_dto_registration_xml(self, mall_price_dto: MallPriceDto, count_rev: int, mall_stock_rate: int=None, file_name=None):
        if file_name is None:
            raw_name = f"{mall_price_dto.compayny_goods_cd}_mall_price_registration_{datetime.now().strftime('%Y%m%d')}_{count_rev}.xml"
            file_name = f"{self._PATH}/" + sanitize_filename(raw_name)

        root = ET.Element("SABANGNET_GOODS_REGI")
        self._create_product_header(root=root)
        for shop_code in self.SHOP_CODE:
            price = getattr(mall_price_dto, shop_code, None)
            self.create_body(
                root=root,
                shop_code=shop_code,
                compayny_goods_cd=mall_price_dto.compayny_goods_cd,
                price=price,
                mall_stock_rate=mall_stock_rate,
            )
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        # 파일 경로 객체 생성 및 디렉토리 생성
        file_path = Path(file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
            tree.write(f, encoding='EUC-KR', xml_declaration=False)

        return file_name
