import pandas as pd
from utils.macros.ERP.utils import macro_basic_process, star_average_process
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


class GAERPMacroV3:
    def __init__(self, row_datas, is_star: bool = False):
        self.row_datas = row_datas
        self.is_star = is_star

    def gauc_erp_macro_run(self):
        logger.info(f"[START]gauc_erp_macro_run")
        df = pd.DataFrame(self.row_datas, dtype=object)

        # 정렬
        df.sort_values(
            by=['fld_dsp', 'receive_name', 'mall_order_id'],
            ascending=[True, True, False],
            inplace=True
        )

        # 기본처리
        df = macro_basic_process(df)

        # 장바구니 중복값 배송비 제거
        df = self._process_dupl_basket(df)

        # 숫자 타입 변환
        df['expected_payout'] = pd.to_numeric(df['expected_payout'], errors='coerce').fillna(0)
        df['service_fee'] = pd.to_numeric(df['service_fee'], errors='coerce').fillna(0)
        df['delv_cost'] = pd.to_numeric(df['delv_cost'], errors='coerce').fillna(0)

        # 금액 계산
        df['etc_cost'] = df['expected_payout'] + df['service_fee'] + df['delv_cost']
        df['etc_cost'] = df['etc_cost'].astype(int).astype(str)

        # 스타배송 평균 배송비 적용
        if self.is_star:
            df = star_average_process(df)

        macro_run_datas = df.to_dict(orient='records')
        logger.info(f"[END]gauc_erp_macro_run")
        return macro_run_datas

    def _process_dupl_basket(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        장바구니 중복값 배송비 제거
        """
        # 특정 키값 생성
        df['site_basket'] = df['fld_dsp'] + \
            '_' + df['mall_order_id'].astype(str)

        # 배송비 유효성 체크
        valid_delivery = (df['delv_cost'] != 0) & (
            df['delv_cost'].notna()) & (df['delv_cost'] != "")

        # 그룹별 첫 번째와 마지막 행 인덱스 찾기
        grouped = df.groupby('site_basket')
        first_idx = df[valid_delivery].groupby('site_basket').head(1).index
        last_idx = grouped.tail(1).index

        # 배송비 매핑 딕셔너리 생성
        delivery_mapping = df.loc[first_idx].set_index('site_basket')[
            'delv_cost'].to_dict()

        # 마지막 행에만 배송비 적용
        mask = df.index.isin(last_idx)
        df.loc[mask, 'delv_cost'] = df.loc[mask, 'site_basket'].map(
            delivery_mapping).fillna(0)

        df.drop('site_basket', axis=1, inplace=True)
        return df


def gauc_erp_macro_run(row_datas: list[dict], is_star: bool = False) -> list[dict]:
    return GAERPMacroV3(row_datas, is_star).gauc_erp_macro_run()
