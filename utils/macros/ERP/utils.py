from utils.logs.sabangnet_logger import get_logger
import pandas as pd
logger = get_logger(__name__)


def average_duplicate_order_address_amounts(ws):
    """
    E셀(주문번호)과 J셀(수취인주소)이 같은 값들의 D셀(금액)을 평균내는 메서드

    Args:
        ws: openpyxl의 worksheet 객체
    """
    # 주문번호와 수취인주소 조합으로 그룹화
    duplicate_groups = {}

    for row in range(2, ws.max_row + 1):
        order_number = str(ws[f"E{row}"].value).strip()
        address = str(ws[f"J{row}"].value).strip()
        amount = ws[f"D{row}"].value

        # 빈 값이 아닌 경우에만 처리
        if order_number and order_number != "None" and address and address != "None":
            key = f"{order_number}_{address}"

            if key not in duplicate_groups:
                duplicate_groups[key] = []

            duplicate_groups[key].append({
                'row': row,
                'amount': int(amount) if amount is not None else 0
            })

    # 2개 이상인 그룹에 대해 평균 계산 및 적용
    for key, group in duplicate_groups.items():
        if len(group) >= 2:
            total_amount = sum(item['amount'] for item in group)
            average_amount = total_amount / len(group)

            # 모든 행에 평균값 적용
            for item in group:
                ws[f"D{item['row']}"].value = average_amount

            logger.info(
                f"주문번호-주소 조합 '{key}'의 {len(group)}개 행에 평균 금액 {average_amount:.2f} 적용")


def macro_basic_process(df: pd.DataFrame):
    """
    기본처리 함수
    """
    logger.info(f"[START]macro_basic_process")

    # 매크로 실행 완료
    df['work_status'] = 'macro_run'

    # 도서지역 배송비 및 상품명 추가
    df = add_island_delivery(df)

    # 상품명 1개 제거
    df['item_name'] = df['item_name'].fillna('').str.replace(' 1개', '')

    # 전화번호 포맷팅
    df = format_phone_number(df)

    # 선불, 착불 처리
    df.loc[df['delivery_payment_type'].fillna(
        '').str.contains('선불'), 'delivery_payment_type'] = ''

    # 주문번호
    df['mall_order_id'] = df['mall_order_id'].fillna(
        '').astype(str)
    logger.info(f"[END]macro_basic_process")
    return df


