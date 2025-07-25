# std
import asyncio
import unicodedata
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
# sql
from sqlalchemy.ext.asyncio import AsyncSession
# model
from models.receive_orders.receive_orders import ReceiveOrders
from models.down_form_orders.down_form_order import BaseDownFormOrder
# schema
from schemas.receive_orders.receive_orders_dto import ReceiveOrdersDto
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto, DownFormOrdersBulkDto
# service
from services.receive_orders.receive_order_read_service import ReceiveOrderReadService
from services.down_form_orders.down_form_order_read_service import DownFormOrderReadService
from services.down_form_orders.template_config_read_service import TemplateConfigReadService
from services.down_form_orders.down_form_order_create_service import DownFormOrderCreateService
from services.export_templates.export_templates_read_service import ExportTemplatesReadService
# file
from minio_handler import temp_file_to_object_name, delete_temp_file


logger = get_logger(__name__)


class DataProcessingUsecase:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_macro_utils = OrderMacroUtils()
        self.order_read_service = ReceiveOrderReadService(session)
        self.template_config_read_service = TemplateConfigReadService(session)
        self.down_form_order_read_service = DownFormOrderReadService(session)
        self.down_form_order_create_service = DownFormOrderCreateService(session)
        self.export_templates_read_service = ExportTemplatesReadService(session)
        
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
        
        logger.info(f"[START] save_down_form_orders_from_receive_orders_by_filter | template_code={template_code} | filters={filters}")
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
        logger.info(f"[START] process_excel_to_down_form_orders | template_code={template_code} | df_count={len(df)}")
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
        logger.info(f"Data processed. processed_data_count={len(processed_data)}")

        # 3. 저장
        items: list[DownFormOrderDto] = [DownFormOrderDto.model_validate(row) for row in processed_data]
        saved_count = await self.down_form_order_create_service.bulk_create_down_form_orders(items)
        logger.info(f"[END] save_down_form_orders_from_receive_orders_without_filter | saved_count={saved_count}")
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
        logger.info(f"[START] save_down_form_orders_from_macro_run_excel | file_name={file.filename} ")
        # 1. 파일 이름에서 템플릿 코드 조회
        try:
            template_code = await self.find_template_code_by_filename(file.filename)
            logger.info(f"template_code: {template_code}")
        except Exception as e:
            logger.error(f"Template not found: {file.filename} | error: {e}")
            raise
        # 2. 임시 파일 생성
        file_name, file_path = await self.process_macro_with_tempfile(template_code, file)
        logger.info(f"temporary file path: {file_path} | file name: {file_name}")
        # 3. 엑셀파일 데이터 파일 변환 후 임시파일 삭제
        dataframe = ExcelHandler.file_path_to_dataframe(file_path)
        logger.info(f"dataframe: {len(dataframe)}")
        # 4. 데이터 저장
        saved_count = await self.process_excel_to_down_form_orders(dataframe, template_code, work_status=work_status)
        logger.info(f"[END] save_down_form_orders_from_macro_run_excel | saved_count={saved_count}")
        return saved_count

    async def process_macro_with_tempfile(self, template_code: str, file: UploadFile) -> tuple[str, str]:
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
            file_path = await self.run_macro_with_file(template_code, temp_upload_file_path)
        finally:
            delete_temp_file(temp_upload_file_path)
        return file_name, file_path

    async def run_macro_with_file(self, template_code: str, file_path: str) -> str:
        """
        1. 템플릿 설정 조회
        2. 템플릿 코드에 해당하는 데이터를 조회하여 매크로 실행
        3. 데이터를 저장하고 저장된 경로를 반환
        """
        logger.info(f"run_macro called with template_code={template_code}, file_path={file_path}")

        macro_name: Optional[str] = await self.template_config_read_service.get_macro_name_by_template_code(template_code)
        logger.info(f"macro_name from DB: {macro_name}")

        if macro_name:
            macro_func = self.order_macro_utils.MACRO_MAP.get(macro_name)
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
        processed_orders: list[dict[str, Any]] = self.order_macro_utils.process_orders_for_db(down_order_data)

        # 3. processed_orders 데이터를 "down_form_order" 테이블에 저장 후 성공한 레코드 수 반환
        try:
            len_saved = await self.down_form_order_create_service.bulk_create_down_form_orders_with_dict(processed_orders)
            logger.info(f"Saved {len_saved} records to down_form_order table with work_status=macro_run")
            
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
        logger.info(f"[START] get_down_form_orders_by_work_status | template_code={template_code} ")
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
        logger.info(f"[START] bulk_save_down_form_orders_from_macro_run_excel | file_count={len(files)}")
        # 1. 세마포어 설정
        semaphore = asyncio.Semaphore(5) # 최대 5개 작업 동시 실행
        successful_results: list[dict[str, Any]] = []
        failed_results: list[dict[str, Any]] = []
        total_saved_count: int = 0
        # 2. 파일 처리
        for file in files:
            result: dict[str, Any] = await self._process_file(file, semaphore)
            saved_count = result.get('saved_count')
            if saved_count:
                successful_results.append(result)
                total_saved_count += saved_count
            else:
                failed_results.append(result)
            logger.info(f"result: {result}")
        logger.info(f"\
            [END] bulk_save_down_form_orders_from_macro_run_excel | \
            successful_results={successful_results} | \
            failed_results={failed_results} | \
            total_saved_count={total_saved_count}"
        )
        return successful_results, failed_results, total_saved_count

    async def _process_file(self, file: UploadFile, semaphore: asyncio.Semaphore) -> dict[str, Any]:
        """
        네임스페이스 분리를 위해 비동기 함수로 만들어짐
        args:
            file: file
            semaphore: semaphore for concurrency control
        returns:
            dict: {"filename": str, "saved_count": int} or {"filename": str, "error": str}
        """
        async with semaphore:
            try:
                saved_count = await self.save_down_form_orders_from_macro_run_excel(
                    file, work_status="macro_run"
                )
                return {"filename": file.filename, "saved_count": saved_count}
            except Exception as e:
                return {"filename": file.filename, "error": str(e)}

    async def find_template_code_by_filename(self, file_name: str) -> str:
        template_list: list[dict[str, str]] = await self.export_templates_read_service.get_export_templates_code_and_name()
        # 입력한 파일 데이터 정규화 -> 조합형(NFC) 형식으로 변환
        file_name = unicodedata.normalize('NFC', file_name)
        for template in template_list:
            template_name = template.get('template_name', '').split(' ')
            try:
                # basic_erp 알리, 브랜디, 기타사이트 구분용
                if len(template_name) > 2:
                    site_names:str = ' '.join(template_name[:-1])
                    temp_type:str = template_name[-1]
                    if any(site_name in file_name for site_name in site_names) and temp_type in file_name:
                        return template.get('template_code')
                if len(template_name) <= 2:
                    site_name:str = template_name[0]
                    # ERP, 합포장 구분
                    temp_type:str = template_name[1]
                    if site_name in file_name and temp_type in file_name:
                        return template.get('template_code')
            except Exception as e:
                logger.error(f"Error template_name: {e}")
                continue
        return None