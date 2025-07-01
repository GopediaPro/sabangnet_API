from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import Base

class MallPrice(Base):
    __tablename__ = "mall_price"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    products_nm: Mapped[str] = mapped_column(String(100), nullable=False)
    standard_price: Mapped[int] = mapped_column(Integer)
    
    product_registration_raw_data_id: Mapped[int] = mapped_column(
        ForeignKey("product_registration_raw_data.id",
                   name="product_registration_raw_data", ondelete="CASCADE"),
        nullable=False
    )

    # ((기본판매가 + (기본판매가 * 0.15)) 1000자리에서 반올림 후 - 100) + 3000
    shop0007: Mapped[int] = mapped_column(Integer)
    shop0042: Mapped[int] = mapped_column(Integer)
    shop0087: Mapped[int] = mapped_column(Integer)
    shop0094: Mapped[int] = mapped_column(Integer)
    shop0121: Mapped[int] = mapped_column(Integer)
    shop0129: Mapped[int] = mapped_column(Integer)
    shop0154: Mapped[int] = mapped_column(Integer)
    shop0650: Mapped[int] = mapped_column(Integer)

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100) + 3000
    shop0029: Mapped[int] = mapped_column(Integer)
    shop0189: Mapped[int] = mapped_column(Integer)
    shop0322: Mapped[int] = mapped_column(Integer)
    shop0444: Mapped[int] = mapped_column(Integer)

    # ((기본판매가 + (기본판매가 * 0.05)) 1000자리에서 반올림 후 - 100)
    shop0100: Mapped[int] = mapped_column(Integer)
    shop0298: Mapped[int] = mapped_column(Integer)
    shop0372: Mapped[int] = mapped_column(Integer)
    
    # 기본판매가 + 3000
    shop0381: Mapped[int] = mapped_column(Integer)
    shop0416: Mapped[int] = mapped_column(Integer)
    shop0449: Mapped[int] = mapped_column(Integer)
    shop0498: Mapped[int] = mapped_column(Integer)
    shop0583: Mapped[int] = mapped_column(Integer)
    shop0587: Mapped[int] = mapped_column(Integer)
    shop0661: Mapped[int] = mapped_column(Integer)

    # 기본판매가 + 100
    shop0055: Mapped[int] = mapped_column(Integer)
    shop0067: Mapped[int] = mapped_column(Integer)
    shop0068: Mapped[int] = mapped_column(Integer)
    shop0273: Mapped[int] = mapped_column(Integer)
    shop0464: Mapped[int] = mapped_column(Integer)

    # 기본판매가
    shop0075: Mapped[int] = mapped_column(Integer)
    shop0319: Mapped[int] = mapped_column(Integer)
    shop0365: Mapped[int] = mapped_column(Integer)
    shop0387: Mapped[int] = mapped_column(Integer)

    @classmethod
    def builder(cls, product_registration_raw_data_id: int, standard_price: int, products_nm: str) -> "MallPrice":
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

        shop0055 = int(standard_price + 100)
        shop0067 = int(standard_price + 100)
        shop0068 = int(standard_price + 100)
        shop0273 = int(standard_price + 100)
        shop0464 = int(standard_price + 100)

        shop0075 = int(standard_price)
        shop0319 = int(standard_price)
        shop0365 = int(standard_price)
        shop0387 = int(standard_price)

        return cls(
            product_registration_raw_data_id=product_registration_raw_data_id,
            standard_price=standard_price,
            products_nm=products_nm,
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
        )
    
    @staticmethod
    def __round_up(price: int) -> int:
        return int(((price + 999) // 1000) * 1000)