def add_island_delivery(df: pd.DataFrame):
    """
    도서지역 배송비 및 상품명 추가
    """
    logger.info(f"[START]add_island_delivery")
    island_dict = [
        {"site_name": "GSSHOP", "fid_dsp": "GSSHOP", "cost": 3000, "add_dsp": None},
        {"site_name": "텐바이텐", "fid_dsp": "텐바이텐", "cost": 3000,
         "add_dsp": "[3000원 연락해야함, 어드민 조회필요(외부몰/자체몰)]"},
        {"site_name": "쿠팡", "fid_dsp": "쿠팡", "cost": 3000, "add_dsp": None},
        {"site_name": "무신사", "fid_dsp": "무신사", "cost": 3000, "add_dsp": None},
        {"site_name": "NS홈쇼핑", "fid_dsp": "NS홈쇼핑", "cost": 3000, "add_dsp": None},
        {"site_name": "CJ온스타일", "fid_dsp": "CJ온스타일", "cost": 3000, "add_dsp": None},
        {"site_name": "오늘의집", "fid_dsp": "오늘의집", "cost": 3000, "add_dsp": None},
        {"site_name": "브랜디", "fid_dsp": "브랜디",
            "cost": 3000, "add_dsp": "[3000원 연락해야함]"},
        {"site_name": "에이블리", "fid_dsp": "에이블리", "cost": 3000, "add_dsp": None},
        {"site_name": "보리보리", "fid_dsp": "보리보리",
            "cost": 3000, "add_dsp": "[3000원 연락해야함]"},
        {"site_name": "지그재그", "fid_dsp": "지그재그", "cost": 3000, "add_dsp": None},
        {"site_name": "카카오톡선물하기", "fid_dsp": "카카오선물하기",
            "cost": 3000, "add_dsp": "[3000원 연락해야함]"},
        {"site_name": "11번가", "fid_dsp": "11번가", "cost": 5000, "add_dsp": None},
        {"site_name": "홈&쇼핑", "fid_dsp": "홈&쇼핑",
            "cost": 3000, "add_dsp": "[3000원 연락해야함]"},
    ]

    # 제주도 배송 주소 필터
    jeju_mask = df['receive_addr'].fillna(
        '').str.contains('제주', case=False, na=False)
    jeju_data = df[jeju_mask].copy()

    if jeju_data.empty:
        return df

    logger.info(f"island count: {len(jeju_data)}")

    for island_info in island_dict:
        # 해당 사이트의 제주도 배송 데이터 필터링
        site_mask = jeju_data['fid_dsp'].fillna('').str.contains(
            island_info['fid_dsp'], case=False, na=False
        )
        target_indices = jeju_data[site_mask].index

        if len(target_indices) == 0:
            continue

        logger.info(
            f"{island_info['site_name']} 제주도 배송: {len(target_indices)}건")

        # 상품명에 추가 정보 append
        if island_info['add_dsp']:
            df.loc[target_indices, 'product_name'] = (
                df.loc[target_indices, 'product_name'].fillna(
                    '') + island_info['add_dsp']
            )

        # 배송비 추가
        if island_info['cost']:
            df.loc[target_indices, 'delv_cost'] = (
                df.loc[target_indices, 'delv_cost'].fillna(
                    0) + island_info['cost']
            )
    logger.info(f"[END]add_island_delivery")
    return df


def format_phone_number(df: pd.DataFrame):
    """
    전화번호 포맷팅
    """
    receive_tel = df['receive_tel'].fillna('').str.replace('-', '')
    receive_cel = df['receive_cel'].fillna('').str.replace('-', '')
    if len(receive_tel) == 11 and receive_tel.startswith('010') and receive_tel.isdigit():
        df.loc[receive_tel,
               'receive_tel'] = f"{receive_tel[:3]}-{receive_tel[3:7]}-{receive_tel[7:]}"
    if len(receive_cel) == 11 and receive_cel.startswith('010') and receive_cel.isdigit():
        df.loc[receive_cel,
               'receive_cel'] = f"{receive_cel[:3]}-{receive_cel[3:7]}-{receive_cel[7:]}"
    return df


def star_average_process(df: pd.DataFrame):
    """
    스타배송 평균 배송비 적용
    """
    logger.info(f"[START]star_average_process")

    df['star_avg'] = df['mall_order_id'].fillna(0) + '_' + df['receive_addr']

    # 배송비 빈값 체크
    valid_delivery_mask = (df['delv_cost'] != 0) & (
        df['delv_cost'].notna()) & (df['delv_cost'] != "")

    # 빈 값이 아닌 그룹만 평균 계산
    valid_delivery_df = df[valid_delivery_mask]

    # 2개 이상인 그룹별 평균 배송비 계산 적용
    if len(valid_delivery_df) > 0:
        group_sizes = valid_delivery_df.groupby('star_avg').size()
        groups_with_multiple = group_sizes[group_sizes >= 2].index
        
        if len(groups_with_multiple) > 0:
            avg_delivery = valid_delivery_df[valid_delivery_df['star_avg'].isin(groups_with_multiple)].groupby('star_avg')['delv_cost'].mean()
            
            # 평균 배송비 적용
            df.loc[df['star_avg'].isin(avg_delivery.index), 'delv_cost'] = df.loc[df['star_avg'].isin(avg_delivery.index), 'star_avg'].map(avg_delivery)
            
            logger.info(f"스타배송 평균 배송비 적용 완료: {len(avg_delivery)}개 그룹 (2개 이상인 그룹만)")
    
    # 임시 컬럼 제거
    df = df.drop('star_avg', axis=1)
    return df
