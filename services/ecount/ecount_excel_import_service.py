"""
Ecount Excel Import Service
이카운트 Excel 가져오기 서비스
"""

import pandas as pd
import tempfile
import os
import time
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from models.ecount.erp_partner_code import EcountErpPartnerCode
from models.ecount.iyes_cost import EcountIyesCost
from repository.ecount_erp_partner_code_repository import EcountErpPartnerCodeRepository
from repository.ecount_iyes_cost_repository import EcountIyesCostRepository
from utils.logs.sabangnet_logger import get_logger
from utils.decorators import api_exception_handler
from minio_handler import upload_and_get_url_and_size, url_arrange
from schemas.ecount.ecount_excel_import_dto import (
    EcountErpPartnerCodeImportResponseDto,
    EcountIyesCostImportResponseDto,
    EcountAllDataImportResponseDto,
    EcountAllDataImportResultDto,
    EcountDataProcessingErrorDto,
    EcountExcelDownloadResponseDto
)

logger = get_logger(__name__)


class EcountExcelImportService:
    """이카운트 Excel 가져오기 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.erp_partner_code_repo = EcountErpPartnerCodeRepository(session)
        self.iyes_cost_repo = EcountIyesCostRepository(session)
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="ERP 파트너 코드 데이터 가져오기 중 오류가 발생했습니다")
    async def import_erp_partner_code_data(self, file_content: bytes, file_name: str, sheet_name: str = "Sheet1", clear_existing: bool = False) -> EcountErpPartnerCodeImportResponseDto:
        """ERP 파트너 코드 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        
        with self._create_temp_file(file_content) as temp_file_path:
            df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
            
            if clear_existing:
                await self.erp_partner_code_repo.delete_all_erp_partner_codes()
                logger.info("기존 ERP 파트너 코드 데이터가 삭제되었습니다.")
            
            # 데이터 처리
            processed_data = self._process_erp_partner_code_data(df)
            processing_stats = self._get_processing_stats()
            
            if processed_data:
                saved_data = await self.erp_partner_code_repo.bulk_upsert_erp_partner_codes(processed_data)
                processing_time = time.time() - start_time
                
                logger.info(f"ERP 파트너 코드 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                
                return EcountErpPartnerCodeImportResponseDto(
                    success=True,
                    message=f"ERP 파트너 코드 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.",
                    imported_count=len(saved_data),
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
            else:
                processing_time = time.time() - start_time
                return EcountErpPartnerCodeImportResponseDto(
                    success=False,
                    message="처리할 수 있는 데이터가 없습니다.",
                    imported_count=0,
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="IYES 단가 데이터 가져오기 중 오류가 발생했습니다")
    async def import_iyes_cost_data(self, file_content: bytes, file_name: str, sheet_name: str = "Sheet1", clear_existing: bool = False) -> EcountIyesCostImportResponseDto:
        """IYES 단가 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        
        with self._create_temp_file(file_content) as temp_file_path:
            df = pd.read_excel(temp_file_path, sheet_name=sheet_name)
            
            if clear_existing:
                await self.iyes_cost_repo.delete_all_iyes_costs()
                logger.info("기존 IYES 단가 데이터가 삭제되었습니다.")
            
            # 데이터 처리
            processed_data = self._process_iyes_cost_data(df)
            processing_stats = self._get_processing_stats()
            
            if processed_data:
                saved_data = await self.iyes_cost_repo.bulk_upsert_iyes_costs(processed_data)
                processing_time = time.time() - start_time
                
                logger.info(f"IYES 단가 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                
                return EcountIyesCostImportResponseDto(
                    success=True,
                    message=f"IYES 단가 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.",
                    imported_count=len(saved_data),
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
            else:
                processing_time = time.time() - start_time
                return EcountIyesCostImportResponseDto(
                    success=False,
                    message="처리할 수 있는 데이터가 없습니다.",
                    imported_count=0,
                    file_name=file_name,
                    error_details=self._format_processing_stats(processing_stats, processing_time, len(df))
                )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="모든 데이터 가져오기 중 오류가 발생했습니다")
    async def import_all_data(self, files: Dict[str, Tuple[bytes, str]], clear_existing: bool = False) -> EcountAllDataImportResponseDto:
        """모든 이카운트 데이터 Excel 파일을 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        results = {}
        
        # ERP 파트너 코드 데이터 처리
        if "erp_partner_code" in files:
            file_content, file_name = files["erp_partner_code"]
            erp_response = await self.import_erp_partner_code_data(file_content, file_name, clear_existing=clear_existing)
            results["erp_partner_code"] = EcountAllDataImportResultDto(
                success=erp_response.success,
                imported_count=erp_response.imported_count,
                file_name=erp_response.file_name
            )
        
        # IYES 단가 데이터 처리
        if "iyes_cost" in files:
            file_content, file_name = files["iyes_cost"]
            iyes_response = await self.import_iyes_cost_data(file_content, file_name, clear_existing=clear_existing)
            results["iyes_cost"] = EcountAllDataImportResultDto(
                success=iyes_response.success,
                imported_count=iyes_response.imported_count,
                file_name=iyes_response.file_name
            )
        
        # 결과 요약
        total_imported = sum(result.imported_count for result in results.values())
        success_count = sum(1 for result in results.values() if result.success)
        
        return EcountAllDataImportResponseDto(
            success=success_count > 0,
            message=f"총 {total_imported}개의 데이터가 가져와졌습니다.",
            total_imported=total_imported,
            success_count=success_count,
            results=results
        )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="단일 파일에서 모든 데이터 가져오기 중 오류가 발생했습니다")
    async def import_all_data_from_single_file(self, file_content: bytes, file_name: str, 
                                             erp_partner_code_sheet: str, iyes_cost_sheet: str, 
                                             clear_existing: bool = False) -> EcountAllDataImportResponseDto:
        """하나의 Excel 파일에서 여러 시트를 읽어 모든 이카운트 데이터를 처리하여 데이터베이스에 저장합니다."""
        
        start_time = time.time()
        results = {}
        
        with self._create_temp_file(file_content) as temp_file_path:
            # ERP 파트너 코드 데이터 처리
            try:
                df_erp = pd.read_excel(temp_file_path, sheet_name=erp_partner_code_sheet)
                if clear_existing:
                    await self.erp_partner_code_repo.delete_all_erp_partner_codes()
                    logger.info("기존 ERP 파트너 코드 데이터가 삭제되었습니다.")
                
                processed_data = self._process_erp_partner_code_data(df_erp)
                if processed_data:
                    saved_data = await self.erp_partner_code_repo.bulk_upsert_erp_partner_codes(processed_data)
                    results["erp_partner_code"] = EcountAllDataImportResultDto(
                        success=True,
                        imported_count=len(saved_data),
                        file_name=f"{file_name} ({erp_partner_code_sheet})"
                    )
                    logger.info(f"ERP 파트너 코드 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                else:
                    results["erp_partner_code"] = EcountAllDataImportResultDto(
                        success=False,
                        imported_count=0,
                        file_name=f"{file_name} ({erp_partner_code_sheet})"
                    )
            except Exception as e:
                logger.error(f"ERP 파트너 코드 시트 처리 중 오류: {e}")
                results["erp_partner_code"] = EcountAllDataImportResultDto(
                    success=False,
                    imported_count=0,
                    file_name=f"{file_name} ({erp_partner_code_sheet})"
                )
            
            # IYES 단가 데이터 처리
            try:
                df_iyes = pd.read_excel(temp_file_path, sheet_name=iyes_cost_sheet)
                if clear_existing:
                    await self.iyes_cost_repo.delete_all_iyes_costs()
                    logger.info("기존 IYES 단가 데이터가 삭제되었습니다.")
                
                processed_data = self._process_iyes_cost_data(df_iyes)
                if processed_data:
                    saved_data = await self.iyes_cost_repo.bulk_upsert_iyes_costs(processed_data)
                    results["iyes_cost"] = EcountAllDataImportResultDto(
                        success=True,
                        imported_count=len(saved_data),
                        file_name=f"{file_name} ({iyes_cost_sheet})"
                    )
                    logger.info(f"IYES 단가 데이터 {len(saved_data)}개가 성공적으로 저장되었습니다.")
                else:
                    results["iyes_cost"] = EcountAllDataImportResultDto(
                        success=False,
                        imported_count=0,
                        file_name=f"{file_name} ({iyes_cost_sheet})"
                    )
            except Exception as e:
                logger.error(f"IYES 단가 시트 처리 중 오류: {e}")
                results["iyes_cost"] = EcountAllDataImportResultDto(
                    success=False,
                    imported_count=0,
                    file_name=f"{file_name} ({iyes_cost_sheet})"
                )
        
        # 결과 요약
        total_imported = sum(result.imported_count for result in results.values())
        success_count = sum(1 for result in results.values() if result.success)
        
        return EcountAllDataImportResponseDto(
            success=success_count > 0,
            message=f"총 {total_imported}개의 데이터가 가져와졌습니다.",
            total_imported=total_imported,
            success_count=success_count,
            results=results
        )
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="Excel 다운로드 중 오류가 발생했습니다")
    async def download_erp_partner_code_excel(self) -> EcountExcelDownloadResponseDto:
        """ERP 파트너 코드 데이터를 Excel 파일로 다운로드합니다."""
        
        try:
            # 데이터 조회
            data = await self.erp_partner_code_repo.get_all_erp_partner_codes()
            
            if not data:
                return EcountExcelDownloadResponseDto(
                    success=False,
                    message="다운로드할 데이터가 없습니다.",
                    file_name="",
                    file_size=0,
                    total_records=0
                )
            
            # DataFrame 생성 - 제공된 컬럼 매핑에 따라
            df_data = []
            for item in data:
                df_data.append({
                    '업체명': item.fld_dsp,           # A
                    '거래처코드': item.partner_code,      # B
                    '오케이마트': '',                     # C (빈 값)
                    '아이예스': '',                     # D (빈 값)
                    'Column1': '',                     # E (빈 값)
                    '송장최종안': '',                     # F (빈 값)
                    '품목코드': item.product_nm,        # G
                    '_1': '',                     # H (빈 값)
                    '업체명_2': '',                     # I (빈 값)
                    '창고': item.wh_cd              # J
                })
            
            df = pd.DataFrame(df_data)
            
            # Excel 파일 생성
            file_name = f"ERP_거래처코드.xlsx"
            file_path = f"/tmp/{file_name}"
            
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            # MinIO에 업로드
            download_url, minio_object_name, file_size = upload_and_get_url_and_size(
                file_path, 
                template_code="erp", 
                file_name=file_name
            )
            
            logger.info(f"ERP 파트너 코드 Excel 파일 생성 및 MinIO 업로드 완료: {file_name} ({len(data)}건)")
            
            return EcountExcelDownloadResponseDto(
                success=True,
                message=f"ERP 파트너 코드 데이터 {len(data)}건이 Excel 파일로 생성되었습니다.",
                file_name=file_name,
                file_size=file_size,
                download_url=url_arrange(download_url),
                total_records=len(data)
            )
            
        except Exception as e:
            logger.error(f"ERP 파트너 코드 Excel 다운로드 중 오류: {e}")
            raise
    
    @api_exception_handler(logger=logger, default_status=500, default_detail="Excel 다운로드 중 오류가 발생했습니다")
    async def download_iyes_cost_excel(self) -> EcountExcelDownloadResponseDto:
        """IYES 단가 데이터를 Excel 파일로 다운로드합니다."""
        
        try:
            # 데이터 조회
            data = await self.iyes_cost_repo.get_all_iyes_costs()
            
            if not data:
                return EcountExcelDownloadResponseDto(
                    success=False,
                    message="다운로드할 데이터가 없습니다.",
                    file_name="",
                    file_size=0,
                    total_records=0
                )
            
            # DataFrame 생성
            df_data = []
            for item in data:
                df_data.append({
                    '제품명': item.product_nm,
                    '원가(VAT 포함)': item.cost,
                    '원가(VAT 10%)': item.cost_10_vat,
                    '원가(VAT 20%)': item.cost_20_vat
                })
            
            df = pd.DataFrame(df_data)
            
            # Excel 파일 생성
            file_name = f"아이예스_단가.xlsx"
            file_path = f"/tmp/{file_name}"
            
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            # MinIO에 업로드
            download_url, minio_object_name, file_size = upload_and_get_url_and_size(
                file_path, 
                template_code="erp", 
                file_name=file_name
            )
            
            logger.info(f"IYES 단가 Excel 파일 생성 및 MinIO 업로드 완료: {file_name} ({len(data)}건)")
            
            return EcountExcelDownloadResponseDto(
                success=True,
                message=f"IYES 단가 데이터 {len(data)}건이 Excel 파일로 생성되었습니다.",
                file_name=file_name,
                file_size=file_size,
                download_url=url_arrange(download_url),
                total_records=len(data)
            )
            
        except Exception as e:
            logger.error(f"IYES 단가 Excel 다운로드 중 오류: {e}")
            raise
    
    def _process_erp_partner_code_data(self, df: pd.DataFrame) -> List[dict]:
        """ERP 파트너 코드 데이터를 처리합니다."""
        processed_data = []
        
        for index, row in df.iterrows():
            try:
                # 새로운 컬럼 구조에 맞춰 데이터 추출
                fld_dsp = row.get('업체명') or row.get('fld_dsp')
                partner_code = row.get('거래처코드') or row.get('partner_code')
                product_nm = row.get('품목코드') or row.get('product_nm')
                wh_cd = row.get('창고') or row.get('wh_cd')
                
                # fld_dsp 또는 product_nm이 있는 경우만 처리
                if (pd.notna(fld_dsp) and str(fld_dsp).strip()) or (pd.notna(product_nm) and str(product_nm).strip()):
                    processed_data.append({
                        'fld_dsp': str(fld_dsp).strip() if pd.notna(fld_dsp) else None,
                        'partner_code': str(partner_code).strip() if pd.notna(partner_code) else None,
                        'product_nm': str(product_nm).strip() if pd.notna(product_nm) else None,
                        'wh_cd': self._safe_convert_to_int(wh_cd)
                    })
                    
            except Exception as e:
                logger.warning(f"ERP 파트너 코드 데이터 처리 중 오류 (행 {index + 1}): {e}")
                continue
        
        return processed_data
    
    def _process_iyes_cost_data(self, df: pd.DataFrame) -> List[dict]:
        """IYES 단가 데이터를 처리합니다."""
        processed_data = []
        
        for index, row in df.iterrows():
            try:
                # product_nm이 있는 경우만 처리
                product_nm = row.get('제품명') or row.get('product_nm')
                cost = row.get('원가(VAT 포함)') or row.get('cost')
                cost_10_vat = row.get('원가(VAT 10%)') or row.get('cost_10_vat')
                cost_20_vat = row.get('원가(VAT 20%)') or row.get('cost_20_vat')
                
                if pd.notna(product_nm) and str(product_nm).strip():
                    processed_data.append({
                        'product_nm': str(product_nm).strip(),
                        'cost': self._safe_convert_to_int(cost),
                        'cost_10_vat': self._safe_convert_to_int(cost_10_vat),
                        'cost_20_vat': self._safe_convert_to_int(cost_20_vat)
                    })
                    
            except Exception as e:
                logger.warning(f"IYES 단가 데이터 처리 중 오류 (행 {index + 1}): {e}")
                continue
        
        return processed_data
    
    def _get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계를 반환합니다."""
        return {
            'processed_count': 0,
            'skipped_count': 0,
            'errors': []
        }
    
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
    
    def _safe_convert_to_int(self, value) -> Optional[int]:
        """값을 안전하게 정수로 변환합니다."""
        if pd.isna(value) or value is None:
            return None
        
        try:
            # 문자열로 변환 후 공백 제거
            str_value = str(value).strip()
            if not str_value:
                return None
            
            # 쉼표 제거 (예: "13,500" -> "13500")
            str_value = str_value.replace(',', '')
            
            # 숫자로 변환 시도 (소수점 포함)
            float_value = float(str_value)
            return int(float_value)
        except (ValueError, TypeError):
            return None
    
    def _format_processing_stats(self, stats: Dict[str, Any], processing_time: float, total_rows: int) -> str:
        """처리 통계를 포맷팅합니다."""
        return f"처리 시간: {processing_time:.2f}초, 총 행: {total_rows}, 처리된 행: {stats['processed_count']}, 건너뛴 행: {stats['skipped_count']}"
