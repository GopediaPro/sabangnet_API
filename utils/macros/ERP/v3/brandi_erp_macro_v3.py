import pandas as pd
from utils.macros.ERP.utils import macro_basic_process, star_average_process
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class BrandiErpMacroV3:
    def __init__(self, row_datas, is_star: bool = False):
        self.row_datas = row_datas
        self.is_star = is_star

    def brandi_erp_macro_run(self):
        logger.info(f"[START]brandi_erp_macro_run")
        df = pd.DataFrame(self.row_datas, dtype=object)

        # 정렬
        df.sort_values(by=["receive_name"], inplace=True)

        # 기본처리
        df = macro_basic_process(df)

        # 금액 계산
        df['etc_cost'] = df['service_fee'].fillna(0) + df['delv_cost'].fillna(0)
        df['etc_cost'] = df['etc_cost'].astype(str)

        # 스타배송 평균 배송비 적용
        if self.is_star:
            df = star_average_process(df)

        macro_run_datas = df.to_dict(orient='records')

        logger.info(f"[END]brandi_erp_macro_run")
        return macro_run_datas

def brandi_erp_macro_run(row_datas: list[dict], is_star: bool = False) -> list[dict]:
    return BrandiErpMacroV3(row_datas, is_star).brandi_erp_macro_run()