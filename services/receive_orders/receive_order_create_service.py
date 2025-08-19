import re
import json
import hashlib
import requests
import xml.etree.ElementTree as ET

from pathlib import Path
from decimal import Decimal
from urllib.parse import urljoin
from datetime import datetime, date
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import SETTINGS
from utils.logs.sabangnet_logger import get_logger
from utils.sabangnet_path_utils import SabangNetPathUtils
from utils.make_xml.order_create_xml import OrderCreateXml
from minio_handler import upload_file_to_minio, get_minio_file_url
from repository.receive_orders_repository import ReceiveOrdersRepository

from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto
from schemas.receive_orders.response.receive_orders_response import ReceiveOrdersBulkCreateResponse


logger = get_logger(__name__)


class ReceiveOrderCreateService:
    """
    주문 목록 수집 서비스
    """
    
    _JSON_PATH = SabangNetPathUtils.get_json_file_path()
    _MASKING_RULES = {
        'USER_NAME': 'name',
        'RECEIVE_NAME': 'name',
        'USER_ID': 'user_id',
        'RECEIVE_TEL': 'phone',
        'RECEIVE_CEL': 'phone',
        'USER_CEL': 'phone',
        'RECEIVE_ADDR': 'address',
        'RECEIVE_ZIPCODE': 'zipcode',
        'ORDER_ID': 'id',
        'MALL_ORDER_ID': 'id',
        'MALL_USER_ID': 'user_id'
    }
    _DECIMAL_FIELDS = [
        'total_cost',
        'pay_cost',
        'sale_cost',
        'mall_won_cost',
        'won_cost',
        'delv_cost'
    ]
    _INT_FIELDS = [
        'sale_cnt',
        'box_ea',
        'p_ea',
        'acnt_regs_srno'
    ]
    _DATE_FIELDS = [
        'order_date'
    ]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.receive_orders_repository = ReceiveOrdersRepository(session)

    def create_request_xml(self, ord_st_date: str, ord_ed_date: str, order_status: str, dst_path_name: str = None) -> Path:
        order_create_xml = OrderCreateXml(
            ord_st_date=ord_st_date,
            ord_ed_date=ord_ed_date,
            order_status=order_status
        )
        tree = order_create_xml.make_order_create_xml()
        xml_file_path = order_create_xml.save_order_create_xml_to_local(tree, dst_path_name)
        logger.info(f"\n요청 XML이 {xml_file_path}에 저장되었습니다.")
        return xml_file_path

    def get_xml_url_from_minio(self, xml_file_path: Path) -> str:
        object_name = upload_file_to_minio(xml_file_path)
        logger.info(f"MinIO에 업로드된 XML 파일 이름: {object_name}")
        xml_url = get_minio_file_url(object_name)
        logger.info(f"MinIO에 업로드된 XML URL: {xml_url}")
        return xml_url
    
    def get_orders_from_sabangnet(self, xml_url: str) -> str:
        try:
            api_url = urljoin(SETTINGS.SABANG_ADMIN_URL, '/RTL_API/xml_order_info.html')
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")
            response = requests.get(full_url, timeout=30)
            response_text = str(response.text)
            if len(response_text) > 1000:
                response_text = response_text[:1000] + "..."
            logger.info(f"API 요청 결과: {response_text}")
            response.raise_for_status()
            return response.text
                
        except requests.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise

    def _parse_date_field(self, val: str) -> date | None:
        """
        날짜 형식을 변환하는 함수.
        """

        if not val:
            return None
        try:
            if len(val) == 8:
                return datetime.strptime(val, '%Y%m%d').date()
            elif len(val) == 14:
                return datetime.strptime(val, '%Y%m%d%H%M%S').date()
            else:
                return None
        except Exception as e:
            logger.error(f"order_date 변환 실패: {val} ({e})")
            return None

    def _convert_json_to_order_list(self, json_orders: list[dict], safe_mode: bool = True) -> list[dict]:
        """
        JSON 데이터를 파싱하여 주문 리스트를 반환하는 함수.
        """
        
        order_dict_list = []
        for order in json_orders:
            # 대소문자 변환
            order_detail = {k.lower(): v for k, v in order.items()}
            
            # 마스킹 처리
            if safe_mode:
                for field_name, mask_type in self._MASKING_RULES.items():
                    if field_name in order_detail and order_detail[field_name]:
                        order_detail[field_name] = self._mask_personal_info(order_detail[field_name], mask_type)
            
            # 기본 필드 추가
            order_detail["receive_dt"] = datetime.now()
            
            # 필드 타입 변환
            for field in self._DECIMAL_FIELDS:
                if field in order_detail:
                    try:
                        order_detail[field] = Decimal(order_detail[field]) if order_detail[field] != '' else None
                    except Exception as e:
                        logger.error(f"{field} Decimal 변환 실패: {order_detail[field]} ({e})")
                        order_detail[field] = None
            
            for field in self._INT_FIELDS:
                if field in order_detail:
                    try:
                        order_detail[field] = int(order_detail[field]) if order_detail[field] != '' else None
                    except Exception as e:
                        logger.error(f"{field} int 변환 실패: {order_detail[field]} ({e})")
                        order_detail[field] = None
            
            for field in self._DATE_FIELDS:
                if field in order_detail:
                    order_detail[field] = self._parse_date_field(order_detail[field])
            
            # dict 형태로 직접 추가
            order_dict_list.append(order_detail)
        
        logger.info(f"총 {len(order_dict_list)}개의 주문을 변환했습니다.")
        return order_dict_list

    def _parse_xml_to_order_list(self, xml_content: str, safe_mode: bool = True) -> list[dict]:
        """
        XML을 파싱하여 주문 리스트를 반환하는 함수.
        """
        
        root = ET.fromstring(xml_content)
        order_dict_list = []
        for data_node in root.findall('DATA'):
            # 먼저 dict로 데이터 수집
            order_detail = {}
            for elem in data_node.findall('*'):
                elem_tag = elem.tag.strip() if elem.tag else ''
                elem_text = elem.text.strip() if elem.text else ''
                if elem.tag and elem.text:
                    if safe_mode and (elem_tag in self._MASKING_RULES):
                        mask_type = self._MASKING_RULES[elem_tag]
                        elem_text = self._mask_personal_info(elem_text, mask_type)
                    # XML 태그명을 소문자로 변환해서 저장
                    order_detail[elem_tag.lower()] = elem_text
            
            # 기본 필드 추가
            order_detail["receive_dt"] = datetime.now()
            
            # 필드 타입 변환
            for field in self._DECIMAL_FIELDS:
                if field in order_detail:
                    try:
                        order_detail[field] = Decimal(order_detail[field]) if order_detail[field] != '' else None
                    except Exception as e:
                        logger.error(f"{field} Decimal 변환 실패: {order_detail[field]} ({e})")
                        order_detail[field] = None
            
            for field in self._INT_FIELDS:
                if field in order_detail:
                    try:
                        order_detail[field] = int(order_detail[field]) if order_detail[field] != '' else None
                    except Exception as e:
                        logger.error(f"{field} int 변환 실패: {order_detail[field]} ({e})")
                        order_detail[field] = None
            
            for field in self._DATE_FIELDS:
                if field in order_detail:
                    order_detail[field] = self._parse_date_field(order_detail[field])
            
            # dict 형태로 직접 추가
            order_dict_list.append(order_detail)
        
        logger.info(f"총 {len(order_dict_list)}개의 주문을 파싱했습니다.")
        return order_dict_list

    def _mask_personal_info(self, value: str, mask_type: str) -> str:
        """
        민감타입에 해당하는 개인정보를 마스킹 처리하는 함수.
        """

        if not value or value.strip() == '':
            return value

        if mask_type == 'name':
            # 이름: 첫 글자만 보이고 나머지는 *
            if len(value) <= 1:
                return '*'
            return value[0] + '*' * (len(value) - 1)

        elif mask_type == 'phone':
            # 전화번호: 중간 4자리를 ****로 마스킹
            phone_digits = re.sub(r'[^0-9]', '', value)
            if len(phone_digits) >= 8:
                if len(phone_digits) == 11:  # 휴대폰
                    return phone_digits[:3] + '****' + phone_digits[7:]
                elif len(phone_digits) == 10:  # 일반전화
                    return phone_digits[:3] + '****' + phone_digits[6:]
            return '****'

        elif mask_type == 'address':
            # 주소: 상세주소 부분을 마스킹
            parts = value.split()
            if len(parts) > 2:
                # 시/도, 시/군/구는 유지하고 상세주소는 마스킹
                return ' '.join(parts[:2]) + ' ****'
            return '****'

        elif mask_type == 'zipcode':
            # 우편번호: 앞 3자리만 유지
            if len(value) >= 3:
                return value[:3] + '*' * (len(value) - 3)
            return '*' * len(value)

        elif mask_type == 'id':
            # ID: 해시값으로 대체 (일관성 유지를 위해)
            return hashlib.md5(value.encode()).hexdigest()[:8]

        elif mask_type == 'user_id':
            # 사용자 ID: 앞 2자리만 유지
            if len(value) > 2:
                return value[:2] + '*' * (len(value) - 2)
            return '*' * len(value)

        return value

    async def save_orders_to_db_from_xml(self, xml_content: str, safe_mode: bool = True) -> ReceiveOrdersBulkCreateResponse:
        """
        XML을 파싱하여 주문 리스트를 DB에 저장하는 함수.
        """

        order_dict_list = self._parse_xml_to_order_list(xml_content, safe_mode)
        logger.info(f"총 {len(order_dict_list)}개의 주문을 DB에 저장합니다.")
        
        try:
            success_models = await self.receive_orders_repository.bulk_insert_orders(order_dict_list)
            
            return ReceiveOrdersBulkCreateResponse(
                success=True,
                total_count=len(order_dict_list),
                success_count=len(success_models),
                duplicated_count=len(order_dict_list) - len(success_models),
            )
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"DB 저장 중 오류: {e}")
            raise

    def save_orders_to_json_from_xml(self, xml_content: str, safe_mode: bool = True) -> ReceiveOrdersBulkCreateResponse:
        """
        XML을 파싱하여 주문 리스트를 JSON 파일로 저장하고 반환하는 함수.
        """

        receive_orders_dict_list = self._parse_xml_to_order_list(xml_content, safe_mode)
        logger.info(f"총 {len(receive_orders_dict_list)}개의 주문을 JSON 파일로 저장합니다.")

        try:
            # dict 리스트를 DTO로 변환
            receive_orders_dto_list: list[ReceiveOrdersDto] = []
            for receive_orders_dict in receive_orders_dict_list:
                try:
                    receive_orders_dto = ReceiveOrdersDto.model_validate(receive_orders_dict)
                    receive_orders_dto_list.append(receive_orders_dto)
                except Exception as e:
                    logger.error(f"DTO 변환 실패: {e} (data: {receive_orders_dict})")
                    continue
            
            # DTO를 JSON으로 직렬화 가능한 형태로 변환
            json_data = [receive_orders_dto.model_dump() for receive_orders_dto in receive_orders_dto_list]
            
            dst_json_path = self._JSON_PATH / "order_list.json"
            with open(dst_json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4, default=str)
            logger.info(f"주문 데이터가 {dst_json_path}에 저장되었습니다.")
            return ReceiveOrdersBulkCreateResponse(
                total_count=len(receive_orders_dict_list),
                success_count=len(receive_orders_dto_list),
                duplicated_count=len(receive_orders_dict_list) - len(receive_orders_dto_list),
            )
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise

    async def save_orders_to_db_from_json(self, json_file_name: str) -> ReceiveOrdersBulkCreateResponse:
        """
        JSON 파일에서 주문 데이터를 읽어 DB에 저장하는 함수.
        """

        json_file_path = self._JSON_PATH / json_file_name
        if not json_file_name.endswith(".json"):
            json_file_path = self._JSON_PATH / f"{json_file_name}.json"

        if not json_file_path.exists():
            raise FileNotFoundError(f"해당 파일을 찾을 수 없습니다. (파일명: {json_file_path})")

        with open(json_file_path, "r", encoding="utf-8") as f:
            raw_order_data_list: list[dict] = json.load(f)
        
        order_data_list = self._convert_json_to_order_list(raw_order_data_list)
        success_models = await self.receive_orders_repository.bulk_insert_orders(order_data_list)
        logger.info(f"저장된 주문 수: {len(success_models)}")

        return ReceiveOrdersBulkCreateResponse(
            total_count=len(order_data_list),
            success_count=len(success_models),
            duplicated_count=len(order_data_list) - len(success_models),
        )

    def get_order_xml_template(self, ord_st_date: str, ord_ed_date: str, order_status: str, file_name: str = None) -> StreamingResponse:
        """
        주문 수집 데이터 XML 템플릿만 생성하고 내려받음. 요청은 안함. (검토용)
        """
        order_create_xml = OrderCreateXml(
            ord_st_date=ord_st_date,
            ord_ed_date=ord_ed_date,
            order_status=order_status
        )
        tree = order_create_xml.make_order_create_xml()
        return order_create_xml.save_order_create_xml_to_stream(tree, file_name)
