from tests.mocks.mock_mall_info import MALL_INFO
from tests.mocks.mock_mall_price import MALL_PRICE
from tests.mocks.mock_macro_info import MACRO_INFO
from tests.mocks.mock_one_one_price import ONE_ONE_PRICE
from tests.mocks.mock_receive_orders import RECEIVE_ORDERS
from tests.mocks.mock_count_executing import COUNT_EXECUTING
from tests.mocks.mock_down_form_orders import DOWN_FORM_ORDERS
from tests.mocks.mock_test_product_raw_data import TEST_PRODUCT_RAW_DATA


MOCK_TABLES = {
    "mall_info": MALL_INFO,
    "mall_price": MALL_PRICE,
    "macro_info": MACRO_INFO,
    "one_one_price": ONE_ONE_PRICE,
    "receive_orders": RECEIVE_ORDERS,
    "count_executing": COUNT_EXECUTING,
    "down_form_orders": DOWN_FORM_ORDERS,
    "product_raw_data": TEST_PRODUCT_RAW_DATA,
}


__all__ = [
    "MOCK_TABLES",
]