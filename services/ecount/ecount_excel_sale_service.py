"""
Ecount Excel Sale Service
Excel 파일을 통한 이카운트 판매 데이터 처리 서비스
"""

import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from fastapi import HTTPException

from minio_handler import upload_and_get_url_with_count_rev, url_arrange
from models.count_executing_data.count_executing_data import CountExecuting
from repository.count_executing_repository import CountExecutingRepository
from schemas.ecount.auth_schemas import EcountAuthInfo
from schemas.ecount.ecount_schemas import EcountApiResponse, EcountSaleDto, EcountPurchaseDto
from services.ecount.ecount_sale_service import EcountSaleService
from utils.decorators import api_exception_handler
from utils.logs.sabangnet_logger import get_logger
from utils.mappings.ecount_excel_mapping import EcountExcelMapper

logger = get_logger(__name__)


class EcountExcelSaleService:
    """이카운트 Excel 판매 서비스"""

    def __init__(self):
        self.sale_service = EcountSaleService()
        self.mapper = EcountExcelMapper()

    def generate_batch_id(self) -> str:
        """배치 ID를 생성합니다."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"EXCEL_SALE_{timestamp}_{unique_id}"

    @api_exception_handler(
        logger=logger,
        default_status=500,
        default_detail="Excel 파일 업로드 중 오류가 발생했습니다"
    )
    async def upload_file_to_minio(
        self,
        file_content: bytes,
        file_name: str,
        batch_id: str,
        template_code: str,
        session
    ) -> Tuple[str, str, int]:
        """
        파일을 MinIO에 업로드합니다.
        
        Args:
            file_content: 파일 내용
            file_name: 파일명
            batch_id: 배치 ID
            template_code: 템플릿 코드
        Returns:
            Tuple[str, str, int]: (file_url, minio_object_name, file_size)
        """
        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(
                delete=False, suffix='.xlsx'
            ) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            count_repo = CountExecutingRepository(session)
            count_rev = await count_repo.get_and_increment(CountExecuting, "ecount_excel_upload_to_api")
            try:
                # MinIO에 업로드
                file_url, minio_object_name, file_size = upload_and_get_url_with_count_rev(
                    tmp_file_path,
                    template_code,
                    file_name,
                    count_rev
                )
                
                logger.info(
                    f"파일 MinIO 업로드 완료: {file_name}, URL: {file_url}"
                )
                return file_url, minio_object_name, file_size
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"MinIO 업로드 실패: {e}")
            raise HTTPException(
                status_code=500, detail=f"파일 업로드 실패: {str(e)}"
            )
    
    def parse_excel_to_ecount_dtos(
        self,
        file_content: bytes,
        sheet_name: str = "Sheet1",
        auth_info: Optional[EcountAuthInfo] = None,
        template_code: Optional[str] = None,
        work_status: Optional[str] = None
    ) -> List[Union[EcountSaleDto, EcountPurchaseDto]]:
        """
        Excel 파일을 파싱하여 EcountSaleDto 또는 EcountPurchaseDto 리스트로 변환합니다.
        
        Args:
            file_content: Excel 파일 내용 (bytes)
            sheet_name: 시트명
            auth_info: 인증 정보 (com_code, user_id 포함)
            template_code: 템플릿 코드 (sale/purchase 구분용)
            work_status: 작업 상태
            
        Returns:
            List[EcountSaleDto]: 변환된 DTO 리스트 (sale 또는 purchase)
        """
        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(
                delete=False, suffix='.xlsx'
            ) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Excel 파일 읽기
                df = pd.read_excel(
                    tmp_file_path, sheet_name=sheet_name
                )
                
                # 빈 DataFrame 체크
                if df.empty:
                    raise ValueError("Excel 파일이 비어있습니다.")
                
                # 매핑 유효성 검증
                mapping_validation = self.mapper.validate_mapping(df, template_code)
                logger.info(f"Excel 매핑 검증 결과: {mapping_validation}")
                
                # template_code에 따라 DTO 타입 결정
                is_purchase = template_code and "purchase" in template_code.lower()
                dto_class = EcountPurchaseDto if is_purchase else EcountSaleDto
                
                ecount_dtos = []
                
                for index, row in df.iterrows():
                    # 빈 행 체크
                    if row.isna().all():
                        continue
                    
                    # Excel 행을 데이터로 매핑
                    if is_purchase:
                        ecount_data = self.mapper.map_excel_row_to_purchase_data(
                            row, auth_info
                        )
                    else:
                        ecount_data = self.mapper.map_excel_row_to_sale_data(
                            row, auth_info
                        )
                    
                    # DTO 생성 (공통 로직)
                    try:
                        dto = dto_class(**ecount_data)
                        # template_code 설정
                        if template_code:
                            dto.template_code = template_code
                        # work_status 설정
                        if work_status:
                            dto.work_status = work_status
                        ecount_dtos.append(dto)
                    except Exception as e:
                        logger.warning(f"행 {index + 2}에서 DTO 생성 실패: {e}")
                        continue
                
                logger.info(f"Excel 파싱 완료: {len(ecount_dtos)}건 처리 ({'purchase' if is_purchase else 'sale'})")
                return ecount_dtos
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"Excel 파싱 중 오류 발생: {e}")
            raise HTTPException(
                status_code=400, detail=f"Excel 파일 파싱 실패: {str(e)}"
            )
    
    @api_exception_handler(
        logger=logger,
        default_status=500,
        default_detail="데이터 처리 중 오류가 발생했습니다"
    )
    async def process_sale_batch(
        self,
        ecount_dtos: List[Union[EcountSaleDto, EcountPurchaseDto]],
        auth_info: EcountAuthInfo,
        batch_id: str,
        user_id: str,
        work_status: str,
        template_code: str
    ) -> Tuple[Optional[EcountApiResponse], List[str], Dict[str, Any]]:
        """
        판매/구매 배치를 처리합니다.
        
        Args:
            ecount_dtos: 판매/구매 DTO 리스트
            auth_info: 인증 정보
            batch_id: 배치 ID
            user_id: 사용자 ID
            work_status: 작업 상태
            template_code: 템플릿 코드
        Returns:
            Tuple[Optional[EcountApiResponse], List[str], Dict[str, Any]]: 
                (API 응답, 오류 목록, 배치 정보)
        """
        try:
            # 배치 정보 설정
            for dto in ecount_dtos:
                dto.batch_id = batch_id
                dto.is_test = auth_info.is_test if hasattr(auth_info, 'is_test') else True

            api_response, errors = await self.sale_service.create_sales_with_validation_and_template_code(
                ecount_dtos=ecount_dtos,  
                auth_info=auth_info,
                template_code=template_code
            )

            
            # 배치 정보 구성
            batch_info = {
                "batch_id": batch_id,
                "user_id": user_id,
                "total_processed": len(ecount_dtos),
                "success_count": api_response.Data.SuccessCnt if api_response and api_response.Data else 0,
                "fail_count": api_response.Data.FailCnt if api_response and api_response.Data else 0,
                "validation_errors": len(errors),
                "processed_at": datetime.now().isoformat(),
                "work_status": work_status
            }
            
            return api_response, errors, batch_info
            
        except Exception as e:
            logger.error(f"배치 처리 중 오류 발생: {e}")
            raise HTTPException(
                status_code=500, detail=f"배치 처리 실패: {str(e)}"
            )
    
    @api_exception_handler(
        logger=logger,
        default_status=500,
        default_detail="Excel 판매 처리 중 오류가 발생했습니다"
    )
    async def process_excel_sale_upload(
        self,
        file_content: bytes,
        file_name: str,
        sheet_name: str,
        auth_info: EcountAuthInfo,
        user_id: str,
        template_code: str,
        clear_existing: bool,
        work_status: str,
        session
    ) -> Dict[str, Any]:
        """
        Excel 파일 업로드 및 판매 처리를 수행합니다.
        
        Args:
            file_content: 파일 내용
            file_name: 파일명
            sheet_name: 시트명
            auth_info: 인증 정보
            user_id: 사용자 ID
            template_code: 템플릿 코드
            clear_existing: 기존 데이터 삭제 여부
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        # 1. 배치 ID 생성
        batch_id = self.generate_batch_id()
        logger.info(f"배치 처리 시작: {batch_id}")
        
        # 2. 파일을 MinIO에 업로드
        file_url, minio_object_name, file_size = await self.upload_file_to_minio(
            file_content, file_name, batch_id, template_code, session
        )
        
        # 3. template_code에 따라 DTO 타입 결정
        is_purchase = template_code and "purchase" in template_code.lower()
        dto_class = EcountPurchaseDto if is_purchase else EcountSaleDto
        
        # 4. Excel 파일을 DTO 리스트로 변환
        ecount_dtos = self.parse_excel_to_ecount_dtos(
            file_content, sheet_name, auth_info, template_code, work_status
        )
        
        if not ecount_dtos:
            raise HTTPException(
                status_code=400,
                detail="Excel 파일에서 유효한 데이터를 찾을 수 없습니다."
            )
        
        # 5. DTO 타입 검증
        actual_dto_type = type(ecount_dtos[0]).__name__
        expected_dto_type = dto_class.__name__
        if actual_dto_type != expected_dto_type:
            logger.warning(f"DTO 타입 불일치: 예상={expected_dto_type}, 실제={actual_dto_type}")
        
        # 6. 배치 처리
        api_response, errors, batch_info = await self.process_sale_batch(
            ecount_dtos, auth_info, batch_id, user_id, work_status, template_code
        )
        
        # 7. 성공한 데이터만 필터링
        successful_dtos = [
            dto for dto in ecount_dtos 
            if dto.is_success
        ]
        
        # 8. 응답 메시지 구성
        success_count = batch_info["success_count"]
        fail_count = batch_info["fail_count"]
        data_type = "구매" if is_purchase else "판매"
        
        message = (
            f"Excel 업로드 처리 완료 ({data_type}): {success_count}건 성공, "
            f"{fail_count}건 실패"
        )
        if errors:
            message += f", {len(errors)}건 검증 오류"
        
        # 9. 최종 응답 데이터 구성
        response_data = {
            "success": success_count > 0,
            "message": message,
            "batch_info": {
                **batch_info,
                "file_url": url_arrange(file_url),
                "file_name": file_name,
                "minio_object_name": minio_object_name,
                "file_size": file_size
            },
            "successful_sales": [dto.model_dump() for dto in successful_dtos],
            "errors": errors,
            "api_response": (
                api_response.Data.model_dump()
                if api_response and api_response.Data
                else None
            )
        }
        
        logger.info(
            f"배치 처리 완료: {batch_id}, 성공: {success_count}건, "
            f"실패: {fail_count}건"
        )
        return response_data
