# std
from typing import Optional
from datetime import date
import pandas as pd
import tempfile
import os

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

# schema
from schemas.integration_request import IntegrationRequest
from schemas.integration_response import ResponseHandler, Metadata
from schemas.down_form_orders.down_form_order_dto import DownFormOrderDto

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


# Request DTOs
from pydantic import BaseModel, Field


class DbToExcelRequest(BaseModel):
    ord_st_date: date = Field(..., description="시작 날짜")
    ord_ed_date: date = Field(..., description="종료 날짜")


class DbToExcelResponse(BaseModel):
    excel_url: str = Field(..., description="Excel 파일 URL")
    record_count: int = Field(..., description="레코드 수")
    file_size: int = Field(..., description="파일 크기 (bytes)")


class ExcelToDbResponse(BaseModel):
    processed_count: int = Field(..., description="처리된 레코드 수")
    inserted_count: int = Field(..., description="삽입된 레코드 수")
    updated_count: int = Field(..., description="업데이트된 레코드 수")
    failed_count: int = Field(0, description="실패한 레코드 수")


@router.post("/db-to-excel-url", response_class=JSONResponse)
async def db_to_excel_url(
    request: IntegrationRequest[DbToExcelRequest],
    down_form_order_read_service: DownFormOrderReadService = Depends(
        get_down_form_order_read_service
    ),
    data_processing_usecase: DataProcessingUsecase = Depends(
        get_data_processing_usecase
    ),
):
    """
    DB에서 날짜 범위로 down_form_orders 데이터를 조회하여 Excel 파일로 변환 후 URL 반환
    """
    try:
        logger.info(f"[db_to_excel_url] 시작 - 요청 데이터: {request.data}")

        ord_st_date = request.data.ord_st_date
        ord_ed_date = request.data.ord_ed_date

        # 날짜 범위로 데이터 조회
        down_form_orders = (
            await down_form_order_read_service.get_down_form_orders_by_date_range(
                date_from=ord_st_date, date_to=ord_ed_date
            )
        )

        if not down_form_orders:
            return ResponseHandler.ok(
                data=DbToExcelResponse(excel_url="", record_count=0, file_size=0),
                metadata=Metadata(version="v2", request_id=request.metadata.request_id),
            )

        logger.info(f"조회된 레코드 수: {len(down_form_orders)}")

        # DownFormOrderDto로 변환 (NaN 값 처리)
        dto_items = []
        for item in down_form_orders:
            # ORM 객체를 dict로 변환
            item_dict = item.__dict__.copy()
            # _sa_instance_state 제거 (SQLAlchemy 내부 속성)
            item_dict.pop("_sa_instance_state", None)

            # NaN 값을 None으로 변환
            for key, value in item_dict.items():
                if pd.isna(value):
                    item_dict[key] = None

            dto_items.append(DownFormOrderDto.model_validate(item_dict))

        # DataFrame 생성
        data_dict = [dto.model_dump() for dto in dto_items]
        df = pd.DataFrame(data_dict)

        # ✅ (추가) sale_cnt를 문자열로 강제: "3.0" -> "3", 공백/NaN -> None (엑셀에 빈칸)
        if "sale_cnt" in df.columns:

            def _sale_cnt_to_str(v):
                if v is None or (isinstance(v, float) and pd.isna(v)):
                    return None
                s = str(v).strip()
                if s == "":
                    return None
                try:
                    return str(int(float(s)))  # "3.0" / Decimal("3") 등도 "3"
                except Exception:
                    return s  # 숫자화 불가 시 원 문자열 유지

            df["sale_cnt"] = df["sale_cnt"].map(_sale_cnt_to_str)

        # ✅ (개선) tz-aware datetime 컬럼의 timezone 정보 제거
        # pandas의 dtype 체크 유틸로 확실하게 처리
        for col in df.columns:
            if pd.api.types.is_datetime64tz_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        # Excel 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
            df.to_excel(tmp_file.name, index=False, engine="openpyxl")
            temp_file_path = tmp_file.name

        try:
            # MinIO에 업로드
            file_name = f"down_form_orders_{ord_st_date}_{ord_ed_date}.xlsx"
            file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                temp_file_path, "down_form_orders", file_name
            )
            file_url = url_arrange(file_url)

            logger.info(
                f"[db_to_excel_url] 완료 - URL: {file_url}, 레코드 수: {len(down_form_orders)}"
            )

            return ResponseHandler.ok(
                data=DbToExcelResponse(
                    excel_url=file_url,
                    record_count=len(down_form_orders),
                    file_size=file_size,
                ),
                metadata=Metadata(version="v2", request_id=request.metadata.request_id),
            )

        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

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
