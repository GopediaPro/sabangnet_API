from utils.macros.ERP.etc_site_macro import ECTSiteMacro
from utils.macros.ERP.zigzag_erp_macro import ZigzagMacro
from utils.macros.ERP.ali_erp_macro import AliMacro
from utils.macros.ERP.brandi_erp_macro import BrandiMacro
from utils.macros.happojang.etc_site_merge_packaging import etc_site_merge_packaging
from utils.macros.happojang.zigzag_merge_packaging import zigzag_merge_packaging
from utils.macros.happojang.ali_merge_packaging import ali_merge_packaging
from utils.macros.happojang.brandy_merge_packaging import brandy_merge_packaging
from utils.macros.happojang.gok_merge_packaging import gok_merge_packaging
from repository.template_config_repository import TemplateConfigRepository
from utils.macros.ERP.Gmarket_auction_erp_macro import GmarketAuctionMacro
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from minio_handler import temp_file_to_object_name, delete_temp_file
from repository.down_form_order_repository import DownFormOrderRepository
from repository.export_form_order_repository import ExportFormOrderRepository
import re

logger = get_logger(__name__)

def run_ect_site_macro(file):
    macro = ECTSiteMacro(file)
    return macro.step_1_to_14()

def run_zigzag_macro(file):
    macro = ZigzagMacro(file)
    return macro.step_1_to_9()

def run_ali_macro(file):
    macro = AliMacro(file)
    return macro.step_1_to_10()

def run_brandi_macro(file):
    macro = BrandiMacro(file)
    return macro.step_1_to_11()

def run_gmarket_auction_macro(file_path):
    macro = GmarketAuctionMacro(file_path)
    result = macro.step_1_to_11()
    return result

# macro_name과 실제 실행 함수를 매핑
MACRO_MAP = {
    "ECTSiteMacro": run_ect_site_macro,
    "ZigzagMacro": run_zigzag_macro,
    "AliMacro": run_ali_macro,
    "BrandiMacro": run_brandi_macro,
    "etc_site_merge_packaging": etc_site_merge_packaging,
    "zigzag_merge_packaging": zigzag_merge_packaging,
    "ali_merge_packaging": ali_merge_packaging,
    "brandy_merge_packaging": brandy_merge_packaging,
    "gok_merge_packaging": gok_merge_packaging,
    "GmarketAuctionMacro": run_gmarket_auction_macro,
}

async def run_macro_with_file(session: AsyncSession, template_code: str, file_path: str):
    template_config_repository = TemplateConfigRepository(session)
    logger.info(f"run_macro called with template_code={template_code}, file_path={file_path}")
    macro_name = await template_config_repository.get_macro_name_by_template_code(template_code)
    logger.info(f"macro_name from DB: {macro_name}")
    if macro_name:
        macro_func = MACRO_MAP.get(macro_name)
        if macro_func is None:
            logger.error(f"Macro '{macro_name}' not found in MACRO_MAP.")
            raise ValueError(f"Macro '{macro_name}' not found in MACRO_MAP.")
        try:
            result = macro_func(file_path)
            logger.info(f"Macro '{macro_name}' executed successfully. file_path={result}")
            return result
        except Exception as e:
            logger.error(f"Error running macro '{macro_name}': {e}")
            raise
    else:
        logger.error(f"Macro not found for template code: {template_code}")
        raise ValueError(f"Macro not found for template code: {template_code}")

async def process_macro_with_tempfile(session, template_code, file):
    """
    1. 업로드 파일을 임시 파일로 저장
    2. 매크로 실행 (run_macro)
    3. 임시 파일 삭제
    4. 파일명 반환
    5. (필요시) presigned URL에서 쿼리스트링 제거
    """
    file_name = file.filename
    temp_upload_file_path = temp_file_to_object_name(file)
    try:
        file_path = await run_macro_with_file(session, template_code, temp_upload_file_path)
    finally:
        delete_temp_file(temp_upload_file_path)
    return file_name, file_path

async def run_macro_with_db(session: AsyncSession, template_code: str):
    template_config_repository = TemplateConfigRepository(session)
    down_form_order_repository = DownFormOrderRepository(session)
    export_form_order_repository = ExportFormOrderRepository(session)
    logger.info(f"run_macro called with template_code={template_code}")
    # 1. 템플릿 설정 조회
    config = await template_config_repository.get_template_config_by_template_code(template_code)
    logger.info(f"Loaded template config: {config}")

    # 2. db 데이터를 템플릿에 따라 df 데이터 run_macro 실행 (preprocess_order_data)
    down_order_data = await down_form_order_repository.get_down_form_orders(template_code, limit=1000000)
    processed_orders = process_orders_for_db(down_order_data, template_code)
    # 3. processed_orders 데이터를 "export_form_order" 테이블에 저장 후 성공한 레코드 수 반환
    try:
        len_saved = await export_form_order_repository.bulk_insert(processed_orders)
        logger.info(f"Saved {len_saved} records to export_form_order table")
        
        return len_saved
    except Exception as e:
        logger.error(f"Error running macro with db: {e}")
        raise

