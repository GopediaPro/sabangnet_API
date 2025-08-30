import pandas as pd
from utils.macros.ERP.utils import macro_basic_process, star_average_process
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)

class ERPEtcSiteMacroV3:
    def __init__(self, row_datas, is_star: bool = False):
        self.row_datas = row_datas
        self.is_star = is_star

    def etc_site_macro_run(self):
        logger.info(f"[START]etc_site_macro_run")
        df = pd.DataFrame(self.row_datas, dtype=object)

        
        # 기본처리
        df = macro_basic_process(df)

        # 정렬
        df.sort_values(by=["fld_dsp", "receive_name", "order_id", "product_name"], 
                       ascending=[True, True, True, True], inplace=True)
        
        df = self._overlap_by_site_column(df)
        df = self._toss_process_column(df)

        # 숫자 타입 변환
        df['expected_payout'] = pd.to_numeric(df['expected_payout'], errors='coerce')
        df['service_fee'] = pd.to_numeric(df['service_fee'], errors='coerce')
        df['delv_cost'] = pd.to_numeric(df['delv_cost'], errors='coerce')
        
        # 금액 계산
        df['etc_cost'] = df['expected_payout'].fillna(
            0) + df['service_fee'].fillna(0) + df['delv_cost'].fillna(0)
        df['etc_cost'] = df['etc_cost'].astype(int).astype(str)

        # 스타배송 평균 배송비 적용
        if self.is_star:
            df = star_average_process(df)

        macro_run_datas = df.to_dict(orient='records')
        logger.info(f"[END]etc_site_macro_run")
        return macro_run_datas
    
    def _overlap_by_site_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        각 사이트별 중복 주문 처리 
        """
        
        # 오늘의집: 항상 0
        df.loc[df['fld_dsp'].str.contains('오늘의집', na=False), 'fld_dsp'] = 0
        
        # 톡스토어, 롯데온, 보리보리, 스마트스토어: 중복 체크
        sites_to_check = ['톡스토어', '롯데온', '보리보리', '스마트스토어']
        
        for site in sites_to_check:
            site_mask = df['fld_dsp'].str.contains(site, na=False)
            if site_mask.any():
                # 해당 사이트의 데이터에서 E 컬럼 기준 중복 체크
                site_df = df[site_mask]
                duplicates = site_df['order_id'].astype(str).str.strip().duplicated(keep='first')
                
                # 중복된 행의 V 값을 0으로 설정
                duplicate_indices = site_df[duplicates].index
                df.loc[duplicate_indices, 'fld_dsp'] = 0
        return df
    
    def _toss_process_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        토스 주문 처리
        """
        # 토스 주문 마스크
        toss_mask = df['fld_dsp'].str.contains('토스', na=False)
        
        if toss_mask.any():
            # 토스주문 배송비 0으로 설정
            df.loc[toss_mask, 'delv_cost'] = 0
            
            # 토스 주문 정보 수집
            toss_orders = df[toss_mask].copy()
            
            # 주문번호)와 금액[배송비미포함] 처리
            toss_orders['order_id'] = toss_orders['order_id'].astype(str).str.strip()
            toss_orders['expected_payout'] = pd.to_numeric(toss_orders['expected_payout'], errors='coerce').fillna(0)
            
            # 주문번호 별로 금액 합계 및 첫 번째 행 인덱스 수집
            order_summary = toss_orders.groupby('order_id').agg({
                'expected_payout': 'sum',
                'index': 'first'
            }).reset_index()
            
            # 30000원 이하인 주문 찾기
            low_amount_orders = order_summary[order_summary['expected_payout'] <= 30000]
            
            # 해당 행들의 배송비를 3000으로 설정
            for _, row in low_amount_orders.iterrows():
                first_row_idx = row['index']
                df.loc[first_row_idx, 'delv_cost'] = 3000
        return df

    def _order_num_by_site_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        사이트별 주문번호 처리 (DataFrame 기반) - 벡터화 연산 사용
        """
        site_list = ["에이블리", "오늘의집", "쿠팡", "텐바이텐",
                    "NS홈쇼핑", "그립", "보리보리", "카카오선물하기", "톡스토어", "토스"]
        
        # B 컬럼에서 해당 사이트들이 포함된 행 찾기
        site_mask = df['fld_dsp'].str.contains('|'.join(site_list), na=False)
        
        if site_mask.any():
            # B 컬럼을 문자열로 변환
            df.loc[site_mask, 'fld_dsp'] = df.loc[site_mask, 'fld_dsp'].astype(str)
            
            # 숫자 패턴 매칭 (소수점 포함)
            numeric_mask = df.loc[site_mask, 'B'].str.match(r'^\d+\.?\d*$')
            
            # 숫자인 값들을 정수로 변환
            numeric_indices = df[site_mask][numeric_mask].index
            df.loc[numeric_indices, 'B'] = df.loc[numeric_indices, 'B'].astype(float).astype(int)
        
        return df
    
def etc_site_macro_run(row_datas: list[dict], is_star: bool = False) -> list[dict]:
    return ERPEtcSiteMacroV3(row_datas, is_star).etc_site_macro_run()