from typing import Any
from decimal import Decimal


ONE_ONE_PRICE: list[dict[str, Any]] = [
    {
        "id": 1,
        "test_product_raw_data_id": 1,
        "product_nm": "테스트상품1",
        "compayny_goods_cd": "GOODS001",
        "standard_price": 7900,
        "one_one_price": Decimal("17900"),
        "shop0007": Decimal("20900"),  # group_115: 115%
        "shop0042": Decimal("20900"),  # group_115: 115%
        "shop0087": Decimal("20900"),  # group_115: 115%
        "shop0094": Decimal("20900"),  # group_115: 115%
        "shop0121": Decimal("20900"),  # group_115: 115%
        "shop0129": Decimal("20900"),  # group_115: 115%
        "shop0154": Decimal("20900"),  # group_115: 115%
        "shop0650": Decimal("20900"),  # group_115: 115%
        "shop0029": Decimal("18900"),  # group_105: 105%
        "shop0189": Decimal("18900"),  # group_105: 105%
        "shop0322": Decimal("18900"),  # group_105: 105%
        "shop0444": Decimal("18900"),  # group_105: 105%
        "shop0100": Decimal("18900"),  # group_105: 105%
        "shop0298": Decimal("18900"),  # group_105: 105%
        "shop0372": Decimal("18900"),  # group_105: 105%
        "shop0381": Decimal("17900"),  # group_same: 그대로
        "shop0416": Decimal("17900"),  # group_same: 그대로
        "shop0449": Decimal("17900"),  # group_same: 그대로
        "shop0498": Decimal("17900"),  # group_same: 그대로
        "shop0583": Decimal("17900"),  # group_same: 그대로
        "shop0587": Decimal("17900"),  # group_same: 그대로
        "shop0661": Decimal("17900"),  # group_same: 그대로
        "shop0075": Decimal("17900"),  # group_same: 그대로
        "shop0319": Decimal("17900"),  # group_same: 그대로
        "shop0365": Decimal("17900"),  # group_same: 그대로
        "shop0387": Decimal("17900"),  # group_same: 그대로
        "shop0055": Decimal("18000"),  # group_plus100: +100
        "shop0067": Decimal("18000"),  # group_plus100: +100
        "shop0068": Decimal("18000"),  # group_plus100: +100
        "shop0273": Decimal("18000"),  # group_plus100: +100
        "shop0464": Decimal("18000")   # group_plus100: +100
    },
    {
        "id": 2,
        "test_product_raw_data_id": 2,
        "product_nm": "테스트상품2",
        "compayny_goods_cd": "GOODS002",
        "standard_price": 20000,
        "one_one_price": Decimal("40900"),
        "shop0007": Decimal("46900"),  # group_115: 115%
        "shop0042": Decimal("46900"),  # group_115: 115%
        "shop0087": Decimal("46900"),  # group_115: 115%
        "shop0094": Decimal("46900"),  # group_115: 115%
        "shop0121": Decimal("46900"),  # group_115: 115%
        "shop0129": Decimal("46900"),  # group_115: 115%
        "shop0154": Decimal("46900"),  # group_115: 115%
        "shop0650": Decimal("46900"),  # group_115: 115%
        "shop0029": Decimal("42900"),  # group_105: 105%
        "shop0189": Decimal("42900"),  # group_105: 105%
        "shop0322": Decimal("42900"),  # group_105: 105%
        "shop0444": Decimal("42900"),  # group_105: 105%
        "shop0100": Decimal("42900"),  # group_105: 105%
        "shop0298": Decimal("42900"),  # group_105: 105%
        "shop0372": Decimal("42900"),  # group_105: 105%
        "shop0381": Decimal("40900"),  # group_same: 그대로
        "shop0416": Decimal("40900"),  # group_same: 그대로
        "shop0449": Decimal("40900"),  # group_same: 그대로
        "shop0498": Decimal("40900"),  # group_same: 그대로
        "shop0583": Decimal("40900"),  # group_same: 그대로
        "shop0587": Decimal("40900"),  # group_same: 그대로
        "shop0661": Decimal("40900"),  # group_same: 그대로
        "shop0075": Decimal("40900"),  # group_same: 그대로
        "shop0319": Decimal("40900"),  # group_same: 그대로
        "shop0365": Decimal("40900"),  # group_same: 그대로
        "shop0387": Decimal("40900"),  # group_same: 그대로
        "shop0055": Decimal("41000"),  # group_plus100: +100
        "shop0067": Decimal("41000"),  # group_plus100: +100
        "shop0068": Decimal("41000"),  # group_plus100: +100
        "shop0273": Decimal("41000"),  # group_plus100: +100
        "shop0464": Decimal("41000")   # group_plus100: +100
    }
]