def preprocess_order_data(order_data, template_code):
    """주문 데이터 전체 전처리"""
    
    # 기본 정보 정리
    processed = {
        'receiver_name': str(order_data.get('receiver_name', '')).strip(),
        'item_name': clean_item_name(order_data.get('item_name')),
        'phone1': format_phone_number(order_data.get('phone1')),
        'phone2': format_phone_number(order_data.get('phone2')),
        'address': str(order_data.get('address', '')).strip(),
        'order_number': clean_order_text(order_data.get('order_number')),
    }
    
    # 숫자 데이터 변환
    numeric_fields = ['quantity', 'product_price', 'option_price', 'delv_cost', 'total_amount']
    for field in numeric_fields:
        processed[field] = convert_to_number(order_data.get(field, 0))
    
    # 배송비 계산
    processed['delv_cost'] = calculate_delivery_fee(processed)
    
    # 제주 주소 처리
    if is_jeju_address(processed['address']):
        processed['item_name'] = add_jeju_notice(processed['item_name'], processed['address'])
        processed['is_jeju'] = True
    else:
        processed['is_jeju'] = False
    
    # 다중 수량 체크
    processed['is_multiple_quantity'] = check_multiple_quantities(processed['item_name'])
    
    return processed

def process_orders_for_db(orders_list, template_code):
    """DB 저장을 위한 주문 리스트 전체 처리"""
    
    # 1. 개별 주문 전처리
    processed_orders = [preprocess_order_data(order, template_code) for order in orders_list]
    
    # 2. 정렬
    processed_orders = sort_orders_by_receiver_and_site(processed_orders)
    
    # 3. 중복 제거 (필요한 경우)
    if processed_orders['site_name'] in ['G마켓', '옥션']:
        processed_orders = remove_duplicate_shipping_fee(processed_orders)
    
    # 4. 주문 병합 (브랜디의 경우)
    if '브랜디' in processed_orders['site_name']:
        groups = group_orders_by_product_and_receiver(processed_orders)
        processed_orders = [merge_order_group(group) for group in groups.values()]
    
    return processed_orders

def sum_slash_values(value_str):
    """슬래시로 구분된 값들을 합산"""
    if not value_str or '/' not in str(value_str):
        return convert_to_number(value_str)
    
    total = 0.0
    for part in str(value_str).split('/'):
        total += convert_to_number(part.strip())
    
    return total

def get_first_valid_slash_value(value_str):
    """슬래시로 구분된 값 중 첫 번째 유효 숫자만 반환"""
    if not value_str or '/' not in str(value_str):
        return convert_to_number(value_str)
    
    for part in str(value_str).split('/'):
        num = convert_to_number(part.strip())
        if num != 0:
            return num
    
    return 0.0

def is_jeju_address(address):
    """주소가 제주도인지 확인"""
    if not address:
        return False
    
    jeju_keywords = ['제주', '서귀포']
    return any(keyword in str(address) for keyword in jeju_keywords)

def add_jeju_notice(item_name, address):
    """제주 주소인 경우 상품명에 안내문구 추가"""
    if not is_jeju_address(address):
        return item_name
    
    notice = "[3000원 연락해야함]"
    if notice not in str(item_name):
        return f"{item_name} {notice}"
    
    return item_name

def group_orders_by_product_and_receiver(orders):
    """상품번호+수령인 기준으로 주문 그룹핑"""
    from collections import defaultdict
    
    groups = defaultdict(list)
    
    for order in orders:
        key = f"{order.get('product_code', '')}-{order.get('receiver_name', '')}"
        groups[key].append(order)
    
    return groups

def merge_order_group(order_group):
    """같은 그룹의 주문들을 병합"""
    if len(order_group) <= 1:
        return order_group[0] if order_group else {}
    
    base_order = order_group[0].copy()
    
    # D열(금액) 합산
    total_amount = 0.0
    for order in order_group:
        amount = order.get('total_amount', 0)
        if isinstance(amount, str) and '=' in amount:
            # 수식인 경우 개별 항목 합산
            o_val = convert_to_number(order.get('product_price', 0))
            p_val = convert_to_number(order.get('option_price', 0))
            v_val = convert_to_number(order.get('delv_cost', 0))
            total_amount += (o_val + p_val + v_val)
        else:
            total_amount += convert_to_number(amount)
    
    # G열(수량) 합산
    total_quantity = sum(convert_to_number(order.get('quantity', 0)) for order in order_group)
    
    # F열(item_name) 결합
    model_names = []
    for order in order_group:
        model = clean_item_name(order.get('item_name', ''))
        if model:
            model_names.append(model)
    
    base_order.update({
        'total_amount': total_amount,
        'quantity': total_quantity,
        'item_name': ' + '.join(model_names)
    })
    
    return base_order

