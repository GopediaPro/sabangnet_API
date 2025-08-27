from utils.logs.sabangnet_logger import get_logger
import pandas as pd

logger = get_logger(__name__)


class BundleUtilsV3:
    def __init__(self, row_datas: list[dict]):
        self.df = pd.DataFrame(row_datas, dtype=object)

    def run_bundle_macro(self):
        logger.info(f"[START]run_bundle_macro_data")
        self.df['bundle_key'] = self.df['receive_zipcode'] + \
            self.df['receive_addr'] + self.df['receive_name']

        all_columns = {
            'order_id': 'max',  # 주문 번호
            'item_name': self.reversed_join(' + '),  # 제품명
            'service_fee': 'max',  # 서비스이용료
            'pay_cost': 'sum',  # 금액[배송비미포함]
            'delv_cost': 'max',
            'idx': self.reversed_join('/'),  # 사방넷주문번호
            'product_name': self.reversed_join(' / '),  # 수집상품명
            'mall_product_id': self.reversed_join('/'),  # 상품번호
            'sku_value': self.reversed_join('/'),  # 수집옵션
            'sale_cnt': self.sum_to_str(),  # 수량
            'expected_payout': 'max',  # 정산예정금액
            'delv_msg': self.reversed_join('/'),  # 배송메시지
            'etc_cost': self.sum_to_str(),  # 금액(이미 ERP 매크로를 통해 계산된 값)

            # 나머지 컬럼
            'seq': 'first',
            'fld_dsp': 'first',
            'process_dt': 'first',
            'form_name': 'first',
            'receive_name': 'first',
            'receive_addr': 'first',
            'receive_zipcode': 'first',
            'receive_cel': 'first',
            'receive_tel': 'first',
            'delivery_payment_type': 'first',
            'invoice_no': 'first',
            'location_nm': 'first',
            'order_etc_7': 'first',
            'product_id': 'first',
            'free_gift': 'first',
            'work_status': 'first',
            'mall_order_id': 'first'
        }
        agg_dict = {col: func for col, func in all_columns.items()
                    if col in self.df.columns}
        self.df = self.df.groupby('bundle_key', as_index=False).agg(agg_dict)
        self.df.drop('bundle_key', axis=1, inplace=True)

        run_bundle_macro_data = self.df.to_dict(orient='records')
        logger.info(f"[END]run_bundle_macro_data")
        return run_bundle_macro_data

    def reversed_join(self, target_str: str) -> str:
        """역순으로 join"""
        return lambda x: target_str.join(filter(None, x[::-1]))

    def sum_to_str(self) -> str:
        """정수 합계 문자열로 반환"""
        return lambda x: str(sum(int(val) for val in x if val is not None))
