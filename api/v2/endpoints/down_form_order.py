# std
from typing import Optional
from datetime import date, datetime
import pandas as pd
import tempfile
import os
import zipfile

# core
from core.db import get_async_session

# sql
from sqlalchemy.ext.asyncio import AsyncSession

# fastapi
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse

# service
from services.usecase.data_processing_usecase import DataProcessingUsecase
from services.down_form_orders.down_form_order_read_service import (
    DownFormOrderReadService,
)
from services.down_form_orders.down_form_order_update_service import (
    DownFormOrderUpdateService,
)
from services.down_form_orders.down_form_order_conversion_service import (
    DownFormOrderConversionService,
)

# schema
from schemas.integration_request import IntegrationRequest
from schemas.integration_response import ResponseHandler, Metadata
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto
from schemas.down_form_orders.request.down_form_orders_request import DbToExcelRequest
from schemas.down_form_orders.response.down_form_orders_response import DbToExcelResponse, ExcelToDbResponse

# utils
from utils.excels.excel_handler import ExcelHandler
from utils.logs.sabangnet_logger import get_logger

# minio
from minio_handler import upload_and_get_url_and_size, url_arrange

logger = get_logger(__name__)

router = APIRouter(
    prefix="/down-form-orders",
    tags=["down-form-orders-v2"],
)


# Dependency
def get_down_form_order_read_service(
    session: AsyncSession = Depends(get_async_session),
) -> DownFormOrderReadService:
    return DownFormOrderReadService(session)


def get_down_form_order_update_service(
    session: AsyncSession = Depends(get_async_session),
) -> DownFormOrderUpdateService:
    return DownFormOrderUpdateService(session)


def get_data_processing_usecase(
    session: AsyncSession = Depends(get_async_session),
) -> DataProcessingUsecase:
    return DataProcessingUsecase(session)


def get_down_form_order_conversion_service(
    session: AsyncSession = Depends(get_async_session),
) -> DownFormOrderConversionService:
    return DownFormOrderConversionService(session)





@router.post("/db-to-excel-url", response_class=JSONResponse)
async def db_to_excel_url(
    request: IntegrationRequest[DbToExcelRequest],
    down_form_order_read_service: DownFormOrderReadService = Depends(
        get_down_form_order_read_service
    ),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase
    ),
    down_form_order_conversion_service: DownFormOrderConversionService = Depends(
        get_down_form_order_conversion_service
    ),
):
    """
    DB에서 날짜 범위로 down_form_orders 데이터를 조회하여 Excel 파일로 변환 후 URL 반환
    """
    try:
        logger.info(f"[db_to_excel_url] 시작 - 요청 데이터: {request.data}")

        ord_st_date = request.data.ord_st_date
        ord_ed_date = request.data.ord_ed_date
        form_names = request.data.form_names

        # 날짜, 양식 이름으로 데이터 조회
        down_form_orders = (
            await down_form_order_read_service.get_down_form_orders_by_date_range(
                date_from=ord_st_date, date_to=ord_ed_date, form_names=form_names
            )
        )

        if not down_form_orders:
            return ResponseHandler.ok(
                data=DbToExcelResponse(excel_url="", record_count=0, file_size=0),
                metadata=Metadata(version="v2", request_id=request.metadata.request_id),
            )

        logger.info(f"조회된 레코드 수: {len(down_form_orders)}")

        # DownFormOrderDto로 변환 및 DataFrame 생성
        dto_items = down_form_order_conversion_service.convert_orm_to_dto_list(down_form_orders)
        df = down_form_order_conversion_service.convert_dto_list_to_dataframe(dto_items)

        # form_names 개수만큼 각각의 Excel 파일 생성
        excel_files = []
        total_record_count = 0
        
        for form_name in form_names:
            # 각 form_name에 대해 별도의 DataFrame 생성
            form_df = df.copy()
            
            # 특정 form_name에 맞춰 column transform
            form_df = await down_form_order_conversion_service.transform_column_by_form_names(form_df, [form_name])
            
            # export_templates에서 description 가져오기
            template_description = await down_form_order_conversion_service.get_template_description(form_name)
            date_now = datetime.now().strftime("%Y%m%d")
            excel_file_name = f"{date_now}_주문서확인처리_{template_description}_매크로완료.xlsx"
            
            # Excel 파일 생성
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
                form_df.to_excel(tmp_file.name, index=False, engine="openpyxl")
                excel_files.append({
                    'temp_path': tmp_file.name,
                    'file_name': excel_file_name
                })
            
            total_record_count += len(form_df)

        try:
            # ZIP 파일 생성
            ord_st_date_str = ord_st_date.strftime("%Y%m%d")
            ord_ed_date_str = ord_ed_date.strftime("%Y%m%d")
            zip_file_name = f"down_form_orders_{ord_st_date_str}_{ord_ed_date_str}.zip"
            zip_temp_path = None
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as zip_tmp_file:
                with zipfile.ZipFile(zip_tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for excel_file in excel_files:
                        zipf.write(excel_file['temp_path'], excel_file['file_name'])
                
                zip_temp_path = zip_tmp_file.name

            # MinIO에 ZIP 파일 업로드
            file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                zip_temp_path, "down_form_orders", zip_file_name
            )
            file_url = url_arrange(file_url)

            logger.info(
                f"[db_to_excel_url] 완료 - URL: {file_url}, 총 레코드 수: {total_record_count}, 파일 수: {len(excel_files)}"
            )

            return ResponseHandler.ok(
                data=DbToExcelResponse(
                    excel_url=file_url,
                    record_count=total_record_count,
                    file_size=file_size,
                ),
                metadata=Metadata(version="v2", request_id=request.metadata.request_id),
            )

        finally:
            # 임시 파일들 삭제
            for excel_file in excel_files:
                if os.path.exists(excel_file['temp_path']):
                    os.remove(excel_file['temp_path'])
            if zip_temp_path and os.path.exists(zip_temp_path):
                os.remove(zip_temp_path)

    except Exception as e:
        logger.error(f"[db_to_excel_url] 오류: {str(e)}", exc_info=True)
        return ResponseHandler.internal_error(
            message=f"Excel 파일 생성 중 오류가 발생했습니다: {str(e)}",
            metadata=Metadata(version="v2", request_id=request.metadata.request_id),
        )


