# std
import asyncio
import unicodedata
import re
import os
import pandas as pd
from datetime import datetime
from fastapi import UploadFile
from typing import Any, Optional
# util
from utils.excels.convert_xlsx import ConvertXlsx
from utils.logs.sabangnet_logger import get_logger
from utils.excels.excel_handler import ExcelHandler
from utils.macros.order_macro_utils import OrderMacroUtils
from utils.macros.data_processing_utils import DataProcessingUtils
from utils.mappings.order_status_label_mapping import STATUS_LABEL_TO_CODE
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# model
from models.receive_orders.receive_orders import ReceiveOrders
from models.down_form_orders.down_form_order import BaseDownFormOrder
# schema
from schemas.receive_orders.response.receive_orders_response import ReceiveOrdersBulkCreateResponse
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto, DownFormOrdersBulkDto, DownFormOrdersFromReceiveOrdersDto
from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto
from schemas.macro_batch_processing.request.batch_process_request import BatchProcessRequest
from schemas.integration_response import ResponseHandler, Metadata
# service
from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
from services.receive_orders.receive_order_create_service import ReceiveOrderCreateService
from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
from services.down_form_orders.template_config_read_service import TemplateConfigReadService
from services.down_form_orders.down_form_order_create_service import DownFormOrderCreateService
from services.export_templates.export_templates_read_service import ExportTemplatesReadService
from services.macro_batch_processing.batch_info_create_service import BatchInfoCreateService
from services.vlookup_datas.vlookup_datas_read_service import VlookupDatasReadService
from services.vlookup_datas.vlookup_datas_create_service import VlookupDatasCreateService
# file
from minio_handler import temp_file_to_object_name, delete_temp_file, upload_and_get_url_and_size, url_arrange


logger = get_logger(__name__)


class DataProcessingUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_macro_utils = OrderMacroUtils()
        self.order_read_service = ReceiveOrderReadService(session)
        self.template_config_read_service = TemplateConfigReadService(session)
        self.down_form_order_read_service = DownFormOrderReadService(session)
        self.down_form_order_create_service = DownFormOrderCreateService(
            session)
        self.export_templates_read_service = ExportTemplatesReadService(
            session)
        self.batch_info_create_service = BatchInfoCreateService(session)
        self.order_create_service = ReceiveOrderCreateService(session)
        self.vlookup_datas_read_service = VlookupDatasReadService(session)
        self.vlookup_datas_create_service = VlookupDatasCreateService(session)

    def parse_filename(self, filename: str) -> dict[str, Any]:
        """
        파일명에서 사이트타입, 용도타입, 세부사이트 추출
        args:
            filename: 파일명
        returns:
            dict: {
                'site_type': str,      # "G마켓,옥션", "기본양식", "브랜디"
                'usage_type': str,      # "ERP용", "합포장용"  
                'sub_site': str,        # "기타사이트", "지그재그", None
                'is_star': bool         # 스타배송 여부
            }
        """
        from utils.unicode_utils import normalize_for_comparison

        # 유니코드 정규화 후 "스타배송" 포함 여부로만 판단
        normalized_filename = normalize_for_comparison(filename)
        is_star = '스타배송' in normalized_filename

        # [사이트타입] 또는 (사이트타입)-용도타입-세부사이트 추출 (구분자: - 또는 _)
        match = re.search(
            r'[\[\(]([^\]\)]+)[\]\)]-([^-_]+?)(?:[-_]([^.]+?))?(?:\.xlsx)?$', normalized_filename)

        result = {
            'site_type': None,
            'usage_type': None,
            'sub_site': None,
            'is_star': is_star
        }
        if not match:
            return result
        
        TYPE_MATCH_MAPPING: dict[str, set[str]] = {
            'site_type': {'G마켓,옥션', '기본양식', '브랜디'},
            'usage_type': {'ERP용', '합포장용'},
            'sub_site': {'기타사이트', '지그재그', '알리'}
        }
        # match group tuple로 반환
        groups = match.groups()
 
        for group in groups:
            # group 비어있으면 패스
            if not group:
                continue
            # group이 TYPE_MATCH_MAPPING에 있는 값과 일치하면 result에 추가
            for key, values in TYPE_MATCH_MAPPING.items():
                if group in values:
                    result[key] = group

        return result

    async def down_form_order_to_excel(self, template_code: str, file_path: str, file_name: str):
        """
        down_form_order_to_excel
        args:
            template_code: template code(gmarket_erp, etc_site_erp ...)
            file_path: file path
            file_name: file name
        returns:
            file_path: file path
        """
        template_config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        down_form_orders = await self.down_form_order_read_service.get_down_form_orders_by_template_code(template_code)

        mapping_field = await DataProcessingUtils.create_mapping_field(template_config)

        convert_xlsx = ConvertXlsx()
        file_path = convert_xlsx.export_translated_to_excel(
            down_form_orders, mapping_field, file_name, file_path=file_path)
        return file_path

    async def get_template_config_by_template_code(self, template_code: str) -> dict:
        """
        get template config
        args:
            template_code: template code(gmarket_erp, etc_site_erp ...)
        returns:
            template_config: 전체 템플릿 설정 (column_mappings 포함)
        """

        template_config: dict = await self.template_config_read_service.get_template_config_by_template_code(template_code=template_code)
        return template_config

    async def get_down_form_orders_by_template_code(self, template_code: str) -> list[DownFormOrderDto]:
        """
        get down_form_orders
        returns:
            down_form_orders: down_form_orders SQLAlchemy ORM 인스턴스
        """

        down_form_order_dtos: list[DownFormOrderDto] = []

        down_form_order_models: list[BaseDownFormOrder] = await self.down_form_order_read_service.get_down_form_orders_by_template_code(template_code=template_code)
        for down_form_order_model in down_form_order_models:
            down_form_order_dtos.append(
                DownFormOrderDto.model_validate(down_form_order_model))

        return down_form_order_dtos

    async def save_down_form_orders_from_receive_orders_by_filter(
            self,
            filters: dict[str, Any],
            template_code: str
    ) -> DownFormOrdersBulkDto:
        """
        save down_form_orders from receive_orders by filter
        args:
            filters: filters
            template_code: template code
        returns:
            down_form_orders_bulk_dto: down_form_orders_bulk_dto
        """

        logger.info(
            f"[START] save_down_form_orders_from_receive_orders_by_filter | template_code={template_code} | filters={filters}")
        # 1. receive_orders 조회하고 모델 받아옴
        receive_orders: list[ReceiveOrders] = await self.order_read_service.get_receive_orders_by_filters(filters)
        if not receive_orders:
            return DownFormOrdersBulkDto(
                success=False,
                template_code=template_code,
                processed_count=0,
                saved_count=0,
                message="No data found to process"
            )
        # 2. receive_orders 데이터를 dto로 변환하고 그걸 다시 dict로 변환
        receive_orders_dict_list: list[dict[str, Any]] = []
        for receive_order in receive_orders:
            receive_orders_dto: ReceiveOrdersDto = ReceiveOrdersDto.model_validate(
                receive_order)
            receive_orders_dict_list.append(receive_orders_dto.model_dump())
        # 3. down_form_orders 저장
        saved_count = await self.save_down_form_orders_from_receive_orders(
            receive_orders_dict_list,
            template_code
        )
        logger.info(
            f"[END] save_down_form_orders_from_receive_orders_by_filter | saved_count={saved_count}")
        return DownFormOrdersBulkDto(
            success=True,
            template_code=template_code,
            processed_count=len(receive_orders),
            saved_count=saved_count,
            message=f"Successfully processed {len(receive_orders)} records and saved {saved_count} records"
        )

    async def save_receive_orders_to_db(self, filters: dict[str, Any]) -> ReceiveOrdersBulkCreateResponse:
        """
        사방넷 주문수집 데이터 조회 및 저장.
        1. 사방넷에 filters에 따라 주문 데이터를 조회.
        2. 조회된 주문 데이터를 receive_orders 테이블에 저장.
        3. 성공 여부를 반환.
        args:
            filters: filters
        returns:
            receive_orders_saved_success: receive_orders_saved_success
        """
        logger.info(f"[START] save_receive_orders_to_db | filters: {filters}")
        date_from = filters.get('date_from').strftime('%Y%m%d')
        date_to = filters.get('date_to').strftime('%Y%m%d')
        order_status = STATUS_LABEL_TO_CODE[filters.get('order_status')].value
        xml_file_path = self.order_create_service.create_request_xml(
            ord_st_date=date_from,
            ord_ed_date=date_to,
            order_status=order_status
        )
        xml_url = self.order_create_service.get_xml_url_from_minio(
            xml_file_path)
        xml_content = self.order_create_service.get_orders_from_sabangnet(
            xml_url)
        safe_mode = os.getenv("DEPLOY_ENV", "production") != "production"
        receive_orders_saved = await self.order_create_service.save_orders_to_db_from_xml(xml_content, safe_mode)
        logger.info(
            f"[END] save_receive_orders_to_db | receive_orders_saved: {receive_orders_saved}")
        return receive_orders_saved.success

    async def save_down_form_order_from_receive_orders_by_filters_v2(
            self,
            filters: dict[str, Any]
    ) -> DownFormOrdersFromReceiveOrdersDto:
        """
        주문수집 데이터 저장 V2.
        1. 사방넷 주문수집 데이터 조회 -> receive_orders 테이블에 저장.
        2. 저장된 주문수집 데이터 매크로 실행 -> down_form_orders 테이블에 저장.
        3. 성공 여부를 반환.
        args:
            filters: filters
        returns:
            DownFormOrdersFromReceiveOrdersDto
        """
        logger.info(
            f"[START] save_down_form_order_from_receive_orders_by_filters_v2 filters: {filters}")

        # 몰 아이디, 배송구분 추출
        fld_dsp = filters.get('fld_dsp')
        dpartner_id = filters.get('dpartner_id')

        # (임시 주석처리)
        # 1. 주문수집 데이터 조회 및 receive_orders 테이블에 저장
        # receive_orders_saved_success = await self.save_receive_orders_to_db(filters)

        # if not receive_orders_saved_success:
        #     logger.error(f"No receive_orders data saved to receive_orders")
        #     raise ValueError("No receive_orders data saved to receive_orders")

        # 2. filters에 따라 receive_orders 조회
        receive_orders: list[ReceiveOrders] = await self.order_read_service.get_receive_orders_by_filters(filters)
        logger.info(f"receive_orders_len: {len(receive_orders)}")
        if not receive_orders:
            logger.error(f"No receive_orders data found to process")
            raise ValueError("No receive_orders data found to process")

        # 3. receive_orders 데이터를 dto로 변환
        receive_orders_dto_list: list[dict[str, Any]] = []
        for receive_order in receive_orders:
            receive_orders_dto: ReceiveOrdersDto = ReceiveOrdersDto.model_validate(
                receive_order)
            receive_orders_dto_list.append(receive_orders_dto.model_dump())

        # 4. template_code 설정[ERP, 합포장]
        template_code_mapping = {
            '옥션2.0': ('gmarket_erp', 'gmarket_bundle'),
            'G마켓2.0': ('gmarket_erp', 'gmarket_bundle'),
            '브랜디': ('brandi_erp', 'basic_bundle'),
            '지그재그': ('zigzag_erp', 'zigzag_bundle')
        }
        erp_template_code, bundle_template_code = template_code_mapping.get(
            fld_dsp, ('basic_erp', 'basic_bundle'))

        is_star = False
        # 5. 배송구분(일반배송, 스타배송) 설정
        if dpartner_id == '스타배송':
            is_star = True
            erp_template_code = f"star_{erp_template_code}"
            bundle_template_code = f"star_{bundle_template_code}"

        logger.info(
            f"erp_template_code: {erp_template_code} | bundle_template_code: {bundle_template_code}")

        # 6. 매크로 실행 및 down_form_orders 테이블에 저장
        # ERP 매크로 실행
        erp_saved_count = await self.run_macro_to_down_form_order(erp_template_code, receive_orders_dto_list, is_star)
        # 합포장 매크로 실행
        bundle_saved_count = await self.run_macro_to_down_form_order(bundle_template_code, receive_orders_dto_list, is_star)
        saved_count = erp_saved_count + bundle_saved_count
        logger.info(
            f"[END] save_down_form_order_from_receive_orders_by_filters_v2 | saved_count: {saved_count} | erp_saved_count: {erp_saved_count} | bundle_saved_count: {bundle_saved_count}")

        return DownFormOrdersFromReceiveOrdersDto(
            success=True,
            fld_dsp=fld_dsp,
            dpartner_id=dpartner_id,
            processed_count=len(receive_orders),
            saved_count=saved_count,
            message=f"Successfully processed {len(receive_orders)} records and total saved {saved_count} records (erp records : {erp_saved_count} , bundle records : {bundle_saved_count})"
        )

    async def save_down_form_orders_from_receive_orders(
            self,
            raw_data: list[dict[str, Any]],
            template_code: str
    ) -> int:
        """
        메인 프로세스: 원본 데이터(receive_orders 테이블 기반) -> 템플릿별 변환 -> down_form_orders 저장

        Args:
            raw_data: receive_orders 테이블에서 가져온 원본 데이터
            template_code: 적용할 템플릿 코드 (예: 'gmarket_erp')

        Returns:
            저장된 레코드 수
        """
        logger.info(
            f"[START] save_down_form_orders_from_receive_orders | template_code={template_code} | raw_data_count={len(raw_data)}")
        # 1. 템플릿 설정 조회
        config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        if not config:
            logger.error(f"Template not found: {template_code}")
            raise ValueError("Template not found")
        logger.info(f"Loaded template config: {config}")

        # 2. 템플릿에 따라 데이터 변환
        if config['is_aggregated']:
            logger.info(
                "Aggregated template detected. Processing aggregated data.")
            processed_data = await DataProcessingUtils.process_aggregated_data(raw_data, config)
        else:
            logger.info("Simple template detected. Processing simple data.")
            processed_data = await DataProcessingUtils.process_simple_data(raw_data, config)
        logger.info(
            f"Data processed. processed_data_count={len(processed_data)}. Sample: {processed_data[:3]}")

        # 3. down_form_orders에 저장
        saved_count = await self.down_form_order_create_service.save_to_down_form_orders(processed_data, template_code)
        logger.info(
            f"[END] save_down_form_orders_from_receive_orders | saved_count={saved_count}")
        return saved_count

    async def process_excel_to_down_form_orders(
            self,
            df: pd.DataFrame,
            template_code: str,
            work_status: str = None
    ) -> int:
        """
        data frame을 읽어 config 매핑에 따라 데이터를 DB에 저장
        Args:
            df: data frame
            template_code: 템플릿 코드 (gmarket_erp, etc_site_erp ...)
            work_status: 매크로 작업 상태 (macro_run, etc...)
        Returns:
            저장된 레코드 수
        """
        logger.info(
            f"[START] process_excel_to_down_form_orders | template_code={template_code} | df_count={len(df)}")
        # 1. config 매핑 정보 조회
        config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        logger.info(f"Loaded template config: {config}")
        # 2. 엑셀 데이터 변환
        raw_data = await DataProcessingUtils.process_excel_data(df, config, work_status)
        # 3. DB 저장
        saved_count = await self.down_form_order_create_service.save_to_down_form_orders(raw_data, template_code)
        logger.info(
            f"[END] process_excel_to_down_form_orders | saved_count={saved_count}")
        return saved_count

    async def save_down_form_orders_from_receive_orders_without_filter(
            self,
            template_code: str,
            raw_data: list[dict[str, Any]]
    ) -> int:
        """
        save down_form_orders from receive_orders without filter
        args:
            template_code: template code
            raw_data: raw data
        returns:
            saved_count: saved count
        """
        logger.info(f"\
            [START] save_down_form_orders_from_receive_orders_without_filter | \
            template_code={template_code} | \
            raw_data_count={len(raw_data)}"
                    )

        # 1. 템플릿 config 조회
        config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        if not config:
            logger.error(f"Template not found: {template_code}")
            raise ValueError("Template not found")
        logger.info(f"Loaded template config: {config}")

        # 2. 데이터 변환/집계
        processed_data = DataProcessingUtils.transform_data(raw_data, config)
        logger.info(
            f"Data processed. processed_data_count={len(processed_data)}")

        # 3. 저장
        items: list[DownFormOrderDto] = [
            DownFormOrderDto.model_validate(row) for row in processed_data]
        saved_count = await self.down_form_order_create_service.bulk_create_down_form_orders(items)
        logger.info(
            f"[END] save_down_form_orders_from_receive_orders_without_filter | saved_count={saved_count}")
        return saved_count

    async def save_down_form_orders_from_macro_run_excel(self, file: UploadFile, work_status: str = None) -> int:
        """
        save down form orders from macro run excel
        args:
            file: excel file
            work_status: work status
        returns:
            saved_count: saved count
        """
        logger.info(
            f"[START] save_down_form_orders_from_macro_run_excel | file_name={file.filename} ")
        # 1. 파일 이름에서 템플릿 코드 조회
        template_code = await self.find_template_code_by_filename(file.filename)
        logger.info(f"template_code: {template_code}")
        if not template_code:
            raise ValueError(
                f"Template code not found for filename: {file.filename}")

        # 2. 파일명 파싱하여 sub_site 정보 추출
        parsed = self.parse_filename(file.filename)
        sub_site = parsed.get('sub_site')
        logger.info(f"sub_site: {sub_site}")

        # 3. 임시 파일 생성
        file_name, file_path = await self.process_macro_with_tempfile(template_code, file, sub_site)
        logger.info(
            f"temporary file path: {file_path} | file name: {file_name}")
        # 4. 엑셀파일 데이터 파일 변환 후 임시파일 삭제
        dataframe = ExcelHandler.file_path_to_dataframe(file_path)
        logger.info(f"dataframe: {len(dataframe)}")
        # 5. 데이터 저장
        saved_count = await self.process_excel_to_down_form_orders(dataframe, template_code, work_status=work_status)
        logger.info(
            f"[END] save_down_form_orders_from_macro_run_excel | saved_count={saved_count}")
        return saved_count

    async def process_macro_with_tempfile(self, template_code: str, file: UploadFile, sub_site: str = None, is_star: bool = False) -> tuple[str, str]:
        """
        1. 업로드 파일을 임시 파일로 저장
        2. 매크로 실행 (run_macro_with_file)
        3. 임시 파일 삭제
        4. 파일명 반환
        5. (필요시) presigned URL에서 쿼리스트링 제거
        """

        file_name = file.filename
        temp_upload_file_path = temp_file_to_object_name(file)
        try:
            file_path = await self.run_macro_with_file(template_code, temp_upload_file_path, sub_site, is_star)
        finally:
            delete_temp_file(temp_upload_file_path)
        return file_name, file_path

    async def run_macro_with_file(self, template_code: str, file_path: str, sub_site: str = None, is_star: bool = False) -> str:
        """
        1. 템플릿 설정 조회
        2. 템플릿 코드에 해당하는 데이터를 조회하여 매크로 실행
        3. 데이터를 저장하고 저장된 경로를 반환
        """
        logger.info(
            f"run_macro called with template_code={template_code}, file_path={file_path}, sub_site={sub_site}, is_star={is_star}")

        # is_star=True인 경우 B열 사이트 값에 "-스타배송" 추가
        if is_star:
            logger.info(f"스타배송 모드 활성화 - B열 사이트 값 수정 시작")
            file_path = self.order_macro_utils.modify_site_column_for_star_delivery(
                file_path)
            logger.info(f"스타배송 수정 완료: {file_path}")

        # 템플릿 코드로 sub_site 여부 조회
        sub_site_true_template_code = await self.template_config_read_service.get_sub_site_true_template_code(template_code)

        # sub_site가 있으면 해당하는 매크로명 조회, 없으면 기본 매크로명 조회
        # if is_star in ['알리', '지그재그', '기타사이트']:
        if sub_site_true_template_code:
            macro_name: Optional[str] = await self.template_config_read_service.get_macro_name_by_template_code_with_sub_site(template_code, sub_site)
            logger.info(f"macro_name from DB with sub_site: {macro_name}")
        else:
            macro_name: Optional[str] = await self.template_config_read_service.get_macro_name_by_template_code(template_code)
            logger.info(f"macro_name from DB: {macro_name}")
        logger.info(
            f"run_macro called with template_code={template_code}, macro_name: {macro_name}")
        if macro_name:
            macro_func = self.order_macro_utils.MACRO_MAP.get(macro_name)
            if macro_func is None:
                logger.error(f"Macro '{macro_name}' not found in MACRO_MAP.")
                raise ValueError(
                    f"Macro '{macro_name}' not found in MACRO_MAP.")
            try:
                # ERP 매크로와 합포장 매크로를 구분하여 호출
                if macro_name in ["AliMacro", "ZigzagMacro", "BrandiMacro", "ECTSiteMacro", "GmarketAuctionMacro"]:
                    # ERP 매크로: file_path와 is_star 두 개 인자 전달
                    result = macro_func(file_path, is_star)
                else:
                    # 합포장 매크로: file_path 하나만 전달
                    result = macro_func(file_path)
                logger.info(
                    f"Macro '{macro_name}' executed successfully. file_path={result}")
                return result
            except Exception as e:
                logger.error(f"Error running macro '{macro_name}': {e}")
                raise
        else:
            logger.error(f"Macro not found for template code: {template_code}")
            raise ValueError(
                f"Macro not found for template code: {template_code}")

    async def run_macro_to_down_form_order(self, template_code: str, receive_orders_data: list[ReceiveOrders], is_star: bool = False) -> int:
        """
        1. 템플릿 설정 조회
        2. receive_orders 데이터 ERP, 합포장  down_form_order dto로 변경
        3. 매크로 실행
        4. down_form_order 테이블에 저장
        5. 저장된 레코드 수를 반환
        """
        # 1. 템플릿 설정 조회
        logger.info(
            f"run_macro_with_db_v3 called with template_code={template_code}")
        config: dict = await self.template_config_read_service.get_template_config_by_template_code_with_mapping(template_code)
        logger.info(f"Loaded template config: {config}")

        # 2. 데이터 1대1 매핑 변환 (DB_to_DB 에서는 합포장, ERP 구분없이 사용)
        processed_data = await DataProcessingUtils.process_receive_order_data(receive_orders_data, config)
        # 3. 매크로 실행
        run_macro_data: list[dict[str, Any]] = []
        macro_func = self.order_macro_utils.MACRO_MAP_V3.get(template_code)
        if macro_func:
            if template_code == 'zigzag_erp' or template_code == 'zigzag_bundle':
                processed_vlookup_data = await self.vlookup_data_processing(processed_data)
                run_macro_data = macro_func(processed_vlookup_data, is_star)
            else:
                run_macro_data = macro_func(processed_data, is_star)
        else:
            logger.error(f"Macro not found for template code: {template_code}")
            raise ValueError(
                f"Macro not found for template code: {template_code}")

        logger.info(f"{template_code} run_macro_data: {run_macro_data[:1]}")
        # 4. down_form_orders 저장
        try:
            saved_count = await self.down_form_order_create_service.bulk_create_down_form_orders_with_dict(run_macro_data)
            logger.info(
                f"Saved {saved_count} records to down_form_order table with work_status=macro_run and template_code={template_code}")
            return saved_count
        except Exception as e:
            logger.error(f"Error running {template_code} macro with db: {e}")
            raise

    async def vlookup_data_processing(self, processed_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        vlookup 데이터 처리
        """
        logger.info(f"[START] VLOOKUP DATA PROCESSING")
        mall_product_id_dict = {}
        # 상품코드 배송비 추출
        for item in processed_data:
            mall_product_id = item.get('mall_product_id')
            if mall_product_id:
                mall_product_id_dict[mall_product_id] = {
                    'mall_product_id': mall_product_id,
                    'delv_cost': item.get('delv_cost')
                }
        logger.info(f"mall_product_id_dict len: {len(mall_product_id_dict)}")
        # vlookup 데이터 조회
        vlookup_datas = await self.vlookup_datas_read_service.get_vlookup_datas_with_not_found_mall_product_ids(mall_product_id_dict.keys())
        found_datas = vlookup_datas.get('found_datas', {})
        not_found_datas = vlookup_datas.get('not_found_datas', [])
        logger.info(
            f"found_datas len: {len(found_datas)} | not_found_datas len: {len(not_found_datas)}")

        # 조회되지 않은 데이터 vlookup_datas 테이블에 추가
        if not_found_datas:
            not_found_data_list: list[dict] = [
                mall_product_id_dict.get(item) for item in not_found_datas]
            saved_count_vlookup_datas = await self.vlookup_datas_create_service.saved_count_bulk_create_vlookup_datas(not_found_data_list)
            logger.info(
                f"saved_count_vlookup_datas: {saved_count_vlookup_datas['saved_count']}")

        # 조회된 데이터 추가
        if found_datas:
            for item in processed_data:
                mall_product_id = item.get('mall_product_id')
                if mall_product_id and mall_product_id in found_datas:
                    item['delv_cost'] = found_datas[mall_product_id]['delv_cost']
        logger.info(f"[END] VLOOKUP DATA PROCESSING")
        return processed_data

    async def run_macro_with_db(self, template_code: str) -> int:
        """
        1. DB 에서 템플릿 코드에 해당하는 데이터를 조회하여 매크로 실행
        2. 데이터를 저장 (down_form_order 테이블)
        3. 저장된 레코드 수를 반환
        """
        logger.info(f"run_macro called with template_code={template_code}")

        # 1. 템플릿 설정 조회 -> 실제로 안쓰고 있는?
        config: dict = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        logger.info(f"Loaded template config: {config}")

        # 2. db 데이터를 템플릿에 따라 df 데이터 run_macro 실행 (preprocess_order_data)
        down_order_data: list[DownFormOrderDto] = (
            await self.down_form_order_read_service.
            get_down_form_orders_by_template_code(template_code)
        )
        processed_orders: list[dict[str, Any]] = self.order_macro_utils.process_orders_for_db(
            down_order_data)

        # 3. processed_orders 데이터를 "down_form_order" 테이블에 저장 후 성공한 레코드 수 반환
        try:
            len_saved = await self.down_form_order_create_service.bulk_create_down_form_orders_with_dict(processed_orders)
            logger.info(
                f"Saved {len_saved} records to down_form_order table with work_status=macro_run")

            return len_saved
        except Exception as e:
            logger.error(f"Error running macro with db: {e}")
            raise

    async def export_down_form_orders_to_excel_by_work_status(self, template_code: str, work_status: str = None) -> str:
        """
        export down_form_orders to excel by work_status
        args:
            template_code: template code
            work_status: work status
        returns:
            file_path: file path
            file_name: file name
        """
        logger.info(
            f"[START] get_down_form_orders_by_work_status | template_code={template_code} ")
        # 1. 데이터 조회
        down_form_orders: list[BaseDownFormOrder] = await self.down_form_order_read_service.get_down_form_orders_by_work_status(work_status)
        logger.info(f"down_form_orders: {len(down_form_orders)}")
        # 2. 템플릿 설정 조회
        template_config: dict = await self.template_config_read_service.get_template_config_by_template_code(template_code=template_code)
        logger.info(f"template_config: {template_config}")
        # 3. 매핑 필드 생성
        mapping_field: dict = await DataProcessingUtils.create_mapping_field(template_config)
        logger.info(f"mapping_field: {mapping_field}")
        # 4. 엑셀 파일 생성
        file_name = f"{template_code}_{work_status}.xlsx"
        convert_xlsx = ConvertXlsx()
        temp_file_path = convert_xlsx.export_temp_excel(
            down_form_orders,
            mapping_field,
            file_name
        )
        logger.info(f"\
            [END] get_down_form_orders_by_work_status | \
            temp_file_path={temp_file_path} | \
            file_name={file_name}"
                    )
        return temp_file_path, file_name

    async def _process_file_basic(self, file: UploadFile) -> dict[str, Any]:
        """
        기본 파일 처리 로직 (DB 저장만)
        args:
            file: file
        returns:
            dict: {"filename": str, "saved_count": int}
        """
        try:
            saved_count = await self.save_down_form_orders_from_macro_run_excel(
                file, work_status="macro_run"
            )
            return {"filename": file.filename, "saved_count": saved_count}
        except Exception as e:
            return {"filename": file.filename, "error": str(e)}

    async def _process_file_with_batch(
        self,
        file: UploadFile,
        request_obj: BatchProcessRequest
    ) -> dict[str, Any]:
        """
        배치 정보와 함께 파일 처리 로직 (DB 저장 + MinIO 업로드)
        args:
            file: file
            request_obj: request object
        returns:
            dict: {"filename": str, "saved_count": int, "template_code": str, "batch_id": str, "file_url": str}
        """
        original_filename = file.filename
        logger.info(f"original_filename={original_filename}")
        try:
            # 1. 파일 이름에서 템플릿 코드 조회
            template_code = await self.find_template_code_by_filename(original_filename)
            logger.info(f"template_code: {template_code}")
            if not template_code:
                raise ValueError(
                    f"Template code not found for filename: {original_filename}")

            # 2. 파일명 파싱하여 sub_site 정보 추출
            parsed = self.parse_filename(original_filename)
            sub_site = parsed.get('sub_site')
            is_star = parsed.get('is_star')
            logger.info(f"sub_site: {sub_site} | is_star: {is_star}")

            # 3. 임시 파일 생성 및 매크로 실행
            file_name, file_path = await self.process_macro_with_tempfile(template_code, file, sub_site, is_star)
            logger.info(
                f"temporary file path: {file_path} | file name: {file_name}")
            ex = ExcelHandler.from_file(file_path, sheet_index=0)
            # 4. 도서지역 배송비 추가
            ex.add_island_delivery(ex.wb)

            # 5. 템플릿 코드 추가
            ex.create_template_code_in_excel(template_code)
            new_file_path = ex.save_file(file_path)
            dataframe = ex.to_dataframe()

            # 6. down_form_order 테이블에 저장
            saved_count = await self.process_excel_to_down_form_orders(dataframe, template_code, work_status="macro_run")
            logger.info(f"saved_count: {saved_count}")

            # 6. 파일 업로드 및 batch 저장
            file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                new_file_path, template_code, file_name)
            file_url = url_arrange(file_url)

            batch_id = await self.batch_info_create_service.build_and_save_batch(
                BatchProcessDto.build_success,
                original_filename,
                file_url,
                file_size,
                request_obj
            )
            return {
                "filename": original_filename,
                "saved_count": saved_count,
                "template_code": template_code,
                "batch_id": batch_id,
                "file_url": file_url,
                "minio_object_name": minio_object_name
            }
        except Exception as e:
            batch_id = await self.batch_info_create_service.build_and_save_batch(
                BatchProcessDto.build_error,
                file.filename,
                request_obj,
                str(e)
            )
            return {
                "filename": original_filename,
                "template_code": template_code,
                "batch_id": batch_id,
                "error_message": str(e)
            }

    async def bulk_save_down_form_orders_from_macro_run_excel(
        self,
        files: list[UploadFile]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
        """
        bulk save down form orders from macro run excel
        args:
            files: list of files
        returns:
            successful_results: list of successful results
            failed_results: list of failed results
            total_saved_count: total saved count
        """
        logger.info(
            f"[START] bulk_save_down_form_orders_from_macro_run_excel | file_count={len(files)}")

        successful_results: list[dict[str, Any]] = []
        failed_results: list[dict[str, Any]] = []
        total_saved_count: int = 0

        for file in files:
            result: dict[str, Any] = await self._process_file_basic(file)
            saved_count = result.get('saved_count')
            if saved_count:
                successful_results.append(result)
                total_saved_count += saved_count
            else:
                failed_results.append(result)
            logger.info(f"result: {result}")

        logger.info(
            f"[END] bulk_save_down_form_orders_from_macro_run_excel | successful_results={successful_results} | failed_results={failed_results} | total_saved_count={total_saved_count}")
        return successful_results, failed_results, total_saved_count

    async def bulk_get_excel_run_macro_minio_url_and_save_db(
        self,
        files: list[UploadFile],
        request_obj: BatchProcessRequest
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
        """
        bulk get excel run macro minio url and save db
        args:
            files: list of files
            request_obj: batch process request object
        returns:
            successful_results: list of successful results
            failed_results: list of failed results
            total_saved_count: total saved count
        """
        logger.info(
            f"[START] bulk_get_excel_run_macro_minio_url_and_save_db | file_count={len(files)}")

        successful_results: list[dict[str, Any]] = []
        failed_results: list[dict[str, Any]] = []
        total_saved_count: int = 0

        for file in files:
            result: dict[str, Any] = await self._process_file_with_batch(file, request_obj)
            saved_count = result.get('saved_count')
            if saved_count:
                successful_results.append(result)
                total_saved_count += saved_count
            else:
                failed_results.append(result)
            logger.info(f"result: {result}")

        logger.info(
            f"[END] bulk_get_excel_run_macro_minio_url_and_save_db | successful_results={successful_results} | failed_results={failed_results} | total_saved_count={total_saved_count}")
        return successful_results, failed_results, total_saved_count

    async def find_template_code_by_filename(self, file_name: str) -> str:
        """
        파일명을 파싱하여 템플릿 코드를 찾는 개선된 메서드
        args:
            file_name: 파일명
        returns:
            template_code: 템플릿 코드
        """
        # 파일명 파싱
        parsed = self.parse_filename(file_name)
        logger.info(f"Parsed filename: {parsed}")

        # site_type, usage_type, is_star를 기반으로 DB에서 직접 조회
        site_type = parsed.get('site_type')
        usage_type = parsed.get('usage_type')
        is_star = parsed.get('is_star')

        if site_type and usage_type:
            template_code = await self.export_templates_read_service.find_template_code_by_site_usage_star(
                site_type, usage_type, is_star
            )

            if template_code:
                logger.info(
                    f"Found template_code: {template_code} for filename: {file_name}")
                return template_code

        logger.warning(f"No template found for filename: {file_name}")
        return None

    def _match_template_by_parsed_info(self, template_name: str, parsed: dict[str, Any]) -> bool:
        """
        파싱된 파일명 정보와 템플릿명을 매칭
        args:
            template_name: 템플릿명
            parsed: 파싱된 파일명 정보
        returns:
            bool: 매칭 여부
        """
        # 스타배송 여부 확인
        if parsed.get('is_star') and '스타배송' not in template_name:
            return False
        if not parsed.get('is_star') and '스타배송' in template_name:
            return False

        # 용도타입 매칭
        usage_type = parsed.get('usage_type', '')
        if 'ERP용' in usage_type and 'ERP용' not in template_name:
            return False
        if '합포장용' in usage_type and '합포장용' not in template_name:
            return False

        # 사이트타입 매칭
        site_type = parsed.get('site_type', '')
        if site_type:
            # 쉼표로 구분된 사이트타입들을 개별적으로 확인
            site_types = [s.strip() for s in site_type.split(',')]
            for site in site_types:
                if site in template_name:
                    return True

            # basic_erp 특별 처리: 기본양식이면서 ERP용인 경우
            if site_type == "기본양식" and "ERP용" in usage_type and "알리 지그재그 기타사이트 ERP용" in template_name:
                return True

        return False

    async def get_excel_run_macro_minio_url(self, file: UploadFile, request_obj: BatchProcessRequest) -> dict[str, Any]:
        """
        get excel run macro minio url
        args:
            file: file
            request_obj: request object
        returns:
            dict: {"success": bool, "template_code": str, "batch_id": str, "file_url": str, "minio_object_name": str}
        """
        original_filename = file.filename
        logger.info(
            f"[START] get_excel_run_macro_minio_url | file_name={original_filename}")
        # 1. 파일 이름에서 템플릿 코드 조회
        template_code: str = await self.find_template_code_by_filename(file.filename)

        if not template_code:
            raise ValueError(
                f"Template code not found for filename: {file.filename}")
        logger.info(f"template_code: {template_code}")

        # 2. 파일명 파싱하여 sub_site 정보 추출
        parsed = self.parse_filename(file.filename)
        sub_site = parsed.get('sub_site')
        logger.info(f"sub_site: {sub_site}")

        # 3. 파일 처리
        try:
            file_name, file_path = await self.process_macro_with_tempfile(template_code, file, sub_site)
            logger.info(f"file_name: {file_name} | file_path: {file_path}")

            # 4. 도서지역 배송비 추가
            ex = ExcelHandler.from_file(file_path, sheet_index=0)
            ex.add_island_delivery(ex.wb)
            file_path = ex.save_file(file_path)

            file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                file_path, template_code, file_name)
            file_url = url_arrange(file_url)
            batch_id = await self.batch_info_create_service.build_and_save_batch(
                BatchProcessDto.build_success,
                original_filename,
                file_url,
                file_size,
                request_obj
            )
            logger.info(
                f"[END] get_excel_run_macro_minio_url | \
                template_code: {template_code} | \
                batch_id: {batch_id} | \
                file_url: {file_url} | \
                minio_object_name: {minio_object_name}"
            )
            return {
                "success": True,
                "template_code": template_code,
                "batch_id": batch_id,
                "file_url": file_url,
                "minio_object_name": minio_object_name
            }
        except Exception as e:
            batch_id = await self.batch_info_create_service.build_and_save_batch(
                BatchProcessDto.build_error,
                original_filename,
                request_obj,
                str(e)
            )
            logger.info(
                f"[END] get_excel_run_macro_minio_url | \
                template_code: {template_code} | \
                batch_id: {batch_id} | \
                error_message: {str(e)}"
            )
            return {
                "success": False,
                "template_code": template_code,
                "batch_id": batch_id,
                "error_message": str(e)
            }
