"""
Ecount Excel Sale Service
Excel 파일을 통한 이카운트 판매 데이터 처리 서비스
"""

import pandas as pd
import tempfile
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from fastapi import HTTPException

from utils.logs.sabangnet_logger import get_logger
from utils.decorators import api_exception_handler
from utils.mappings.ecount_excel_mapping import EcountExcelMapper
from schemas.ecount.ecount_schemas import EcountSaleDto, EcountApiResponse
from schemas.ecount.auth_schemas import EcountAuthInfo
from services.ecount.ecount_sale_service import EcountSaleService
from minio_handler import upload_and_get_url_and_size, url_arrange

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
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="Excel 파일 업로드 중 오류가 발생했습니다")
    async def upload_file_to_minio(self, file_content: bytes, file_name: str, batch_id: str) -> Tuple[str, str, int]:
        """
        파일을 MinIO에 업로드합니다.
        
        Args:
            file_content: 파일 내용
            file_name: 파일명
            batch_id: 배치 ID
            
        Returns:
            Tuple[str, str, int]: (file_url, minio_object_name, file_size)
        """
        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                # MinIO에 업로드
                file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                    tmp_file_path, 
                    "ecount_sale", 
                    file_name
                )
                
                logger.info(f"파일 MinIO 업로드 완료: {file_name}, URL: {file_url}")
                return file_url, minio_object_name, file_size
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"MinIO 업로드 실패: {e}")
            raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
    
    def parse_excel_to_sale_dtos(self, file_content: bytes, sheet_name: str = "Sheet1", auth_info: Optional[EcountAuthInfo] = None) -> List[EcountSaleDto]:
        """
        Excel 파일을 파싱하여 EcountSaleDto 리스트로 변환합니다.
        
        Args:
            file_content: Excel 파일 내용 (bytes)
            sheet_name: 시트명
            auth_info: 인증 정보 (com_code, user_id 포함)
            
        Returns:
            List[EcountSaleDto]: 변환된 판매 DTO 리스트
        """
        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Excel 파일 읽기
                df = pd.read_excel(tmp_file_path, sheet_name=sheet_name)
                
                # 빈 DataFrame 체크
                if df.empty:
                    raise ValueError("Excel 파일이 비어있습니다.")
                
                # 매핑 유효성 검증
                mapping_validation = self.mapper.validate_mapping(df)
                logger.info(f"Excel 매핑 검증 결과: {mapping_validation}")
                
                sale_dtos = []
                
                for index, row in df.iterrows():
                    # 빈 행 체크
                    if row.isna().all():
                        continue
                    
                    # Excel 행을 판매 데이터로 매핑
                    sale_data = self.mapper.map_excel_row_to_sale_data(row, auth_info)
                    
                    # EcountSaleDto 생성
                    try:
                        sale_dto = EcountSaleDto(**sale_data)
                        sale_dtos.append(sale_dto)
                    except Exception as e:
                        logger.warning(f"행 {index + 2}에서 DTO 생성 실패: {e}")
                        continue
                
                logger.info(f"Excel 파싱 완료: {len(sale_dtos)}건 처리")
                return sale_dtos
                
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except Exception as e:
            logger.error(f"Excel 파싱 중 오류 발생: {e}")
            raise HTTPException(status_code=400, detail=f"Excel 파일 파싱 실패: {str(e)}")
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="판매 데이터 처리 중 오류가 발생했습니다")
    async def process_sale_batch(
        self, 
        sale_dtos: List[EcountSaleDto], 
        auth_info: EcountAuthInfo,
        batch_id: str,
        user_id: str
    ) -> Tuple[Optional[EcountApiResponse], List[str], Dict[str, Any]]:
        """
        판매 배치를 처리합니다.
        
        Args:
            sale_dtos: 판매 DTO 리스트
            auth_info: 인증 정보
            batch_id: 배치 ID
            user_id: 사용자 ID
            
        Returns:
            Tuple: (api_response, errors, batch_info)
        """
        try:
            # 배치 정보 설정
            for sale_dto in sale_dtos:
                sale_dto.batch_id = batch_id
                sale_dto.is_test = auth_info.is_test if hasattr(auth_info, 'is_test') else True
            
            # create_sales_with_validation을 사용하여 배치 처리
            api_response, errors = await self.sale_service.create_sales_with_validation(
                sale_dtos=sale_dtos,
                auth_info=auth_info
            )
            
            # 배치 정보 구성
            batch_info = {
                "batch_id": batch_id,
                "user_id": user_id,
                "total_processed": len(sale_dtos),
                "success_count": api_response.Data.SuccessCnt if api_response and api_response.Data else 0,
                "fail_count": api_response.Data.FailCnt if api_response and api_response.Data else 0,
                "validation_errors": len(errors),
                "processed_at": datetime.now().isoformat()
            }
            
            return api_response, errors, batch_info
            
        except Exception as e:
            logger.error(f"판매 배치 처리 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=f"판매 배치 처리 실패: {str(e)}")
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="Excel 판매 처리 중 오류가 발생했습니다")
    async def process_excel_sale_upload(
        self,
        file_content: bytes,
        file_name: str,
        sheet_name: str,
        auth_info: EcountAuthInfo,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Excel 파일 업로드 및 판매 처리를 수행합니다.
        
        Args:
            file_content: 파일 내용
            file_name: 파일명
            sheet_name: 시트명
            auth_info: 인증 정보
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        # 1. 배치 ID 생성
        batch_id = self.generate_batch_id()
        logger.info(f"배치 처리 시작: {batch_id}")
        
        # 2. 파일을 MinIO에 업로드
        file_url, minio_object_name, file_size = await self.upload_file_to_minio(
            file_content, file_name, batch_id
        )
        
        # 3. Excel 파일을 EcountSaleDto 리스트로 변환
        sale_dtos = self.parse_excel_to_sale_dtos(file_content, sheet_name, auth_info)
        
        if not sale_dtos:
            raise HTTPException(status_code=400, detail="Excel 파일에서 유효한 데이터를 찾을 수 없습니다.")
        
        # 4. 판매 배치 처리
        api_response, errors, batch_info = await self.process_sale_batch(
            sale_dtos, auth_info, batch_id, user_id
        )
        
        # 5. 성공한 데이터만 필터링
        successful_sales = [
            sale for sale in sale_dtos 
            if sale.is_success
        ]
        
        # 6. 응답 메시지 구성
        success_count = batch_info["success_count"]
        fail_count = batch_info["fail_count"]
        
        message = f"Excel 업로드 처리 완료: {success_count}건 성공, {fail_count}건 실패"
        if errors:
            message += f", {len(errors)}건 검증 오류"
        
        # 7. 최종 응답 데이터 구성
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
            "successful_sales": [sale.model_dump() for sale in successful_sales],
            "errors": errors,
            "api_response": api_response.Data.model_dump() if api_response and api_response.Data else None
        }
        
        logger.info(f"배치 처리 완료: {batch_id}, 성공: {success_count}건, 실패: {fail_count}건")
        return response_data