def calculate_delivery_fee(order_data):
    """사이트별 배송비 계산"""
    
    # 무료 배송 사이트
    free_delivery_sites = {'오늘의집'}
    site_name = order_data.get('site_name', '')
    if any(site in site_name for site in free_delivery_sites):
        return 0
    
    # 배송비 분할 사이트
    split_delivery_sites = {'롯데온', '보리보리', '스마트스토어', '톡스토어'}
    if any(site in site_name for site in split_delivery_sites):
        order_code = str(order_data.get('idx', ''))
        original_fee = convert_to_number(order_data.get('delv_cost', 0))
        
        if '/' in order_code:
            order_count = len(order_code.split('/'))
            if original_fee > 3000 and order_count > 0:
                return round(original_fee / order_count)
    
    # 토스 특수 처리
    if '토스' in site_name:
        product_amount = convert_to_number(order_data.get('pay_cost', 0))
        return 0 if product_amount > 30000 else 3000
    
    # 기본 배송비 반환
    return convert_to_number(order_data.get('delv_cost', 0))

def sort_orders_by_receiver_and_site(orders):
    """수취인명, 사이트 순으로 정렬"""
    return sorted(orders, key=lambda x: (
        x.get('receiver_name', ''),
        x.get('site_name', '')
    ))

def sort_orders_by_receiver_only(orders):
    """수취인명으로만 정렬"""
    return sorted(orders, key=lambda x: x.get('receiver_name', ''))

def build_lookup_mapping(lookup_data):
    """조회 테이블을 딕셔너리로 변환"""
    mapping = {}
    for row in lookup_data:
        key = str(row.get('lookup_key', ''))
        value = row.get('lookup_value', 'S')  # 기본값 'S'
        if key:
            mapping[key] = value
    return mapping

def lookup_value(lookup_map, key, default='S'):
    """키로 값 조회"""
    return lookup_map.get(str(key), default)

def remove_duplicate_shipping_fee(orders):
    """바구니 번호별 중복 배송비 제거"""
    basket_dict = {}
    
    # 첫 번째 패스: 배송비가 있는 첫 주문 기록
    for i, order in enumerate(orders):
        basket_no = str(order.get('mall_order_id', '')).strip()
        delv_cost = convert_to_number(order.get('delv_cost', 0))
        
        if basket_no and basket_no != '':
            if basket_no not in basket_dict and delv_cost > 0:
                basket_dict[basket_no] = i
    
    # 두 번째 패스: 중복 바구니의 배송비를 0으로 설정
    for i, order in enumerate(orders):
        basket_no = str(order.get('mall_order_id', '')).strip()
        
        if basket_no and basket_no != '':
            if basket_no in basket_dict and basket_dict[basket_no] != i:
                order['delv_cost'] = 0
    
    return orders

def check_multiple_quantities(product_text):
    """상품명에서 다중 수량 여부 확인"""
    if not product_text:
        return False
    
    parts = [p.strip() for p in str(product_text).split('+')]
    qty_count = sum(1 for p in parts if re.search(r'\d+개', p))
    
    return qty_count >= 2

def extract_quantity_from_text(text):
    """텍스트에서 수량 추출"""
    if not text:
        return 1
    
    match = re.search(r'(\d+)개', str(text))
    return int(match.group(1)) if match else 1

def clean_item_name(val):
    """
    상품명에서 ' 1개' 등 불필요한 텍스트 제거
    """
    if not val:
        return val
    return str(val).replace(' 1개', '').strip()


def format_phone_number(val):
    """
    전화번호 11자리 → 010-0000-0000 형식
    """
    val = str(val or '').replace('-', '').strip()
    if len(val) == 11 and val.startswith('010') and val.isdigit():
        return f"{val[:3]}-{val[3:7]}-{val[7:]}"
    return val


def convert_to_number(val):
    """
    '12,345원' → 12345 (실패 시 0)
    """
    import re
    try:
        return int(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0
    except ValueError:
        return 0


def clean_order_text(val):
    """
    주문번호 등에서 불필요한 공백/특수문자 제거
    """
    if not val:
        return ''
    return str(val).strip().replace(' ', '').replace('\n', '').replace('\r', '') 