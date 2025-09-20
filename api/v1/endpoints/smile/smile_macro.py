from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from services.smile.smile_macro_service import SmileMacroService
from schemas.smile.smile_macro_dto import (
    SmileMacroRequestDto,
    SmileMacroResponseDto,
    SmileMacroStageRequestDto
)
from schemas.macro_batch_processing.request.batch_process_request import BatchProcessRequest
from core.db import get_async_session
from utils.decorators import smile_excel_import_handler
from minio_handler import temp_file_to_object_name, delete_temp_file
import json

logger = get_logger(__name__)
router = APIRouter(
    prefix="/smile-macro",
    tags=["smile-macro"]
)

@router.post("/smile-excel-macro-multiple")
@smile_excel_import_handler()
async def smile_excel_macro_multiple_minio(
    request: str = Form(
        ...,
        description=json.dumps(
            BatchProcessRequest.Config.json_schema_extra['example'], indent=2)
    ),
    files: List[UploadFile] = File(..., description="처리할 엑셀 파일들"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    여러 엑셀 파일을 합친 후 스마일배송 매크로 처리하고 MinIO에 업로드
    
    Args:
        request: 배치 처리 요청 정보
        files: 업로드된 엑셀 파일들
        session: 데이터베이스 세션
        
    Returns:
        Dict: 처리 결과 (MinIO URL 포함, 두 개의 파일 경로 포함)
    """
    # request 객체 파싱
    request_obj = BatchProcessRequest(**json.loads(request))
    
    # 파일들 저장
    temp_file_paths = []
    for file in files:
        temp_file_path = temp_file_to_object_name(file)
        temp_file_paths.append(temp_file_path)
    
    try:
        # 서비스 인스턴스 생성 (세션 포함)
        smile_macro_service = SmileMacroService(session)
        
        # 여러 파일을 합쳐서 매크로 처리하고 MinIO에 업로드
        result = await smile_macro_service.merge_and_process_files_with_minio(
            file_paths=temp_file_paths,
            request_obj=request_obj
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    finally:
        # 임시 파일들 정리
        for temp_file_path in temp_file_paths:
            delete_temp_file(temp_file_path)
