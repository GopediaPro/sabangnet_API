from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Body
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from services.smile.smile_macro_service import SmileMacroService
from schemas.integration_request import IntegrationRequest
from schemas.integration_response import ResponseHandler, Metadata
from schemas.smile.request.smile_macro_v2_request import SmileMacroV2Request
from schemas.smile.response.smile_macro_v2_response import SmileMacroV2Response
from core.db import get_async_session
from utils.decorators import smile_excel_import_handler
from minio_handler import temp_file_to_object_name, delete_temp_file
import json

logger = get_logger(__name__)
router = APIRouter(
    prefix="/smile-macro",
    tags=["smile-macro"]
)

def get_smile_macro_service(session: AsyncSession = Depends(get_async_session)) -> SmileMacroService:
    return SmileMacroService(session=session)

@router.post("/smile-excel-macro-multiple-v2")
@smile_excel_import_handler()
async def smile_excel_macro_multiple_v2(
    request: str = Form(..., description="요청 데이터 (JSON 문자열)"),
    files: List[UploadFile] = File(..., description="처리할 엑셀 파일들"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    여러 엑셀 파일을 합친 후 스마일배송 매크로 처리하고 MinIO에 업로드 (v2)
    
    처리 과정:
    1. batch_process 생성 (request_id 기반, order_date_from/to를 date_from/to로 저장)
    2. 여러 엑셀 파일을 합쳐서 매크로 처리
    3. smile_macro 테이블에 처리된 데이터 저장 (batch_id 포함)
    4. down_form_orders 테이블에 batch_id 업데이트
    5. A, G 파일 및 전체 파일 생성하여 MinIO에 업로드
    6. batch_process에 파일 정보 업데이트
    
    Args:
        request: JSON 문자열 형태의 IntegrationRequest<SmileMacroV2Request>
            예시: {"data":{"order_date_from":"2025-08-23","order_date_to":"2025-08-23"},"metadata":{"request_id":"lyckabc"}}
            - data.order_date_from: 주문 시작 일자
            - data.order_date_to: 주문 종료 일자
            - metadata.request_id: 요청 ID (batch_process 생성용)
        files: 업로드된 엑셀 파일들
        session: 데이터베이스 세션
        
    Returns:
        SmileMacroV2Response: 처리 결과 (batch_id, 파일 URL 포함)
    """
    try:
        # JSON 문자열을 파싱하여 IntegrationRequest 객체 생성
        request_obj = IntegrationRequest[SmileMacroV2Request](**json.loads(request))
        
        # 요청 데이터 추출
        order_date_from = request_obj.data.order_date_from
        order_date_to = request_obj.data.order_date_to
        request_id = request_obj.metadata.request_id if request_obj.metadata else None
        
        # 파일들 저장
        temp_file_paths = []
        for file in files:
            temp_file_path = temp_file_to_object_name(file)
            temp_file_paths.append(temp_file_path)
        
        try:
            # 서비스 인스턴스 생성 (세션 포함)
            smile_macro_service = SmileMacroService(session)
            
            # v2 메서드로 스마일 매크로 처리
            result = await smile_macro_service.process_smile_macro_with_db_v2(
                file_paths=temp_file_paths,
                order_date_from=order_date_from,
                order_date_to=order_date_to,
                request_id=request_id
            )
            
            # 메타데이터 생성
            metadata = Metadata(
                version="2.0",
                request_id=request_obj.metadata.request_id if request_obj.metadata else None
            )
            
            logger.info("스마일 매크로 처리 (v2) 완료")
            
            # ResponseHandler를 사용하여 응답 생성
            return ResponseHandler.created(result, metadata)
            
        finally:
            # 임시 파일들 정리
            for temp_file_path in temp_file_paths:
                delete_temp_file(temp_file_path)
                
    except Exception as e:
        logger.error(f"smile_excel_macro_multiple_v2 실패: {str(e)}")
        
        # 에러 메타데이터 생성 (request_obj가 정의되지 않았을 수 있으므로 안전하게 처리)
        request_id = None
        try:
            if 'request_obj' in locals():
                request_id = request_obj.metadata.request_id if request_obj.metadata else None
        except:
            pass
            
        metadata = Metadata(
            version="2.0",
            request_id=request_id
        )
        
        # ResponseHandler를 사용하여 에러 응답 생성
        return ResponseHandler.internal_error(
            message="스마일 매크로 처리 중 오류가 발생했습니다.",
            metadata=metadata
        )
