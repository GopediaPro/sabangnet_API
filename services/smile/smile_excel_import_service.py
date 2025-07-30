"""
Smile Excel Import Service
스마일배송 Excel 가져오기 서비스
"""

import pandas as pd
import tempfile
import os
import time
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from models.smile.smile_sku_data import SmileSkuData
from models.smile.smile_erp_data import SmileErpData
from models.smile.smile_settlement_data import SmileSettlementData
from models.smile.smile_sku_data import SmileSkuData
from repository.smile_erp_data_repository import SmileErpDataRepository
from repository.smile_settlement_data_repository import SmileSettlementDataRepository
from repository.smile_sku_data_repository import SmileSkuDataRepository
from utils.logs.sabangnet_logger import get_logger
from utils.decorators import api_exception_handler
from utils.builders.smile_data_builder import SmileDataProcessor
from schemas.smile.smile_excel_import_dto import (
    SmileErpDataImportResponseDto,
    SmileSettlementDataImportResponseDto,
    SmileSkuDataImportResponseDto,
    SmileAllDataImportResponseDto,
    SmileAllDataImportResultDto,
    SmileDataProcessingErrorDto
)

logger = get_logger(__name__)


class SmileExcelImportService:
    """스마일배송 Excel 가져오기 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.erp_repo = SmileErpDataRepository(session)
        self.settlement_repo = SmileSettlementDataRepository(session)
        self.sku_repo = SmileSkuDataRepository(session)
        self.data_processor = SmileDataProcessor()
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="ERP 데이터 가져오기 중 오류가 발생했습니다")
    async def import_erp_data(self, file_content: bytes, file_name: str, sheet_name: str = "Sheet1", clear_existing: bool = False) -> SmileErpDataImportResponseDto:
        """ERP 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        
        with self._create_temp_file(file_content) as temp_file_path:
            df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
            
            if clear_existing:
                await self.erp_repo.delete_all_erp_data()
                logger.info("기존 ERP 데이터가 삭제되었습니다.")
            
            # 빌더를 사용하여 데이터 처리
            erp_data_list = self.data_processor.process_erp_data(df)
            processing_stats = self.data_processor.get_processing_stats()
            
            if erp_data_list:
                saved_data = await self.erp_repo.bulk_create_erp_data(erp_data_list)
                processing_time = time.time() - start_time
                
                logger.info(f"ERP 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                
                return SmileErpDataImportResponseDto(
                    success=True,
                    message=f"ERP 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.",
                    imported_count=len(saved_data),
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
            else:
                processing_time = time.time() - start_time
                return SmileErpDataImportResponseDto(
                    success=False,
                    message="처리할 수 있는 데이터가 없습니다.",
                    imported_count=0,
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="정산 데이터 가져오기 중 오류가 발생했습니다")
    async def import_settlement_data(self, file_content: bytes, file_name: str, site: str, sheet_name: str = "Sheet1", clear_existing: bool = False) -> SmileSettlementDataImportResponseDto:
        """정산 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        
        with self._create_temp_file(file_content) as temp_file_path:
            df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
            
            # Unnamed 컬럼들 제거
            unnamed_columns = [col for col in df.columns if 'Unnamed: 11' in str(col)]
            if unnamed_columns:
                logger.info(f"제거할 Unnamed 컬럼들: {unnamed_columns}")
                df = df.drop(columns=unnamed_columns)
            
            # Excel 파일의 컬럼명 로깅
            logger.info(f"Excel 파일 컬럼명: {list(df.columns)}")
            logger.info(f"Excel 파일 행 수: {len(df)}")
            
            # 컬럼명 분석
            logger.info("컬럼명 분석:")
            for i, col in enumerate(df.columns):
                logger.info(f"  컬럼 {i}: '{col}' (타입: {type(col)})")
            
            logger.info(f"Excel 파일 샘플 데이터 (처음 3행):")
            for i in range(min(3, len(df))):
                logger.info(f"  행 {i}: {dict(df.iloc[i])}")
            
            if clear_existing:
                await self.settlement_repo.delete_all_settlement_data()
                logger.info("기존 정산 데이터가 삭제되었습니다.")
            
            # site 파라미터와 함께 데이터 프로세서 초기화
            data_processor = SmileDataProcessor(site=site)
            
            # 빌더를 사용하여 데이터 처리
            settlement_data_list = data_processor.process_settlement_data(df)
            processing_stats = data_processor.get_processing_stats()
            
            if settlement_data_list:
                saved_data = await self.settlement_repo.bulk_create_settlement_data(settlement_data_list, site)
                processing_time = time.time() - start_time
                
                logger.info(f"정산 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                
                return SmileSettlementDataImportResponseDto(
                    success=True,
                    message=f"정산 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.",
                    imported_count=len(saved_data),
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
            else:
                processing_time = time.time() - start_time
                return SmileSettlementDataImportResponseDto(
                    success=False,
                    message="처리할 수 있는 데이터가 없습니다.",
                    imported_count=0,
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="SKU 데이터 가져오기 중 오류가 발생했습니다")
    async def import_sku_data(self, file_content: bytes, file_name: str, sheet_name: str = "Sheet1", clear_existing: bool = False) -> SmileSkuDataImportResponseDto:
        """SKU 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        
        with self._create_temp_file(file_content) as temp_file_path:
            df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
            
            if clear_existing:
                await self.sku_repo.delete_all_sku_data()
                logger.info("기존 SKU 데이터가 삭제되었습니다.")
            
            # 빌더를 사용하여 데이터 처리
            sku_data_list = self.data_processor.process_sku_data(df)
            processing_stats = self.data_processor.get_processing_stats()
            
            if sku_data_list:
                saved_data = await self.sku_repo.bulk_create_sku_data(sku_data_list)
                processing_time = time.time() - start_time
                
                logger.info(f"SKU 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                
                return SmileSkuDataImportResponseDto(
                    success=True,
                    message=f"SKU 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.",
                    imported_count=len(saved_data),
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
            else:
                processing_time = time.time() - start_time
                return SmileSkuDataImportResponseDto(
                    success=False,
                    message="처리할 수 있는 데이터가 없습니다.",
                    imported_count=0,
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="모든 데이터 가져오기 중 오류가 발생했습니다")
    async def import_all_data(self, files: Dict[str, Tuple[bytes, str]], clear_existing: bool = False) -> SmileAllDataImportResponseDto:
        """모든 스마일배송 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        results = {}
        
        # ERP 데이터 처리
        if "erp" in files:
            file_content, file_name = files["erp"]
            erp_response = await self.import_erp_data(file_content, file_name, clear_existing=clear_existing)
            results["erp"] = SmileAllDataImportResultDto(
                success=erp_response.success,
                imported_count=erp_response.imported_count,
                file_name=erp_response.file_name
            )
        
        # 정산 데이터 처리
        if "settlement" in files:
            file_content, file_name = files["settlement"]
            settlement_response = await self.import_settlement_data(file_content, file_name, clear_existing=clear_existing)
            results["settlement"] = SmileAllDataImportResultDto(
                success=settlement_response.success,
                imported_count=settlement_response.imported_count,
                file_name=settlement_response.file_name
            )
        
        # SKU 데이터 처리
        if "sku" in files:
            file_content, file_name = files["sku"]
            sku_response = await self.import_sku_data(file_content, file_name, clear_existing=clear_existing)
            results["sku"] = SmileAllDataImportResultDto(
                success=sku_response.success,
                imported_count=sku_response.imported_count,
                file_name=sku_response.file_name
            )
        
        # 결과 요약
        total_imported = sum(result.imported_count for result in results.values())
        success_count = sum(1 for result in results.values() if result.success)
        
        return SmileAllDataImportResponseDto(
            success=success_count > 0,
            message=f"총 {total_imported}개의 데이터가 가져와졌습니다.",
            total_imported=total_imported,
            success_count=success_count,
            results=results
        )
    
    def _parse_date(self, date_value) -> Optional[datetime]:
        """날짜 값을 파싱합니다."""
        if pd.isna(date_value):
            return None
        if isinstance(date_value, str):
            return pd.to_datetime(date_value).date()
        return date_value.date() if hasattr(date_value, 'date') else date_value
    
    def _parse_numeric(self, value) -> Optional[float]:
        """숫자 값을 파싱합니다."""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except:
            return None
    
    def _handle_row_error(self, index: int, row: pd.Series, error: Exception, stats: Dict[str, Any]):
        """행 처리 오류를 처리합니다."""
        error_info = SmileDataProcessingErrorDto(
            row_number=index + 1,
            column_name="unknown",
            error_type="data_processing",
            error_message=str(error),
            raw_value=str(row.to_dict())
        )
        stats['errors'].append(error_info)
        logger.warning(f"행 처리 중 오류: {error}, 행 데이터: {row.to_dict()}")
        stats['skipped_count'] = stats.get('skipped_count', 0) + 1
    
    def _create_temp_file(self, content: bytes):
        """임시 파일을 생성하는 컨텍스트 매니저입니다."""
        class TempFileContext:
            def __init__(self, content):
                self.content = content
                self.temp_file = None
                self.temp_path = None
            
            def __enter__(self):
                self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
                self.temp_file.write(self.content)
                self.temp_file.flush()
                self.temp_path = self.temp_file.name
                return self.temp_path
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.temp_file:
                    self.temp_file.close()
                if self.temp_path and os.path.exists(self.temp_path):
                    try:
                        os.unlink(self.temp_path)
                    except:
                        pass
        
        return TempFileContext(content)
    
    def _format_processing_stats(self, stats: Dict[str, Any], processing_time: float, total_rows: int) -> str:
        """처리 통계를 포맷팅합니다."""
        return f"처리 시간: {processing_time:.2f}초, 총 행: {total_rows}, 처리된 행: {stats['processed_count']}, 건너뛴 행: {stats['skipped_count']}" 