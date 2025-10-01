from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base
from typing import Optional

class ProductMallValue(Base):
    __tablename__ = "product_mall_value"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_nm: Mapped[str] = mapped_column(String(100), nullable=True)
    standard_price: Mapped[int] = mapped_column(Integer, nullable=True)
    compayny_goods_cd: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # ForeignKey 제거하고 일반 Integer 필드로 변경
    test_product_raw_data_id: Mapped[int] = mapped_column(Integer, nullable=True)

    # 새로 추가할 필드들 (모두 String, nullable=True)
    batch_id: Mapped[str] = mapped_column(String(100), nullable=True)
    gubun: Mapped[str] = mapped_column(String(50), nullable=True)
    mall_prod_name: Mapped[str] = mapped_column(String(200), nullable=True)
    mall_prop1_cd: Mapped[str] = mapped_column(String(100), nullable=True)
    buinf_id3: Mapped[str] = mapped_column(String(100), nullable=True)
    mall_stock_rate: Mapped[str] = mapped_column(String(50), nullable=True)
    certno: Mapped[str] = mapped_column(String(100), nullable=True)
    issuedate: Mapped[str] = mapped_column(String(50), nullable=True)
    certdate: Mapped[str] = mapped_column(String(50), nullable=True)
    avlst_dm: Mapped[str] = mapped_column(String(50), nullable=True)
    avled_dm: Mapped[str] = mapped_column(String(50), nullable=True)
    cert_agency: Mapped[str] = mapped_column(String(100), nullable=True)
    certfield: Mapped[str] = mapped_column(String(100), nullable=True)

    # JSONB 컬럼으로 모든 shop 정보 저장
    shops: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, server_default='{}')

    # 1+1 상품명 패턴 매핑 (향후 mall_info 테이블로 이동 예정)
    SHOP_1PLUS1_NAME_PATTERNS = {
        "shop0007": "2개세트 {product_nm}",
        "shop0055": "2개세트 {product_nm}",
        "shop0075": "2개세트 {product_nm}",
        "shop0087": "2개세트 {product_nm}",
        "shop0121": "2개세트 {product_nm}",
        "shop0129": "2개세트 {product_nm}",
        "shop0381": "2개세트 {product_nm}",
        "shop0464": "[1개+1개] {product_nm}",  # 특별 패턴
        "shop0650": "2개세트 {product_nm}",
    }

    @classmethod
    def _get_1plus1_product_name(cls, shop_code: str, product_nm: str, compayny_goods_cd: str) -> str:
        """1+1 상품명 생성"""
        if shop_code in cls.SHOP_1PLUS1_NAME_PATTERNS:
            pattern = cls.SHOP_1PLUS1_NAME_PATTERNS[shop_code]
            return pattern.format(product_nm=product_nm)
        else:
            # 패턴에 없는 shop들은 원본 product_nm 그대로 사용
            return compayny_goods_cd

    @classmethod
    def builder(cls, product_raw_data_id: int, standard_price: int, product_nm: str, 
                compayny_goods_cd: str, gubun: str, **kwargs) -> "ProductMallValue":
        """
        gubun에 따라 다른 가격 계산 로직 적용
        """
        if gubun in ["전문몰", "마스터"]:
            # 단품상품 가격 계산 (기존 MallPrice 로직)
            return cls._build_single_product_prices(
                product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun, **kwargs
            )
        elif gubun == "1+1":
            # 1+1 상품 가격 계산
            return cls._build_one_plus_one_prices(
                product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun, **kwargs
            )
        else:
            # 기본 가격 계산
            return cls._build_default_prices(
                product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun, **kwargs
            )

    @classmethod
    def _build_single_product_prices(cls, product_raw_data_id: int, standard_price: int, 
                                   product_nm: str, compayny_goods_cd: str, gubun: str, **kwargs) -> "ProductMallValue":
        """단품상품 가격 계산 (전문가/마스터)"""
        shops = {}
        
        # ((기본판매가 + (기본판매가 * 0.15)) 1000자리에서 반올림 후 - 100) + 3000
        price_115_roundup_minus100_plus3000 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        for shop_code in ["shop0007", "shop0042", "shop0087", "shop0094", "shop0121", "shop0129", "shop0154", "shop0650"]:
            shops[shop_code] = {
                "mall_price": price_115_roundup_minus100_plus3000,
                "product_nm": product_nm
            }

        # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100) + 3000
        price_105_roundup_minus100_plus3000 = int(cls.__round_up(standard_price * 105 // 100) - 100 + 3000)
        for shop_code in ["shop0029", "shop0189", "shop0322", "shop0444"]:
            shops[shop_code] = {
                "mall_price": price_105_roundup_minus100_plus3000,
                "product_nm": product_nm
            }

        # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100)
        price_105_roundup_minus100 = int(cls.__round_up(standard_price * 105 // 100) - 100)
        for shop_code in ["shop0100", "shop0298", "shop0372"]:
            shops[shop_code] = {
                "mall_price": price_105_roundup_minus100,
                "product_nm": product_nm
            }

        # 기본판매가 + 3000
        price_plus3000 = int(standard_price + 3000)
        for shop_code in ["shop0381", "shop0416", "shop0449", "shop0498", "shop0583", "shop0587", "shop0661", "shop0666"]:
            shops[shop_code] = {
                "mall_price": price_plus3000,
                "product_nm": product_nm
            }

        # 기본판매가 + 100
        price_plus100 = int(standard_price + 100)
        for shop_code in ["shop0055", "shop0067", "shop0068", "shop0273", "shop0464"]:
            shops[shop_code] = {
                "mall_price": price_plus100,
                "product_nm": product_nm
            }

        # 기본판매가
        for shop_code in ["shop0075", "shop0319", "shop0365", "shop0387"]:
            shops[shop_code] = {
                "mall_price": standard_price,
                "product_nm": product_nm
            }

        return cls._create_instance(
            product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun, shops, **kwargs
        )

    @classmethod
    def _build_one_plus_one_prices(cls, product_raw_data_id: int, standard_price: int, 
                                 product_nm: str, compayny_goods_cd: str, gubun: str, **kwargs) -> "ProductMallValue":
        """1+1 상품 가격 계산"""
        shops = {}
        
        # 1+1 상품은 무료배송 기준으로 계산
        # 기본+15% // GS Shop, 텐바이텐, 롯데홈쇼핑, 무신사, NS홈쇼핑, CJ온스타일, K쇼핑, 홈&쇼핑
        price_115_percent = int(standard_price * 115 // 100)
        for shop_code in ["shop0007", "shop0042", "shop0087", "shop0094", "shop0121", "shop0129", "shop0154", "shop0650"]:
            shops[shop_code] = {
                "mall_price": price_115_percent,
                "product_nm": cls._get_1plus1_product_name(shop_code, product_nm, compayny_goods_cd)
            }

        # 기본+5% // YES24, 오늘의집, 브랜디, 카카오스타일
        price_105_percent = int(standard_price * 105 // 100)
        for shop_code in ["shop0029", "shop0189", "shop0322", "shop0444"]:
            shops[shop_code] = {
                "mall_price": price_105_percent,
                "product_nm": cls._get_1plus1_product_name(shop_code, product_nm, compayny_goods_cd)
            }

        # 기본+5% // 신세계몰, Cafe24, 롯데온
        for shop_code in ["shop0100", "shop0298", "shop0372"]:
            shops[shop_code] = {
                "mall_price": price_105_percent,
                "product_nm": cls._get_1plus1_product_name(shop_code, product_nm, compayny_goods_cd)
            }

        # 기본가 // 에이블리, 아트박스, 카카오톡선물하기, 올웨이즈, 토스쇼핑, AliExpress, 떠리몰
        for shop_code in ["shop0381", "shop0416", "shop0449", "shop0498", "shop0583", "shop0587", "shop0661", "shop0666"]:
            shops[shop_code] = {
                "mall_price": standard_price,
                "product_nm": cls._get_1plus1_product_name(shop_code, product_nm, compayny_goods_cd)
            }

        # 기본+100 // 스마트스토어, ESM옥션, ESM지마켓, 카카오톡스토어, 11번가
        price_plus100 = int(standard_price + 100)
        for shop_code in ["shop0055", "shop0067", "shop0068", "shop0273", "shop0464"]:
            shops[shop_code] = {
                "mall_price": price_plus100,
                "product_nm": cls._get_1plus1_product_name(shop_code, product_nm, compayny_goods_cd)
            }

        # 기본가 // 쿠팡, 도매꾹, Grip, 하프클럽
        for shop_code in ["shop0075", "shop0319", "shop0365", "shop0387"]:
            shops[shop_code] = {
                "mall_price": standard_price,
                "product_nm": cls._get_1plus1_product_name(shop_code, product_nm, compayny_goods_cd)
            }

        return cls._create_instance(
            product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun, shops, **kwargs
        )

    @classmethod
    def _build_default_prices(cls, product_raw_data_id: int, standard_price: int, 
                            product_nm: str, compayny_goods_cd: str, gubun: str, **kwargs) -> "ProductMallValue":
        """기본 가격 계산"""
        shops = {}
        
        # 모든 쇼핑몰에 기본가 적용
        all_shop_codes = [
            "shop0007", "shop0042", "shop0087", "shop0094", "shop0121", "shop0129", "shop0154", "shop0650",
            "shop0029", "shop0189", "shop0322", "shop0444", "shop0100", "shop0298", "shop0372",
            "shop0381", "shop0416", "shop0449", "shop0498", "shop0583", "shop0587", "shop0661", "shop0666",
            "shop0055", "shop0067", "shop0068", "shop0273", "shop0464", "shop0075", "shop0319", "shop0365", "shop0387"
        ]
        
        for shop_code in all_shop_codes:
            shops[shop_code] = {
                "mall_price": standard_price,
                "product_nm": product_nm
            }
        
        return cls._create_instance(
            product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun, shops, **kwargs
        )

    @classmethod
    def _create_instance(cls, product_raw_data_id: int, standard_price: int, product_nm: str, 
                        compayny_goods_cd: str, gubun: str, shops: dict, **kwargs) -> "ProductMallValue":
        """인스턴스 생성"""
        return cls(
            test_product_raw_data_id=product_raw_data_id,
            standard_price=standard_price,
            product_nm=product_nm,
            compayny_goods_cd=compayny_goods_cd,
            gubun=gubun,
            shops=shops,
            **kwargs
        )
    
    @staticmethod
    def __round_up(price: int) -> int:
        return int(((price + 999) // 1000) * 1000)