@router.post("/excel-to-db", response_class=JSONResponse)
async def get_excel_to_db(
    request_id: str = Form(..., description="유저 아이디"),
    file: UploadFile = File(..., description="Excel 파일"),
    down_form_order_update_service: DownFormOrderUpdateService = Depends(
        get_down_form_order_update_service
    ),
):
    """
    Excel 파일을 업로드하여 idx(주문번호) 기준으로 upsert 처리
    """
    try:
        logger.info(
            f"[get_excel_to_db] 시작 - 파일: {file.filename}, 요청자: {request_id}"
        )

        # Excel 파일을 DataFrame으로 변환
        dataframe = ExcelHandler.from_upload_file_to_dataframe(file)

        logger.info(f"읽은 레코드 수: {len(dataframe)}")

        if dataframe.empty:
            return ResponseHandler.ok(
                data=ExcelToDbResponse(
                    processed_count=0, inserted_count=0, updated_count=0, failed_count=0
                ),
                metadata=Metadata(version="v2", request_id=request_id),
            )

        # idx 컬럼 확인
        if "idx" not in dataframe.columns:
            return ResponseHandler.bad_request(
                message="Excel 파일에 'idx' 컬럼이 필요합니다.",
                metadata=Metadata(version="v2", request_id=request_id),
            )

        # DataFrame을 DTO 리스트로 변환
        dto_items = []
        failed_count = 0

        for _, row in dataframe.iterrows():
            try:
                # NaN 값을 None으로 변환
                row_dict = row.to_dict()
                for key, value in row_dict.items():
                    if pd.isna(value):
                        row_dict[key] = None
                    # Timezone-naive pandas Timestamp을 timezone-aware datetime으로 변환
                    elif isinstance(value, pd.Timestamp) and value.tz is None:
                        # UTC 타임존으로 localize
                        row_dict[key] = value.tz_localize("UTC")

                dto = DownFormOrderDto.model_validate(row_dict)
                dto_items.append(dto)
            except Exception as e:
                logger.warning(f"레코드 변환 실패: {row.to_dict()}, 오류: {str(e)}")
                failed_count += 1

        logger.info(f"변환 완료 - 성공: {len(dto_items)}, 실패: {failed_count}")

        # Upsert 처리
        inserted_count, updated_count = (
            await down_form_order_update_service.bulk_upsert_from_excel(dto_items)
        )

        logger.info(
            f"[get_excel_to_db] 완료 - 삽입: {inserted_count}, 업데이트: {updated_count}"
        )

        return ResponseHandler.ok(
            data=ExcelToDbResponse(
                processed_count=len(dto_items),
                inserted_count=inserted_count,
                updated_count=updated_count,
                failed_count=failed_count,
            ),
            metadata=Metadata(version="v2", request_id=request_id),
        )

    except Exception as e:
        logger.error(f"[get_excel_to_db] 오류: {str(e)}", exc_info=True)
        return ResponseHandler.internal_error(
            message=f"Excel 파일 처리 중 오류가 발생했습니다: {str(e)}",
            metadata=Metadata(version="v2", request_id=request_id),
        )
