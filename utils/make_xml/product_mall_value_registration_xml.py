from utils.make_xml.sabangnet_xml import SabangnetXml
from schemas.mall_price.product_mall_value_dto import ProductMallValueDto
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from utils.make_xml.file_name_for_xml import sanitize_filename

class ProductMallValueRegistrationXml(SabangnetXml):

    _PATH = "./files/xml/request/product_mall_value"

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

    def create_body(self, root, shop_code: str, compayny_goods_cd: str, price: int, 
                   mall_stock_rate: str = None, mall_prod_name: str = None, 
                   mall_prop1_cd: str = None, certno: str = None, 
                   issuedate: str = None, certdate: str = None,
                   avlst_dm: str = None, avled_dm: str = None,
                   cert_agency: str = None, certfield: str = None):

        data = ET.SubElement(root, "DATA")

        shop_code_element = ET.SubElement(data, "MALL_CODE")
        shop_code_element.text = shop_code

        compayny_goods_cd_element = ET.SubElement(data, "COMPAYNY_GOODS_CD")
        compayny_goods_cd_element.text = compayny_goods_cd

        mall_price_element = ET.SubElement(data, "MALL_GOODS_PRICE")
        mall_price_element.text = str(price)
        
        if mall_stock_rate: # 재고율 있을 경우
            mall_stock_rate_element = ET.SubElement(data, "MALL_GOODS_STOCK_RATE")
            mall_stock_rate_element.text = mall_stock_rate

        # 새로 추가된 필드들
        if mall_prod_name:
            mall_prod_name_element = ET.SubElement(data, "MALL_PROD_NAME")
            mall_prod_name_element.text = mall_prod_name

        if mall_prop1_cd:
            mall_prop1_cd_element = ET.SubElement(data, "MALL_PROP1_CD")
            mall_prop1_cd_element.text = mall_prop1_cd

        if certno:
            certno_element = ET.SubElement(data, "CERTNO")
            certno_element.text = certno

        if issuedate:
            issuedate_element = ET.SubElement(data, "ISSUEDATE")
            issuedate_element.text = issuedate

        if certdate:
            certdate_element = ET.SubElement(data, "CERTDATE")
            certdate_element.text = certdate

        if avlst_dm:
            avlst_dm_element = ET.SubElement(data, "AVLST_DM")
            avlst_dm_element.text = avlst_dm

        if avled_dm:
            avled_dm_element = ET.SubElement(data, "AVLED_DM")
            avled_dm_element.text = avled_dm

        if cert_agency:
            cert_agency_element = ET.SubElement(data, "CERT_AGENCY")
            cert_agency_element.text = cert_agency

        if certfield:
            certfield_element = ET.SubElement(data, "CERTFIELD")
            certfield_element.text = certfield

        return data
        
    def make_product_mall_value_registration_xml(self, product_mall_value_dto: ProductMallValueDto, 
                                               count_rev: int, file_name=None):
        """ProductMallValue 등록용 XML 생성"""
        
        from utils.logs.sabangnet_logger import get_logger
        logger = get_logger(__name__)
        
        # 파일명에서 공백과 특수문자 제거
        safe_company_goods_cd = product_mall_value_dto.compayny_goods_cd.replace(' ', '_').replace('+', 'plus').replace('-', '_')
        raw_name = f"{safe_company_goods_cd}_product_mall_value_registration_{datetime.now().strftime('%Y%m%d')}_{count_rev}.xml"
        file_name = f"{self._PATH}/" + sanitize_filename(raw_name)

        logger.info(f"XML 생성 시작 - 상품코드: {product_mall_value_dto.compayny_goods_cd}, 파일명: {file_name}")

        root = ET.Element("SABANGNET_GOODS_REGI")
        self._create_product_header(root=root)
        
        processed_shops = 0
        for shop_code in self.SHOP_CODE:
            price = getattr(product_mall_value_dto, shop_code, None)
            if price is not None:
                logger.debug(f"상점 {shop_code} 처리 - 가격: {price}")
                self.create_body(
                    root=root,
                    shop_code=shop_code,
                    compayny_goods_cd=product_mall_value_dto.compayny_goods_cd,
                    price=price,
                    mall_stock_rate=product_mall_value_dto.mall_stock_rate,
                    mall_prod_name=product_mall_value_dto.mall_prod_name,
                    mall_prop1_cd=product_mall_value_dto.mall_prop1_cd,
                    certno=product_mall_value_dto.certno,
                    issuedate=product_mall_value_dto.issuedate,
                    certdate=product_mall_value_dto.certdate,
                    avlst_dm=product_mall_value_dto.avlst_dm,
                    avled_dm=product_mall_value_dto.avled_dm,
                    cert_agency=product_mall_value_dto.cert_agency,
                    certfield=product_mall_value_dto.certfield,
                )
                processed_shops += 1
        
        logger.info(f"XML 생성 완료 - 처리된 상점 수: {processed_shops}")
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)

        # 파일 경로 객체 생성 및 디렉토리 생성
        file_path = Path(file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write('<?xml version="1.0" encoding="euc-kr"?>\n'.encode("EUC-KR"))
            tree.write(f, encoding='EUC-KR', xml_declaration=False)

        return file_name
