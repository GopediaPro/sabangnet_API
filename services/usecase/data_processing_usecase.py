# std
from typing import Any
from datetime import datetime
# util
from utils.excels.convert_xlsx import ConvertXlsx
from utils.logs.sabangnet_logger import get_logger
from utils.excels.excel_handler import ExcelHandler
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# model
from models.receive_orders.receive_orders import ReceiveOrders
from models.down_form_orders.down_form_order import BaseDownFormOrder
# schema
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto, DownFormOrdersBulkDto
# service
from services.macro.order_macro_service import process_macro_with_tempfile
from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
from services.down_form_orders.template_config_read_service import TemplateConfigReadService
from services.down_form_orders.down_form_order_create_service import DownFormOrderCreateService
# schema
from schemas.down_form_orders.down_form_order_mapper import map_raw_to_down_form, map_aggregated_to_down_form, map_excel_to_down_form


logger = get_logger(__name__)


class DataProcessingFunctions:
    """
    작업 처리용 클래스 (밑에 있는 DataProcessingUsecase 클래스가 이 클래스를 상속받아서 사용)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def _convert_delivery_method(self, value: Any, context: dict[str, Any]) -> str:
        if not value:
            return ""
        mapping = {"credit": "선불", "cod": "착불", "prepaid": "선불"}
        return mapping.get(str(value).lower(), str(value))

    def _sku_quantity(self, value: Any, context: dict[str, Any]) -> str:
        sku_alias = context.get('sku_alias', '') or value or ''
        sale_cnt = context.get('sale_cnt', 0) or 0
        return f"{sku_alias} {sale_cnt}개" if sku_alias else ""

    def _barcode_quantity(self, value: Any, context: dict[str, Any]) -> str:
        barcode = context.get('barcode', '') or value or ''
        sale_cnt = context.get('sale_cnt', 0) or 0
        return f"{barcode} {sale_cnt}개" if barcode else ""

    def _calculate_service_fee(self, value: Any, context: dict[str, Any]) -> int:
        pay_cost = context.get('pay_cost', 0) or 0
        mall_won_cost = context.get('mall_won_cost', 0) or 0
        sale_cnt = context.get('sale_cnt', 0) or 0
        return int(pay_cost - (mall_won_cost * sale_cnt))

    def _transform_data(self, raw_data: list[dict[str, Any]], config: dict) -> list[dict[str, Any]]:
        processed_data = []
        if config.get('is_aggregated'):
            group_by = config.get('group_by_fields', [])
            grouped = {}
            for row in raw_data:
                key = tuple(row.get(f) for f in group_by)
                grouped.setdefault(key, []).append(row)
            for seq, (key, group_rows) in enumerate(grouped.items(), start=1):
                base = {
                    'process_dt': datetime.now(),
                    'form_name': config['template_code'],
                    'seq': seq,
                }
                base.update(map_aggregated_to_down_form(group_rows, config))
                processed_data.append(base)
        else:
            for seq, row in enumerate(raw_data, start=1):
                base = {
                    'process_dt': datetime.now(),
                    'form_name': config['template_code'],
                    'seq': seq,
                }
                base.update(map_raw_to_down_form(row, config))
                processed_data.append(base)
        return processed_data

    async def _create_mapping_field(self, template_config: dict) -> dict:
        """
        create mapping field
        args:
            template_config: 전체 템플릿 설정 (column_mappings 포함)
        returns:
            mapping_field: mapping field {"순번": "seq","사이트": "fld_dsp"...}
        """
        mapping_field = {}
        for col in template_config["column_mappings"]:
            mapping_field[col["target_column"]] = col["source_field"]
        return mapping_field

    async def _process_simple_data(
        self,
        raw_data: list[dict[str, Any]],
        config: dict
    ) -> list[dict[str, Any]]:
        """단순 변환 (1:1 매핑)"""
        processed_data = []
        for seq, raw_row in enumerate(raw_data, start=1):
            processed_row = {
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
            }
            processed_row.update(map_raw_to_down_form(raw_row, config))
            processed_data.append(processed_row)
        return processed_data

    async def _process_aggregated_data(
        self,
        raw_data: list[dict[str, Any]],
        config: dict
    ) -> list[dict[str, Any]]:
        """집계 변환 (합포장용)"""
        grouped_data = {}
        group_field_mapping = {
            'order_id': 'order_id',
            'receive_name': 'receive_name',
            'receive_addr': 'receive_addr'
        }
        for raw_row in raw_data:
            group_key = tuple(
                raw_row.get(group_field_mapping.get(field, field), '')
                for field in config['group_by_fields']
            )
            if group_key not in grouped_data:
                grouped_data[group_key] = []
            grouped_data[group_key].append(raw_row)
        processed_data = []
        for seq, (group_key, group_rows) in enumerate(grouped_data.items(), start=1):
            processed_row = {
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
            }
            processed_row.update(
                map_aggregated_to_down_form(group_rows, config))
            processed_data.append(processed_row)
        return processed_data

    async def _save_to_down_form_orders(self, processed_data: list[dict[str, Any]], template_code: str) -> int:
        logger.info(
            f"[START] _save_to_down_form_orders | processed_data_count={len(processed_data)} | template_code={template_code}")
        if not processed_data:
            logger.warning("No processed data to save.")
            return 0
        try:
            objects = [BaseDownFormOrder(**row) for row in processed_data]
            self.session.add_all(objects)
            await self.session.commit()
            logger.info(
                f"[END] _save_to_down_form_orders | saved_count={len(objects)}")
            return len(objects)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Exception during _save_to_down_form_orders: {e}")
            raise

    async def _process_excel_data(self, df, config, work_status: str = None) -> list[dict[str, Any]]:
        """
        DataFrame과 config(column_mappings)를 받아 DB 저장용 dict 리스트로 변환
        """
        raw_data = map_excel_to_down_form(df, config)
        processed_data = []
        for seq, raw_row in enumerate(raw_data, start=1):
            processed_row = raw_row.copy()
            processed_row.update({
                'process_dt': datetime.now(),
                'form_name': config['template_code'],
                'seq': seq,
                'work_status': work_status,
            })
            processed_data.append(processed_row)
        return processed_data


"""
아래부터 메인 프로세스 클래스
DataProcessingFunctions 클래스를 상속받아서 사용
실제 유저의 요청을 받아서 처리함
"""


class DataProcessingUsecase(DataProcessingFunctions):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.order_read_service = ReceiveOrderReadService(session)
        self.down_form_order_read_service = DownFormOrderReadService(session)
        self.down_form_order_create_service = DownFormOrderCreateService(
            session)
        self.template_config_read_service = TemplateConfigReadService(session)

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
        template_config = await self.get_template_config_by_template_code(template_code)
        down_form_orders = await self.get_down_form_orders_by_template_code(template_code)

        mapping_field = await self._create_mapping_field(template_config)

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

    async def save_down_form_orders_from_receive_orders_by_filter(self, filters: dict[str, Any], template_code: str) -> DownFormOrdersBulkDto:
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

    async def save_down_form_orders_from_receive_orders(
        self,
        raw_data: list[dict[str, Any]],
        template_code: str
    ) -> int:
        logger.info(
            f"[START] save_down_form_orders_from_receive_orders | template_code={template_code} | raw_data_count={len(raw_data)}")
        """
        메인 프로세스: 원본 데이터(receive_orders 테이블 기반) -> 템플릿별 변환 -> down_form_orders 저장
        
        Args:
            raw_data: receive_orders 테이블에서 가져온 원본 데이터
            template_code: 적용할 템플릿 코드 (예: 'gmarket_erp')
        
        Returns:
            저장된 레코드 수
        """

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
            processed_data = await self._process_aggregated_data(raw_data, config)
        else:
            logger.info("Simple template detected. Processing simple data.")
            processed_data = await self._process_simple_data(raw_data, config)
        logger.info(
            f"Data processed. processed_data_count={len(processed_data)}. Sample: {processed_data[:3]}")

        # 3. down_form_orders에 저장
        saved_count = await self._save_to_down_form_orders(processed_data, template_code)
        logger.info(
            f"[END] save_down_form_orders_from_receive_orders | saved_count={saved_count}")
        return saved_count

    async def process_excel_to_down_form_orders(self, df, template_code: str, work_status: str = None) -> int:
        """
        Excel 파일을 읽어 config 매핑에 따라 데이터를 DB에 저장
        Args:
            df: Excel 파일 DataFrame
            template_code: 템플릿 코드
        Returns:
            저장된 레코드 수
        """
        logger.info(
            f"[START] process_excel_to_down_form_orders | template_code={template_code} | df_count={len(df)}")
        # 1. config 매핑 정보 조회
        config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        logger.info(f"Loaded template config: {config}")
        # 2. 엑셀 데이터 변환
        raw_data = await self._process_excel_data(df, config, work_status)
        # 3. DB 저장
        saved_count = await self._save_to_down_form_orders(raw_data, template_code)
        logger.info(
            f"[END] process_excel_to_down_form_orders | saved_count={saved_count}")
        return saved_count

    async def save_down_form_orders_from_receive_orders_without_filter(self, template_code: str, raw_data: list[dict[str, Any]]) -> int:
        """
        save down_form_orders from receive_orders without filter
        args:
            template_code: template code
            raw_data: raw data
        returns:
            saved_count: saved count
        """
        logger.info(
            f"[START] save_down_form_orders_from_receive_orders_without_filter | template_code={template_code} | raw_data_count={len(raw_data)}")

        # 1. 템플릿 config 조회
        config = await self.template_config_read_service.get_template_config_by_template_code(template_code)
        if not config:
            logger.error(f"Template not found: {template_code}")
            raise ValueError("Template not found")
        logger.info(f"Loaded template config: {config}")

        # 2. 데이터 변환/집계
        processed_data = self._transform_data(raw_data, config)
        logger.info(
            f"Data processed. processed_data_count={len(processed_data)}")

        # 3. 저장
        items: list[DownFormOrderDto] = [
            DownFormOrderDto.model_validate(row) for row in processed_data]
        try:
            saved_count = await self.down_form_order_create_service.bulk_create_down_form_orders(items)
            logger.info(f"[END] process_and_save | saved_count={saved_count}")
            return saved_count
        except Exception as e:
            await self.session.rollback()
            logger.error(f"DB Error: {e}")
            raise

    async def save_down_form_orders_from_macro_run_excel(self, file, template_code: str, work_status: str = None) -> int:
        """
        save down form orders from macro run excel
        args:
            file: excel file
            template_code: template code
            work_status: work status
        returns:
            saved_count: saved count
        """
        logger.info(
            f"[START] save_down_form_orders_from_macro_run_excel | template_code={template_code} ")
        # 1. 임시 파일 생성
        file_name, file_path = await process_macro_with_tempfile(self.session, template_code, file)
        logger.info(f"temporary file path: {file_path}, file name: {file_name}")
        # 2. 엑셀파일 데이터 파일 변환 후 임시파일 삭제
        dataframe = ExcelHandler.file_path_to_dataframe(file_path)
        logger.info(f"dataframe: {len(dataframe)}")
        # # 3. 데이터 저장
        saved_count = await self.process_excel_to_down_form_orders(dataframe, template_code, work_status=work_status)
        logger.info(
            f"[END] save_down_form_orders_from_macro_run_excel | saved_count={saved_count}")
        return saved_count

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
        down_form_orders = await self.down_form_order_read_service.get_down_form_orders_by_work_status(work_status)
        logger.info(f"down_form_orders: {len(down_form_orders)}")
        # 2. 템플릿 설정 조회
        template_config = await self.get_template_config_by_template_code(template_code)
        logger.info(f"template_config: {template_config}")
        # 3. 매핑 필드 생성
        mapping_field = await self._create_mapping_field(template_config)
        logger.info(f"mapping_field: {mapping_field}")
        # 4. 엑셀 파일 생성
        file_name = f"{template_code}_{work_status}.xlsx"
        convert_xlsx = ConvertXlsx()
        temp_file_path = convert_xlsx.export_temp_excel(
            down_form_orders, mapping_field, file_name)
        logger.info(
            f"[END] get_down_form_orders_by_work_status | temp_file_path={temp_file_path} | file_name={file_name}")
        return temp_file_path, file_name