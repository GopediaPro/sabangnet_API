"""
한진 Excel 다운로드 서비스
"""
import pandas as pd
import os
import tempfile
from datetime import datetime
from typing import Optional
from fastapi import UploadFile

from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from utils.product_text_processor import process_product_text
from models.down_form_orders.down_form_order import BaseDownFormOrder
from models.count_executing_data.count_executing_data import CountExecuting
from repository.down_form_order_repository import DownFormOrderRepository
from services.macro_batch_processing.batch_info_create_service import BatchInfoCreateService
from services.count_excuting_service import CountExecutingService
from schemas.hanjin.hanjin_printWbls_dto import (
    DownloadExcelFormRequest,
    DownloadExcelFormResponse,
    UploadExcelFormRequest,
    UploadExcelFormResponse,
    UpdatedRecord,
)
from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto
from minio_handler import upload_and_get_url_with_count_rev, url_arrange


logger = get_logger(__name__)


class HanjinDownloadService:
    """한진 Excel 다운로드 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repo = DownFormOrderRepository(session)
        self.batch_info_create_service = BatchInfoCreateService(session)
        self.count_executing_service = CountExecutingService(session)
    
    def _map_data_to_excel_format(self, orders: list[BaseDownFormOrder]) -> pd.DataFrame:
        """
        DB 데이터를 Excel 형식으로 매핑
        
        Args:
            orders: down_form_orders 데이터 목록
            
        Returns:
            pd.DataFrame: Excel 형식으로 매핑된 데이터
        """
        # 매핑 규칙 정의 (form_for_hanjin_invoice_no_print.txt 기반)
        mapping_data = []
        
        for order in orders:

            
            mapped_row = {
                # A: 수취인명
                '수취인명': order.receive_name or '',
                # B: 사이트
                '사이트': order.fld_dsp or '',
                # C: 금액 (pay_cost + delv_cost)
                '금액': '',
                # D: 주문번호
                '주문번호': order.order_id or '',
                # E: 제품명
                '제품명': order.item_name or '',
                # F: 수량
                '수량': '',
                # G: 전화번호1
                '전화번호1': order.receive_cel or '',
                # H: 전화번호2
                '전화번호2': order.receive_tel or '',
                # I: 수취인주소
                '수취인주소': order.receive_addr or '',
                # J: 우편번호
                '우편번호': order.receive_zipcode or '',
                # K: 선/착불
                '선/착불': order.delivery_method_str or '',
                # L: 상품번호
                '상품번호': order.mall_product_id or '',
                # M: 배송메세지
                '배송메세지': order.delv_msg or '',
                # N: 정산예정금액
                '정산예정금액': '',
                # O: 서비스이용료
                '서비스이용료': '',
                # P: 장바구니번호
                '장바구니번호': order.mall_order_id or '',
                # Q: 운송장번호
                '운송장번호': order.invoice_no or '',
                # R: 운임비타입
                '운임비타입': order.location_nm or '',
                # S: 판매자관리코드
                '판매자관리코드': order.order_etc_7 or '',
                # T: 금액[배송미포함] (pay_cost만)
                '금액[배송미포함]': '',
                # U: 배송비
                '배송비': '',
                # V: 사방넷품번코드
                '사방넷품번코드': order.product_id or '',
                # W: 사방넷주문번호
                '사방넷주문번호': order.idx or '',
                # X: 수집상품명
                '수집상품명': order.product_name or '',
                # Y: 수집옵션
                '수집옵션': order.sku_value or '',
                # Z: 옵션별칭
                '옵션별칭': order.sku_alias or '',
            }
            mapping_data.append(mapped_row)
        
        return pd.DataFrame(mapping_data)
    
    def _process_dataframe_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame의 데이터를 처리합니다.
        
        Args:
            df: 원본 DataFrame
            
        Returns:
            pd.DataFrame: 처리된 DataFrame
        """
        # DataFrame 복사
        processed_df = df.copy()
        
        # 1. 운임비타입 처리: "/" 구분자로 분리된 경우 가장 앞의 값 사용
        if '운임비타입' in processed_df.columns:
            processed_df['운임비타입'] = processed_df['운임비타입'].apply(
                lambda x: str(x).split('/')[0].strip() if x and '/' in str(x) else str(x) if x else ''
            )
            logger.info("운임비타입 데이터 처리 완료")
        
        # 2. 제품명 처리: ProductTextProcessor 사용
        if '제품명' in processed_df.columns:
            processed_df['제품명'] = processed_df['제품명'].apply(
                lambda x: process_product_text(str(x)) if x else ''
            )
            logger.info("제품명 데이터 처리 완료")
        
        return processed_df
    
    def _create_excel_file(self, df: pd.DataFrame, form_name: str) -> str:
        """
        DataFrame을 Excel 파일로 생성
        
        Args:
            df: 데이터프레임
            form_name: 양식코드
            
        Returns:
            str: 생성된 Excel 파일 경로
        """
        # 임시 디렉토리 생성
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"사방넷_출력본_{form_name}_{timestamp}.xlsx"
        file_path = os.path.join(temp_dir, filename)
        
        # Excel 파일 생성
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        
        logger.info(f"Excel 파일 생성 완료: {file_path}")
        return file_path
    
    async def download_excel_form(
        self,
        reg_date_from: str,
        reg_date_to: str,
        form_name: str,
        request_id: Optional[str] = None
    ) -> DownloadExcelFormResponse:
        """
        Excel 폼 다운로드 처리
        
        Args:
            reg_date_from: 수집일자 시작 (YYYYMMDD)
            reg_date_to: 수집일자 종료 (YYYYMMDD)
            form_name: 양식코드
            request_id: 요청 ID
            
        Returns:
            DownloadExcelFormResponse: 다운로드 응답
        """
        try:
            # 1. DB에서 데이터 조회
            orders = await self.down_form_order_repo.get_down_form_orders_for_excel_export(
                reg_date_from=reg_date_from,
                reg_date_to=reg_date_to,
                form_name=form_name
            )
            
            if not orders:
                logger.warning(f"조회된 데이터가 없습니다: {reg_date_from} ~ {reg_date_to}, form_name: {form_name}")
                return DownloadExcelFormResponse(
                    batch_id=0,
                    file_url="",
                    file_name="",
                    file_size=0,
                    processed_count=0,
                    message="조회된 데이터가 없습니다."
                )
            
            # 2. DataFrame으로 변환
            df = self._map_data_to_excel_format(orders)
            
            # 3. DataFrame 데이터 처리
            df = self._process_dataframe_data(df)
            
            # 4. Excel 파일 생성
            excel_file_path = self._create_excel_file(df, form_name)
            
            # 5. count_rev 획득
            count_rev = await self.count_executing_service.get_and_increment(CountExecuting, "hanjin_excel_download")
            
            # 6. MinIO 업로드
            file_url, minio_object_name, file_size = upload_and_get_url_with_count_rev(
                file_path=excel_file_path,
                template_code="hanjin_excel",
                file_name=os.path.basename(excel_file_path),
                count_rev=count_rev
            )
            
            # 7. URL 정리
            clean_url = url_arrange(file_url)
            
            # 8. batch_process 생성 및 저장
            # 간단한 request 객체 생성 (BatchProcessDto.build_success에서 필요한 필드들)
            class SimpleRequest:
                def __init__(self, request_id):
                    self.created_by = request_id or "hanjin_download_service"
                    self.filters = None
            
            simple_request = SimpleRequest(request_id)
            
            batch_id = await self.batch_info_create_service.build_and_save_batch(
                BatchProcessDto.build_success_with_status,
                os.path.basename(excel_file_path),  # original_filename
                clean_url,  # file_url
                file_size,  # file_size
                simple_request,  # request object
                "hanjin_for_invoice_no_excel_down"  # work_status
            )
            
            logger.info(f"Excel 다운로드 처리 완료: batch_id={batch_id}, processed_count={len(orders)}")
            
            return DownloadExcelFormResponse(
                batch_id=batch_id,
                file_url=clean_url,
                file_name=os.path.basename(excel_file_path),
                file_size=file_size,
                processed_count=len(orders),
                message="Excel 다운로드가 성공적으로 완료되었습니다."
            )
            
        except Exception as e:
            logger.error(f"Excel 다운로드 처리 실패: {str(e)}")
            raise e

    def _map_excel_to_db_format(self, df: pd.DataFrame) -> list[dict]:
        """
        Excel 데이터를 DB 형식으로 매핑
        
        Args:
            df: Excel에서 읽어온 DataFrame
            
        Returns:
            list[dict]: DB 업데이트용 데이터 리스트
        """
        # 매핑 규칙 정의 (form_for_hanjin_invoice_no_upload_to_sabang.txt 기반)
        mapping_data = []
        
        for _, row in df.iterrows():
            # Excel 컬럼명을 DB 필드명으로 매핑
            mapped_row = {
                'fld_dsp': str(row.get('도서', '')),
                'invoice_no': str(row.get('운송장번호', '')),
                'receive_name': str(row.get('받으시는 분', '')),
                'order_id': str(row.get('메모3', '')),  # 메모3 -> order_id (문자열로 변환)
                'idx': str(row.get('메모4', '')),      # 메모4 -> idx (문자열로 변환)
            }
            
            # 필수 데이터 검증
            if mapped_row['fld_dsp'] and mapped_row['invoice_no'] and mapped_row['order_id']:
                mapping_data.append(mapped_row)
            else:
                logger.warning(f"필수 데이터 누락으로 건너뜀: {mapped_row}")
        
        return mapping_data

    def _create_excel_with_updated_data(
        self, 
        original_df: pd.DataFrame, 
        updated_records: list[dict], 
        form_name: str
    ) -> str:
        """
        원본 Excel에 업데이트 결과를 새 시트로 추가하여 새로운 Excel 파일 생성
        
        Args:
            original_df: 원본 DataFrame
            updated_records: 업데이트된 레코드 정보
            form_name: 양식코드
            
        Returns:
            str: 생성된 Excel 파일 경로
        """
        # 임시 디렉토리 생성
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"사방넷_운송장번호_업데이트결과_{form_name}_{timestamp}.xlsx"
        file_path = os.path.join(temp_dir, filename)
        
        # 업데이트 결과를 DataFrame으로 변환
        updated_df = pd.DataFrame(updated_records)
        
        # Excel 파일 생성 (원본 시트 + 업데이트 결과 시트)
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 원본 데이터 시트
            original_df.to_excel(writer, sheet_name='원본데이터', index=False)
            
            # 업데이트 결과 시트
            if not updated_df.empty:
                updated_df.to_excel(writer, sheet_name='업데이트결과', index=False)
            else:
                # 빈 DataFrame이라도 시트 생성
                pd.DataFrame({'메시지': ['업데이트된 데이터가 없습니다.']}).to_excel(
                    writer, sheet_name='업데이트결과', index=False
                )
        
        logger.info(f"업데이트 결과 Excel 파일 생성 완료: {file_path}")
        return file_path

    async def upload_excel_form(
        self,
        file: UploadFile,
        request_id: Optional[str] = None
    ) -> UploadExcelFormResponse:
        """
        Excel 파일을 업로드하여 invoice_no를 업데이트하고 결과를 반환합니다.
        
        Args:
            file: 업로드된 Excel 파일
            request_id: 요청 ID
            
        Returns:
            UploadExcelFormResponse: 업로드 및 업데이트 결과
        """
        temp_file_path = None
        
        try:
            # 1. 파일 확장자 검증
            if not file.filename.endswith(('.xlsx', '.xls')):
                raise ValueError("Excel 파일(.xlsx, .xls)만 업로드 가능합니다.")
            
            # 2. 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # 3. Excel 파일을 DataFrame으로 읽기
            df = pd.read_excel(temp_file_path, sheet_name=0)  # 첫 번째 시트 읽기
            
            # 4. 필수 컬럼 검증
            required_columns = ['도서', '운송장번호', '메모3']  # fld_dsp, invoice_no, order_id
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"필수 컬럼이 누락되었습니다: {missing_columns}")
            
            # 5. Excel 데이터를 DB 형식으로 매핑
            excel_data = self._map_excel_to_db_format(df)
            
            if not excel_data:
                logger.warning("업데이트할 유효한 데이터가 없습니다.")
                return UploadExcelFormResponse(
                    batch_id=0,
                    file_url="",
                    file_name="",
                    file_size=0,
                    total_processed=0,
                    success_count=0,
                    failed_count=0,
                    updated_data=[],
                    message="업데이트할 유효한 데이터가 없습니다."
                )
            
            # 6. count_rev 획득
            count_rev = await self.count_executing_service.get_and_increment(CountExecuting, "hanjin_excel_upload")
            
            # 7. DB 업데이트 실행
            updated_records = await self.down_form_order_repo.bulk_update_invoice_no_by_excel_data(
                excel_data=excel_data,
                batch_id=None  # batch_id는 나중에 설정
            )
            
            # 8. 업데이트 결과 통계 계산
            success_count = sum(1 for record in updated_records if record.get('success', False))
            failed_count = len(updated_records) - success_count
            
            # 9. 업데이트된 데이터를 UpdatedRecord 객체로 변환
            updated_data = [
                UpdatedRecord(
                    idx=record.get('idx', ''),
                    invoice_no=record.get('invoice_no', ''),
                    fld_dsp=record.get('fld_dsp', ''),
                    order_id=record.get('order_id', ''),
                    form_name=record.get('form_name', ''),
                    success=record.get('success', False),
                    error_message=record.get('error_message')
                )
                for record in updated_records
            ]
            
            # 10. 원본 Excel에 업데이트 결과를 새 시트로 추가하여 새로운 Excel 파일 생성
            result_excel_path = self._create_excel_with_updated_data(
                original_df=df,
                updated_records=updated_records,
                form_name="hanjin_invoice_upload"
            )
            
            # 11. MinIO 업로드
            file_url, minio_object_name, file_size = upload_and_get_url_with_count_rev(
                file_path=result_excel_path,
                template_code="hanjin_excel_upload",
                file_name=os.path.basename(result_excel_path),
                count_rev=count_rev
            )
            
            # 12. URL 정리
            clean_url = url_arrange(file_url)
            
            # 13. batch_process 생성 및 저장
            class SimpleRequest:
                def __init__(self, request_id):
                    self.created_by = request_id or "hanjin_upload_service"
                    self.filters = None
            
            simple_request = SimpleRequest(request_id)
            
            batch_id = await self.batch_info_create_service.build_and_save_batch(
                BatchProcessDto.build_success_with_status,
                os.path.basename(result_excel_path),  # original_filename
                clean_url,  # file_url
                file_size,  # file_size
                simple_request,  # request object
                "hanjin_for_invoice_no_excel_upload"  # work_status
            )
            
            # 14. 임시 파일들 정리
            if os.path.exists(result_excel_path):
                os.unlink(result_excel_path)
            
            logger.info(f"Excel 업로드 및 invoice_no 업데이트 완료: batch_id={batch_id}, success={success_count}, failed={failed_count}")
            
            return UploadExcelFormResponse(
                batch_id=batch_id,
                file_url=clean_url,
                file_name=os.path.basename(result_excel_path),
                file_size=file_size,
                total_processed=len(updated_records),
                success_count=success_count,
                failed_count=failed_count,
                updated_data=updated_data,
                message=f"Excel 업로드 및 invoice_no 업데이트가 완료되었습니다. 성공: {success_count}건, 실패: {failed_count}건"
            )
            
        except Exception as e:
            logger.error(f"Excel 업로드 및 invoice_no 업데이트 실패: {str(e)}")
            raise e
        finally:
            # 임시 파일 정리
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
