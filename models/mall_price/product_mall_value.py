from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base

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

    # ((기본판매가 + (기본판매가 * 0.15)) 1000자리에서 반올림 후 - 100) + 3000
    shop0007: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0042: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0087: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0094: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0121: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0129: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0154: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0650: Mapped[int] = mapped_column(Integer, nullable=True)

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100) + 3000
    shop0029: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0189: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0322: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0444: Mapped[int] = mapped_column(Integer, nullable=True)

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100)
    shop0100: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0298: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0372: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # 기본판매가 + 3000
    shop0381: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0416: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0449: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0498: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0583: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0587: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0661: Mapped[int] = mapped_column(Integer, nullable=True)

    # 기본판매가 + 100
    shop0055: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0067: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0068: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0273: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0464: Mapped[int] = mapped_column(Integer, nullable=True)

    # 기본판매가
    shop0075: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0319: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0365: Mapped[int] = mapped_column(Integer, nullable=True)
    shop0387: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # 떠리몰 (기본판매가 + 3000 또는 기본판매가)
    shop0666: Mapped[int] = mapped_column(Integer, nullable=True)

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
        # 1. 기본판매가 계산
        shop0007 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0042 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0087 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0094 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0121 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0129 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0154 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)
        shop0650 = int(cls.__round_up(standard_price * 115 // 100) - 100 + 3000)

        shop0029 = int(cls.__round_up(standard_price * 105 // 100) - 100 + 3000)
        shop0189 = int(cls.__round_up(standard_price * 105 // 100) - 100 + 3000)
        shop0322 = int(cls.__round_up(standard_price * 105 // 100) - 100 + 3000)
        shop0444 = int(cls.__round_up(standard_price * 105 // 100) - 100 + 3000)

        shop0100 = int(cls.__round_up(standard_price * 105 // 100) - 100)
        shop0298 = int(cls.__round_up(standard_price * 105 // 100) - 100)
        shop0372 = int(cls.__round_up(standard_price * 105 // 100) - 100)

        shop0381 = int(standard_price + 3000)
        shop0416 = int(standard_price + 3000)
        shop0449 = int(standard_price + 3000)
        shop0498 = int(standard_price + 3000)
        shop0583 = int(standard_price + 3000)
        shop0587 = int(standard_price + 3000)
        shop0661 = int(standard_price + 3000)
        shop0666 = int(standard_price + 3000)

        shop0055 = int(standard_price + 100)
        shop0067 = int(standard_price + 100)
        shop0068 = int(standard_price + 100)
        shop0273 = int(standard_price + 100)
        shop0464 = int(standard_price + 100)

        shop0075 = int(standard_price)
        shop0319 = int(standard_price)
        shop0365 = int(standard_price)
        shop0387 = int(standard_price)

        return cls._create_instance(
            product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun,
            shop0007, shop0042, shop0087, shop0094, shop0121, shop0129, shop0154, shop0650,
            shop0029, shop0189, shop0322, shop0444, shop0100, shop0298, shop0372,
            shop0381, shop0416, shop0449, shop0498, shop0583, shop0587, shop0661,
            shop0055, shop0067, shop0068, shop0273, shop0464, shop0075, shop0319, shop0365, shop0387, shop0666,
            **kwargs
        )

    @classmethod
    def _build_one_plus_one_prices(cls, product_raw_data_id: int, standard_price: int, 
                                 product_nm: str, compayny_goods_cd: str, gubun: str, **kwargs) -> "ProductMallValue":
        """1+1 상품 가격 계산"""
        # 1+1 상품은 무료배송 기준으로 계산
        shop0007 = int(standard_price * 115 // 100)  # 기본+15% // GS Shop
        shop0042 = int(standard_price * 115 // 100)  # 텐바이텐
        shop0087 = int(standard_price * 115 // 100)  # 롯데홈쇼핑
        shop0094 = int(standard_price * 115 // 100)  # 무신사
        shop0121 = int(standard_price * 115 // 100)  # NS홈쇼핑
        shop0129 = int(standard_price * 115 // 100)  # CJ온스타일
        shop0154 = int(standard_price * 115 // 100)  # K쇼핑
        shop0650 = int(standard_price * 115 // 100)  # 홈&쇼핑

        shop0029 = int(standard_price * 105 // 100)  # 기본+5% // YES24
        shop0189 = int(standard_price * 105 // 100)  # 오늘의집
        shop0322 = int(standard_price * 105 // 100)  # 브랜디
        shop0444 = int(standard_price * 105 // 100)  # 카카오스타일

        shop0100 = int(standard_price * 105 // 100)  # 기본+5% // 신세계몰
        shop0298 = int(standard_price * 105 // 100)  # 기본+5% // Cafe24
        shop0372 = int(standard_price * 105 // 100)  # 롯데온

        shop0381 = int(standard_price)  # 에이블리
        shop0416 = int(standard_price)  # 아트박스
        shop0449 = int(standard_price)  # 카카오톡선물하기  
        shop0498 = int(standard_price)  # 올웨이즈
        shop0583 = int(standard_price)  # 토스쇼핑
        shop0587 = int(standard_price)  # AliExpress    
        shop0661 = int(standard_price)  # 떠리몰
        shop0666 = int(standard_price)  # 떠리몰

        shop0055 = int(standard_price + 100)  # 기본+100 // 스마트스토어
        shop0067 = int(standard_price + 100)  # ESM옥션
        shop0068 = int(standard_price + 100)  # ESM지마켓
        shop0273 = int(standard_price + 100)  # 카카오톡스토어
        shop0464 = int(standard_price + 100)  # 11번가

        shop0075 = int(standard_price)  # 쿠팡
        shop0319 = int(standard_price)  # 도매꾹
        shop0365 = int(standard_price)  # Grip
        shop0387 = int(standard_price)  # 하프클럽
        

        return cls._create_instance(
            product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun,
            shop0007, shop0042, shop0087, shop0094, shop0121, shop0129, shop0154, shop0650,
            shop0029, shop0189, shop0322, shop0444, shop0100, shop0298, shop0372,
            shop0381, shop0416, shop0449, shop0498, shop0583, shop0587, shop0661,
            shop0055, shop0067, shop0068, shop0273, shop0464, shop0075, shop0319, shop0365, shop0387, shop0666,
            **kwargs
        )

    @classmethod
    def _build_default_prices(cls, product_raw_data_id: int, standard_price: int, 
                            product_nm: str, compayny_goods_cd: str, gubun: str, **kwargs) -> "ProductMallValue":
        """기본 가격 계산"""
        # 모든 쇼핑몰에 기본가 적용
        default_price = int(standard_price)
        return cls._create_instance(
            product_raw_data_id, standard_price, product_nm, compayny_goods_cd, gubun,
            default_price, default_price, default_price, default_price, default_price, default_price, default_price, default_price,
            default_price, default_price, default_price, default_price, default_price, default_price, default_price,
            default_price, default_price, default_price, default_price, default_price, default_price, default_price,
            default_price, default_price, default_price, default_price, default_price, default_price, default_price, default_price, default_price,
            **kwargs
        )

    @classmethod
    def _create_instance(cls, product_raw_data_id: int, standard_price: int, product_nm: str, 
                        compayny_goods_cd: str, gubun: str,
                        shop0007, shop0042, shop0087, shop0094, shop0121, shop0129, shop0154, shop0650,
                        shop0029, shop0189, shop0322, shop0444, shop0100, shop0298, shop0372,
                        shop0381, shop0416, shop0449, shop0498, shop0583, shop0587, shop0661,
                        shop0055, shop0067, shop0068, shop0273, shop0464, shop0075, shop0319, shop0365, shop0387, shop0666,
                        **kwargs) -> "ProductMallValue":
        """인스턴스 생성"""
        return cls(
            test_product_raw_data_id=product_raw_data_id,
            standard_price=standard_price,
            product_nm=product_nm,
            compayny_goods_cd=compayny_goods_cd,
            gubun=gubun,
            shop0007=shop0007,
            shop0042=shop0042,
            shop0087=shop0087,
            shop0094=shop0094,
            shop0121=shop0121,
            shop0129=shop0129,
            shop0154=shop0154,
            shop0650=shop0650,
            shop0029=shop0029,
            shop0189=shop0189,
            shop0322=shop0322,
            shop0444=shop0444,
            shop0100=shop0100,
            shop0298=shop0298,
            shop0372=shop0372,
            shop0381=shop0381,
            shop0416=shop0416,
            shop0449=shop0449,
            shop0498=shop0498,
            shop0583=shop0583,
            shop0587=shop0587,
            shop0661=shop0661,
            shop0055=shop0055,
            shop0067=shop0067,
            shop0068=shop0068,
            shop0273=shop0273,
            shop0464=shop0464,
            shop0075=shop0075,
            shop0319=shop0319,
            shop0365=shop0365,
            shop0387=shop0387,
            shop0666=shop0666,
            **kwargs
        )
    
    @staticmethod
    def __round_up(price: int) -> int:
        return int(((price + 999) // 1000) * 1000)
