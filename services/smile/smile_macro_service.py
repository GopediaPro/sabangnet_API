import pandas as pd
import os
import random
import string
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from utils.macros.smile.smile_macro_handler import SmileMacroHandler
from utils.macros.smile.smile_common_utils import SmileCommonUtils
from utils.builders.smile_data_builder import SmileMacroDataBuilder
from utils.handlers.data_type_handler import SmileDataTypeHandler
from repository.smile_erp_data_repository import SmileErpDataRepository
from repository.smile_settlement_data_repository import SmileSettlementDataRepository
from repository.smile_sku_data_repository import SmileSkuDataRepository
from repository.smile_macro_repository import SmileMacroRepository
from repository.down_form_order_repository import DownFormOrderRepository
from schemas.smile.smile_macro_dto import (
    SmileMacroRequestDto, 
    SmileMacroResponseDto, 
    SmileMacroStageRequestDto
)
from schemas.smile.request.smile_macro_v2_request import SmileMacroV2Request
from schemas.smile.response.smile_macro_v2_response import SmileMacroV2Response
from schemas.macro_batch_processing.request.batch_process_request import BatchProcessRequest
from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto
from schemas.receive_orders.request.receive_orders_request import BaseDateRangeRequest
from services.macro_batch_processing.batch_info_create_service import BatchInfoCreateService
from minio_handler import upload_and_get_url_and_size, url_arrange
from models.smile.smile_macro import SmileMacro
logger = get_logger(__name__)


class SmileMacroService:
    """
    스마일배송 매크로 서비스
    VBA 매크로를 Python으로 변환한 처리 로직을 제공
    """
    
    def __init__(self, session: AsyncSession = None):
        self.logger = logger
        self.session = session
        if session:
            self.erp_repository = SmileErpDataRepository(session)
            self.settlement_repository = SmileSettlementDataRepository(session)
            self.sku_repository = SmileSkuDataRepository(session)
            self.smile_macro_repository = SmileMacroRepository(session)
            self.down_form_order_repository = DownFormOrderRepository(session)
            self.batch_info_create_service = BatchInfoCreateService(session)
    
    def _generate_random_alphabat(self) -> str:
        """랜덤 알파벳 생성"""
        return ''.join(random.choices(string.ascii_uppercase, k=1))
    
    def _get_site_name_from_column_a(self, first_char: str) -> str:
        """A 컬럼의 첫 글자를 기준으로 사이트명 반환"""
        if first_char.upper() == 'A':
            return "옥션"
        elif first_char.upper() == 'G':
            return "G마켓"
        elif first_char.lower() == 'bundle':
            return "합포장"
        elif first_char.lower() == 'full':
            return "전체"
        else:
            return "기타"
    
    def _generate_filename(self, first_char: str) -> str:
        """파일명 생성"""
        site_name = self._get_site_name_from_column_a(first_char)
        return f"스마일_{site_name}.xlsx"
    
    def _split_data_by_column_a(self, macro_handler: SmileMacroHandler) -> Tuple[SmileMacroHandler, SmileMacroHandler]:
        """A 컬럼을 기준으로 데이터를 A, G로 분리"""
        # A 컬럼 데이터 수집
        a_data = []
        g_data = []
        
        # 데이터 행 처리 (2행부터)
        for row in range(2, macro_handler.ws.max_row + 1):
            row_data = []
            for col in range(1, macro_handler.ws.max_column + 1):
                row_data.append(macro_handler.ws.cell(row=row, column=col).value)
            
            # A 컬럼의 첫 글자 확인 (A 컬럼은 1번째 컬럼)
            if row_data and row_data[0]:
                first_char = str(row_data[0])[0].upper()
                if first_char == 'A':
                    a_data.append(row_data)
                elif first_char == 'G':
                    g_data.append(row_data)
        
        # 임시 파일 생성하여 새로운 핸들러 생성
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        temp_file.close()
        
        # 원본 워크북을 임시 파일로 저장
        macro_handler.wb.save(temp_file.name)
        
        # A 데이터용 핸들러 생성
        a_handler = SmileMacroHandler.from_file(temp_file.name)
        a_handler.ws.delete_rows(2, a_handler.ws.max_row)  # 헤더 제외한 모든 행 삭제
        
        # G 데이터용 핸들러 생성
        g_handler = SmileMacroHandler.from_file(temp_file.name)
        g_handler.ws.delete_rows(2, g_handler.ws.max_row)  # 헤더 제외한 모든 행 삭제
        
        # A 데이터 추가
        for row_idx, row_data in enumerate(a_data, start=2):
            for col_idx, cell_value in enumerate(row_data, start=1):
                a_handler.ws.cell(row=row_idx, column=col_idx, value=cell_value)
        
        # G 데이터 추가
        for row_idx, row_data in enumerate(g_data, start=2):
            for col_idx, cell_value in enumerate(row_data, start=1):
                g_handler.ws.cell(row=row_idx, column=col_idx, value=cell_value)
        
        # 임시 파일 삭제
        try:
            os.remove(temp_file.name)
        except:
            pass
        
        return a_handler, g_handler
    
    async def save_macro_handler_to_db(self, macro_handler: SmileMacroHandler) -> List[dict]:
        """
        매크로 핸들러의 데이터를 DB에 저장
        
        Args:
            macro_handler: 매크로 핸들러
            
        Returns:
            List[dict]: 저장된 데이터 리스트
        """
        try:
            if not self.session:
                self.logger.warning("데이터베이스 세션이 없습니다. DB 저장을 건너뜁니다.")
                return False
            
            # 컬럼 매핑 정보를 빌더에서 가져오기
            column_mapping = SmileMacroDataBuilder.get_column_mapping()
            integer_fields = SmileMacroDataBuilder.get_integer_fields()
            date_fields = SmileMacroDataBuilder.get_date_fields()
            
            # 데이터 수집
            smile_macro_data_list = []
            
            # 헤더 제외하고 2행부터 처리
            for row_num in range(2, macro_handler.ws.max_row + 1):
                row_data = {}
                
                # 각 컬럼을 순회하며 데이터 수집
                for col_letter in column_mapping.keys():
                    if column_mapping[col_letter] is None:
                        continue  # source_field가 없는 컬럼은 건너뛰기
                    
                    cell_value = macro_handler.ws[f'{col_letter}{row_num}'].value
                    field_name = column_mapping[col_letter]
                    
                    # 데이터 타입 변환 (핸들러 사용)
                    field_type = SmileDataTypeHandler.get_field_type(
                        field_name, integer_fields, date_fields
                    )
                    row_data[field_name] = SmileDataTypeHandler.convert_field_value(
                        cell_value, field_name, field_type
                    )
                
                smile_macro_data_list.append(row_data)
            
            # DB에 저장
            if smile_macro_data_list:
                await self.smile_macro_repository.create_multiple_smile_macro(smile_macro_data_list)
                self.logger.info(f"매크로 핸들러 데이터 {len(smile_macro_data_list)}개 DB 저장 완료")
                return smile_macro_data_list
            else:
                self.logger.warning("저장할 데이터가 없습니다.")
                return []
                
        except Exception as e:
            self.logger.error(f"매크로 핸들러 DB 저장 중 오류: {str(e)}")
            return []

    async def save_macro_handler_to_db_v2(self, macro_handler: SmileMacroHandler, batch_id: int) -> List[dict]:
        """
        매크로 핸들러의 데이터를 DB에 저장 (v2) - batch_id 포함
        
        Args:
            macro_handler: 매크로 핸들러
            batch_id: 배치 ID
            
        Returns:
            List[dict]: 저장된 데이터 리스트
        """
        try:
            if not self.session:
                self.logger.warning("데이터베이스 세션이 없습니다. DB 저장을 건너뜁니다.")
                return []
            
            # 컬럼 매핑 정보를 빌더에서 가져오기
            column_mapping = SmileMacroDataBuilder.get_column_mapping()
            integer_fields = SmileMacroDataBuilder.get_integer_fields()
            date_fields = SmileMacroDataBuilder.get_date_fields()
            
            # 데이터 수집
            smile_macro_data_list = []
            
            # 헤더 제외하고 2행부터 처리
            for row_num in range(2, macro_handler.ws.max_row + 1):
                row_data = {}
                
                # 각 컬럼을 순회하며 데이터 수집
                for col_letter in column_mapping.keys():
                    if column_mapping[col_letter] is None:
                        continue  # source_field가 없는 컬럼은 건너뛰기
                    
                    cell_value = macro_handler.ws[f'{col_letter}{row_num}'].value
                    field_name = column_mapping[col_letter]
                    
                    # 데이터 타입 변환 (핸들러 사용)
                    field_type = SmileDataTypeHandler.get_field_type(
                        field_name, integer_fields, date_fields
                    )
                    row_data[field_name] = SmileDataTypeHandler.convert_field_value(
                        cell_value, field_name, field_type
                    )
                
                # batch_id 추가
                row_data['batch_id'] = batch_id
                
                # reg_date에 현재 한국 시간 추가 (YYYYMMDDHHMMSS 형식)
                from datetime import timezone
                korea_tz = timezone(timedelta(hours=9))  # 한국 시간대 (UTC+9)
                current_time = datetime.now(korea_tz)
                row_data['reg_date'] = current_time.strftime('%Y%m%d%H%M%S')
                
                smile_macro_data_list.append(row_data)
            
            # DB에 저장
            if smile_macro_data_list:
                await self.smile_macro_repository.create_multiple_smile_macro(smile_macro_data_list)
                self.logger.info(f"매크로 핸들러 데이터 {len(smile_macro_data_list)}개 DB 저장 완료 (batch_id: {batch_id})")
                return smile_macro_data_list
            else:
                self.logger.warning("저장할 데이터가 없습니다.")
                return []
                
        except Exception as e:
            self.logger.error(f"매크로 핸들러 DB 저장 (v2) 중 오류: {str(e)}")
            return []
    
    async def save_macro_handler_to_down_form_order(self, smile_macro_data_list: List[dict], batch_id: Optional[str] = None, template_code: Optional[str] = None):
        """
        smile_macro 데이터를 down_form_order DB에 저장
        
        Args:
            smile_macro_data_list: smile_macro 데이터 리스트
            batch_id: 배치 ID
            template_code: 템플릿 코드 ('smile_erp' 또는 'smile_bundle')
        """
        try:
            if not smile_macro_data_list:
                self.logger.warning("down_form_order에 저장할 데이터가 없습니다.")
                return
            
            from schemas.smile.smile_macro_dto import SmileMacroDto
            
            down_form_order_data_list = []
            
            for macro_data in smile_macro_data_list:
                # SmileMacroDto 생성
                smile_macro_dto = SmileMacroDto(**macro_data)
                
                # 통합된 변환 메서드 사용
                down_form_data = smile_macro_dto.to_down_form_order_data(form_type=template_code)
                # etc_cost 에 pay_cost 값 넣기 (정수로 변환 후 문자열로 저장)
                if 'pay_cost' in down_form_data:
                    pay_cost_value = down_form_data['pay_cost']
                    if pay_cost_value is not None:
                        try:
                            # Decimal이나 float인 경우 정수로 변환 후 문자열로 저장
                            if isinstance(pay_cost_value, (Decimal, float)):
                                down_form_data['etc_cost'] = str(int(pay_cost_value))
                            else:
                                # 문자열인 경우 먼저 float로 변환 후 정수로 변환
                                if isinstance(pay_cost_value, str):
                                    down_form_data['etc_cost'] = str(int(float(pay_cost_value)))
                                else:
                                    down_form_data['etc_cost'] = str(int(pay_cost_value))
                        except (ValueError, TypeError):
                            # 변환 실패 시 None으로 설정
                            self.logger.warning(f"pay_cost 값을 정수로 변환할 수 없습니다: {pay_cost_value}")
                            down_form_data['etc_cost'] = None
                    else:
                        down_form_data['etc_cost'] = None
                down_form_order_data_list.append(down_form_data)
            
            # down_form_order DB에 저장
            if down_form_order_data_list:
                if self.down_form_order_repository:
                    # save_to_down_form_orders 메서드 활용 (기존 생성 코드 활용)
                    saved_count = await self.down_form_order_repository.save_to_down_form_orders(
                        down_form_order_data_list, 
                        template_code=template_code,
                        batch_id=batch_id
                    )
                    self.logger.info(f"down_form_order에 {saved_count}개 데이터 저장 완료 (template_code: {template_code})")
                else:
                    self.logger.warning("down_form_order_repository가 없습니다. 저장을 건너뜁니다.")
                    
        except Exception as e:
            self.logger.error(f"down_form_order 저장 중 오류: {str(e)}")
            if self.session:
                await self.session.rollback()
            raise e
    
    async def process_smile_macro_with_db(self, file_path: str, output_path: Optional[str] = None, request_obj: Optional[BatchProcessRequest] = None) -> SmileMacroResponseDto:
        """
        데이터베이스에서 데이터를 가져와서 스마일배송 매크로 처리
        
        Args:
            file_path: 처리할 엑셀 파일 경로
            output_path: 출력 파일 경로 (None이면 자동 생성)
            fld_dsp: 사이트명 (G마켓, 옥션 등), None이면 전체 사이트
            
        Returns:
            SmileMacroResponseDto - 처리 결과
        """
        try:
            # 파일 존재 확인
            if not os.path.exists(file_path):
                return SmileMacroResponseDto(
                    success=False,
                    message=f"파일을 찾을 수 없습니다: {file_path}",
                    error_details="File not found"
                )
            
            # 데이터베이스에서 데이터 조회
            erp_df = await self.get_erp_data_from_db()
            settlement_df = await self.get_settlement_data_from_db()
            sku_df = await self.get_sku_data_from_db()
            
            # 매크로 핸들러 초기화 (데이터베이스 리포지토리 전달)
            macro_handler = SmileMacroHandler.from_file(
                file_path, 
                erp_repository=self.erp_repository,
                settlement_repository=self.settlement_repository
            )
            
            # 매크로 핸들러 데이터 행 수 확인
            initial_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"매크로 핸들러 초기화 완료, 초기 데이터 행 수: {initial_rows}")
            
            # 1-5단계 처리 (async)
            stage_1_5_success = await macro_handler.process_stage_1_to_5(erp_df, settlement_df)
            if not stage_1_5_success:
                return SmileMacroResponseDto(
                    success=False,
                    message="1-5단계 처리 중 오류가 발생했습니다.",
                    error_details="Stage 1-5 processing failed"
                )
            
            # 1-5단계 처리 후 데이터 행 수 확인
            after_stage_5_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"1-5단계 처리 후 데이터 행 수: {after_stage_5_rows}")
            
            # 6-8단계 처리
            stage_6_8_success = macro_handler.process_stage_6_to_8(sku_df)
            if not stage_6_8_success:
                return SmileMacroResponseDto(
                    success=False,
                    message="6-8단계 처리 중 오류가 발생했습니다.",
                    error_details="Stage 6-8 processing failed"
                )
            
            # 전체 칼럼 및 값 중간 점검 (서비스 레이어에서도 확인)
            inspection_result = macro_handler.print_all_columns_and_values()
            self.logger.info(f"서비스 레이어에서 확인한 중간 점검 결과: {inspection_result}")
            
            # 6-8단계 처리 후 데이터 행 수 확인
            after_stage_8_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"6-8단계 처리 후 데이터 행 수: {after_stage_8_rows}")
            
            # A 컬럼을 기준으로 데이터 분리, Header 변경
            a_handler, g_handler = self._split_data_by_column_a(macro_handler)

            # A 데이터 값 변경
            SmileCommonUtils.transform_column_a_data(macro_handler.ws)
            # macro_handler data를 smile_macro DB에 저장하고 데이터 반환
            smile_macro_data_list = await self.save_macro_handler_to_db(macro_handler)
            
            # batch_id 생성 (request_obj가 있는 경우)
            batch_id = None
            if request_obj:
                # 원본 파일명 생성 (첫 번째 파일명 사용)
                original_filename = os.path.basename(file_path)
                # 임시로 빈 file_url과 file_size로 batch 생성 (나중에 실제 값으로 업데이트)
                batch_id = await self.batch_info_create_service.build_and_save_batch(
                    BatchProcessDto.build_success,
                    original_filename,
                    "",  # 임시 file_url
                    0,   # 임시 file_size
                    request_obj
                )
                self.logger.info(f"배치 ID 생성 완료: {batch_id}")
            
            # smile_macro DB의 data를 down_form_order DB에 저장 (batch_id 포함)
            await self.save_macro_handler_to_down_form_order(smile_macro_data_list, batch_id, 'smile_erp')

            # 전체 파일 저장
        
            # A 데이터 파일 저장
            a_saved_path = self._save_data_file(a_handler, 'A', file_path)
            
            # G 데이터 파일 저장
            g_saved_path = self._save_data_file(g_handler, 'G', file_path)
            
            # 처리된 행 수 계산
            a_processed_rows, g_processed_rows, _, total_processed_rows = self._calculate_processed_rows(a_handler, g_handler, [])
            
            self.logger.info(f"데이터베이스 기반 스마일배송 매크로 처리 완료: A파일={a_saved_path}({a_processed_rows}행), G파일={g_saved_path}({g_processed_rows}행)")
            
            return SmileMacroResponseDto(
                success=True,
                message="데이터베이스 기반 스마일배송 매크로 처리가 성공적으로 완료되었습니다.",
                output_path=a_saved_path,
                output_path2=g_saved_path,
                processed_rows=total_processed_rows,
                batch_id=batch_id,
                macro_handler=macro_handler
            )
            
        except Exception as e:
            self.logger.error(f"데이터베이스 기반 스마일배송 매크로 처리 중 오류: {str(e)}")
            return SmileMacroResponseDto(
                success=False,
                message=f"매크로 처리 중 오류가 발생했습니다: {str(e)}",
                error_details=str(e)
            )
    
    def merge_and_process_files(self, file_paths: List[str], output_path: Optional[str] = None) -> SmileMacroResponseDto:
        """
        여러 파일을 합친 후 스마일배송 매크로 처리
        
        Args:
            file_paths: 처리할 엑셀 파일 경로 리스트
            output_path: 출력 파일 경로 (None이면 자동 생성)
            fld_dsp: 사이트명 (G마켓, 옥션 등), None이면 전체 사이트
            
        Returns:
            SmileMacroResponseDto - 처리 결과
        """
        try:
            if not file_paths:
                return SmileMacroResponseDto(
                    success=False,
                    message="처리할 파일이 없습니다.",
                    error_details="No files provided"
                )
            
            # 파일 존재 확인
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return SmileMacroResponseDto(
                        success=False,
                        message=f"파일을 찾을 수 없습니다: {file_path}",
                        error_details=f"File not found: {file_path}"
                    )
            
            # 파일 합치기
            from utils.excels.excel_handler import ExcelHandler
            merged_file_path = ExcelHandler.merge_excel_files_smart(file_paths)
            
            # 합쳐진 파일로 매크로 처리
            result = self.process_smile_macro_with_db(merged_file_path, output_path)
            
            # 임시 합쳐진 파일 삭제
            try:
                os.remove(merged_file_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            self.logger.error(f"파일 합치기 및 매크로 처리 중 오류: {str(e)}")
            return SmileMacroResponseDto(
                success=False,
                message=f"파일 합치기 및 매크로 처리 중 오류가 발생했습니다: {str(e)}",
                error_details=str(e)
            )
    
    async def process_smile_macro_with_db_v2(
        self,
        file_paths: List[str],
        order_date_from: date,
        order_date_to: date,
        request_id: Optional[str] = None
    ) -> SmileMacroV2Response:
        """
        스마일 매크로 처리 (v2) - batch_id를 down_form_orders와 smile_macro에 추가
        
        Args:
            file_paths: 처리할 엑셀 파일 경로 리스트
            order_date_from: 주문 시작 일자
            order_date_to: 주문 종료 일자
            request_id: 요청 ID (batch_process 생성용)
            
        Returns:
            SmileMacroV2Response: 처리 결과
        """
        try:
            if not file_paths:
                raise ValueError("처리할 파일이 없습니다.")
            
            # 파일 존재 확인
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
            # 파일 합치기
            from utils.excels.excel_handler import ExcelHandler
            merged_file_path = ExcelHandler.merge_excel_files_smart(file_paths)
            
            # 배치 프로세스 생성 (order_date_from/to를 date_from/to로 저장)
            batch_id = None
            if request_id:
                from schemas.macro_batch_processing.batch_process_dto import BatchProcessDto
                from schemas.macro_batch_processing.request.batch_process_request import BatchProcessRequest
                
                # BatchProcessRequest 생성 (order_date_from/to를 date_from/to로 매핑)
                batch_request_erp = BatchProcessRequest(
                    created_by=request_id,
                    filters=BaseDateRangeRequest(
                        date_from=order_date_from,
                        date_to=order_date_to
                    )
                )

                batch_request_bundle = BatchProcessRequest(
                    created_by=request_id,
                    filters=BaseDateRangeRequest(
                        date_from=order_date_from,
                        date_to=order_date_to
                    )
                )
                
                # 배치 생성 (파일명은 나중에 업데이트)
                batch_id = await self.batch_info_create_service.build_and_save_batch(
                    BatchProcessDto.build_success,
                    "",  # 임시 original_filename
                    "",  # 임시 file_url
                    0,   # 임시 file_size
                    batch_request_erp
                )
                # 배치 생성
                batch_id_bundle = await self.batch_info_create_service.build_and_save_batch(
                    BatchProcessDto.build_success,
                    "",  # 임시 original_filename
                    "",  # 임시 file_url
                    0,   # 임시 file_size
                    batch_request_bundle
                )
                self.logger.info(f"배치 ID 생성 완료: {batch_id}, {batch_id_bundle}")
            
            # 기존 process_smile_macro_with_db의 프로세스들을 직접 활용
            # 파일 존재 확인
            if not os.path.exists(merged_file_path):
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {merged_file_path}")
            
            # 데이터베이스에서 데이터 조회
            erp_df = await self.get_erp_data_from_db()
            settlement_df = await self.get_settlement_data_from_db()
            sku_df = await self.get_sku_data_from_db()
            
            # 매크로 핸들러 초기화 (데이터베이스 리포지토리 전달)
            macro_handler = SmileMacroHandler.from_file(
                merged_file_path, 
                erp_repository=self.erp_repository,
                settlement_repository=self.settlement_repository
            )
            
            # 매크로 핸들러 데이터 행 수 확인
            initial_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"매크로 핸들러 초기화 완료, 초기 데이터 행 수: {initial_rows}")
            
            # 1-5단계 처리 (async)
            stage_1_5_success = await macro_handler.process_stage_1_to_5(erp_df, settlement_df)
            if not stage_1_5_success:
                raise Exception("1-5단계 처리 중 오류가 발생했습니다.")
            
            # 1-5단계 처리 후 데이터 행 수 확인
            after_stage_5_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"1-5단계 처리 후 데이터 행 수: {after_stage_5_rows}")
            
            # 6-8단계 처리
            stage_6_8_success = macro_handler.process_stage_6_to_8(sku_df)
            if not stage_6_8_success:
                raise Exception("6-8단계 처리 중 오류가 발생했습니다.")
            
            # 전체 칼럼 및 값 중간 점검 (서비스 레이어에서도 확인)
            inspection_result = macro_handler.print_all_columns_and_values()
            # self.logger.info(f"서비스 레이어에서 확인한 중간 점검 결과: {inspection_result}")
            
            # 6-8단계 처리 후 데이터 행 수 확인
            after_stage_8_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"6-8단계 처리 후 데이터 행 수: {after_stage_8_rows}")
            
            # A 컬럼을 기준으로 데이터 분리, Header 변경
            a_handler, g_handler = self._split_data_by_column_a(macro_handler)

            # A 데이터 값 변경
            SmileCommonUtils.transform_column_a_data(macro_handler.ws)
            
            # macro_handler를 smile_macro DB에 smile_erp 저장 (batch_id 포함)
            smile_macro_data_list = await self.save_macro_handler_to_db_v2(macro_handler, batch_id)

            # smile_macro_data_list를 smile_bundle 용 데이터로 변환
            smile_macro_data_list_bundle = self.convert_to_smile_bundle_data(smile_macro_data_list)
            # smile_macro_data_list를 down_form_order DB에 저장 (batch_id 포함)
            await self.save_macro_handler_to_down_form_order(smile_macro_data_list, batch_id, 'smile_erp')

            # smile_macro_data_list_bundle 를 down_form_order DB에 저장 (batch_id 포함)
            await self.save_macro_handler_to_down_form_order(smile_macro_data_list_bundle, batch_id_bundle, 'smile_bundle')

            # A 데이터 파일 저장
            a_saved_path = self._save_data_file(a_handler, 'A', merged_file_path)
            # G 데이터 파일 저장
            g_saved_path = self._save_data_file(g_handler, 'G', merged_file_path)
            # full 데이터 파일 저장
            full_saved_path = self._save_data_file(macro_handler, 'full', merged_file_path)
            # bundle 데이터 파일 저장
            bundle_saved_path = self._save_bundle_data_to_excel(smile_macro_data_list_bundle, 'bundle', merged_file_path)
            
            # 처리된 행 수 계산
            a_processed_rows, g_processed_rows, bundle_processed_rows, total_processed_rows = self._calculate_processed_rows(a_handler, g_handler, smile_macro_data_list_bundle)
            
            self.logger.info(f"데이터베이스 기반 스마일배송 매크로 처리 완료: A파일={a_saved_path}({a_processed_rows}행), G파일={g_saved_path}({g_processed_rows}행)")
            self.logger.info(f"데이터베이스 기반 스마일배송 매크로 처리 완료: 전체={full_saved_path}({total_processed_rows}행)")
            self.logger.info(f"데이터베이스 기반 스마일배송 매크로 처리 완료: bundle파일={bundle_saved_path}({bundle_processed_rows}행)")
            
            # down_form_orders 테이블에 batch_id 업데이트
            if batch_id:
                await self._update_down_form_orders_batch_id(order_date_from, order_date_to, batch_id)
            
            # 처리된 파일들을 MinIO에 업로드
            upload_result = await self._upload_files_to_minio(
                a_saved_path, g_saved_path, bundle_saved_path, full_saved_path
            )
            
            # 결과에서 URL 추출
            a_file_url = upload_result.get('a_file_url')
            g_file_url = upload_result.get('g_file_url')
            bundle_file_url = upload_result.get('bundle_file_url')
            full_file_url = upload_result.get('full_file_url')
            full_minio_object_name = upload_result.get('full_minio_object_name')
            bundle_minio_object_name = upload_result.get('bundle_minio_object_name')
            full_file_size = upload_result.get('full_file_size')
            bundle_file_size = upload_result.get('bundle_file_size')
            
            # batch_process에 파일 정보 업데이트
            if batch_id and full_file_url:
                await self._update_batch_process_files(batch_id, full_file_url, full_minio_object_name, full_file_size)
            if batch_id_bundle and bundle_file_url:
                await self._update_batch_process_files(batch_id_bundle, bundle_file_url, bundle_minio_object_name, bundle_file_size)
            
            # 임시 파일들 정리
            try:
                os.remove(merged_file_path)
                os.remove(a_saved_path)
                os.remove(g_saved_path)
                os.remove(bundle_saved_path)
            except:
                pass
            
            return SmileMacroV2Response(
                batch_id=batch_id or 0,
                processed_count=total_processed_rows,
                a_file_url=a_file_url,
                g_file_url=g_file_url,
                full_file_url=full_file_url,
                bundle_url=bundle_file_url, 
                message="스마일 매크로 처리 완료"
            )
            
        except Exception as e:
            self.logger.error(f"스마일 매크로 처리 (v2) 중 오류: {str(e)}")
            raise e

    async def merge_and_process_files_with_minio(self, file_paths: List[str], request_obj: BatchProcessRequest) -> Dict[str, Any]:
        """
        여러 파일을 합친 후 스마일배송 매크로 처리하고 MinIO에 업로드
        
        Args:
            file_paths: 처리할 엑셀 파일 경로 리스트
            fld_dsp: 사이트명 (G마켓, 옥션 등), None이면 전체 사이트
            template_code: 템플릿 코드 (MinIO 경로용)
            
        Returns:
            Dict[str, Any] - 처리 결과 (MinIO URL 포함)
        """
        try:
            if not file_paths:
                return {
                    "success": False,
                    "message": "처리할 파일이 없습니다.",
                    "error_details": "No files provided"
                }
            
            # 파일 존재 확인
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    return {
                        "success": False,
                        "message": f"파일을 찾을 수 없습니다: {file_path}",
                        "error_details": f"File not found: {file_path}"
                    }
            
            # 파일 합치기
            from utils.excels.excel_handler import ExcelHandler
            merged_file_path = ExcelHandler.merge_excel_files_smart(file_paths)
            
            # 합쳐진 파일로 매크로 처리 (동기적으로 처리)
            result = await self.process_smile_macro_with_db(merged_file_path, None, request_obj)
            
            if not result.success:
                # 임시 합쳐진 파일 삭제
                try:
                    os.remove(merged_file_path)
                except:
                    pass
                return {
                    "success": False,
                    "message": result.message,
                    "error_details": result.error_details
                }
            
            # 처리된 파일들을 MinIO에 업로드
            try:
                # 파일 업로드
                files_info = [
                    (result.output_path, 'a'),
                    (result.output_path2, 'g')
                ]
                upload_result = self._upload_multiple_files_to_minio(files_info)
                
                # 결과에서 URL과 정보 추출
                a_file_url = upload_result.get('a_file_url')
                g_file_url = upload_result.get('g_file_url')
                a_minio_object_name = upload_result.get('a_minio_object_name')
                g_minio_object_name = upload_result.get('g_minio_object_name')
                a_file_size = upload_result.get('a_file_size')
                g_file_size = upload_result.get('g_file_size')
                
                # batch 업데이트 (batch_id가 있는 경우)
                if result.batch_id:
                    try:
                        # A 파일 정보로 batch 업데이트
                        from repository.batch_info_repository import BatchInfoRepository
                        batch_repository = BatchInfoRepository(self.session)
                        
                        # A 파일 정보로 batch 업데이트
                        batch_dto = BatchProcessDto(
                            batch_id=result.batch_id,
                            file_url=a_file_url,
                            file_size=a_file_size,
                            file_name=a_file_name
                        )
                        await batch_repository.update_batch_info(batch_dto)
                        self.logger.info(f"배치 정보 업데이트 완료: batch_id={result.batch_id}")
                        
                        # macro_handler 데이터를 기반으로 전체 파일을 저장하여 batch_process에 입력
                        if result.macro_handler:
                            await self._save_macro_handler_to_batch_process(
                                result.macro_handler, 
                                result.batch_id, 
                                a_file_url, 
                                a_file_size
                            )
                    except Exception as e:
                        self.logger.error(f"배치 정보 업데이트 실패: {str(e)}")
                
                # 임시 파일들 정리
                try:
                    os.remove(merged_file_path)
                    os.remove(result.output_path)
                    os.remove(result.output_path2)
                except:
                    pass
                
                return {
                    "success": True,
                    "message": "파일 합치기 및 매크로 처리가 성공적으로 완료되었습니다.",
                    "file_url": a_file_url,
                    "file_url2": g_file_url,
                    "minio_object_name": a_minio_object_name,
                    "minio_object_name2": g_minio_object_name,
                    "file_size": a_file_size,
                    "file_size2": g_file_size,
                    "processed_rows": result.processed_rows,
                    "output_path": result.output_path,
                    "output_path2": result.output_path2,
                    "batch_id": result.batch_id
                }
                
            except Exception as e:
                self.logger.error(f"MinIO 업로드 중 오류: {str(e)}")
                # 임시 파일들 정리
                try:
                    os.remove(merged_file_path)
                    os.remove(result.output_path)
                except:
                    pass
                return {
                    "success": False,
                    "message": f"MinIO 업로드 중 오류가 발생했습니다: {str(e)}",
                    "error_details": str(e)
                }
            
        except Exception as e:
            self.logger.error(f"파일 합치기 및 매크로 처리 중 오류: {str(e)}")
            return {
                "success": False,
                "message": f"파일 합치기 및 매크로 처리 중 오류가 발생했습니다: {str(e)}",
                "error_details": str(e)
            }

    
    def validate_erp_data(self, erp_data: List[Dict[str, Any]]) -> bool:
        """
        ERP 데이터 유효성 검증
        
        Args:
            erp_data: ERP 데이터 리스트
            
        Returns:
            bool: 유효성 검증 결과
        """
        required_fields = ['날짜', '사이트', '고객성함', '주문번호', 'ERP']
        return SmileCommonUtils.validate_required_fields(erp_data, required_fields)
    
    def validate_settlement_data(self, settlement_data: List[Dict[str, Any]]) -> bool:
        """
        정산 데이터 유효성 검증
        
        Args:
            settlement_data: 정산 데이터 리스트
            
        Returns:
            bool: 유효성 검증 결과
        """
        required_fields = [
            '주문번호', '상품번호', '장바구니번호', '상품명', '구매자명',
            '입금확인일', '배송완료일', '조기정산일자', '구분', '판매금액',
            '서비스이용료', '정산금액', '송금대상액', '결제일', '발송일',
            '환불일', '사이트'
        ]
        return SmileCommonUtils.validate_required_fields(settlement_data, required_fields)
    
    def _convert_to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        딕셔너리 리스트를 DataFrame으로 변환
        
        Args:
            data: 딕셔너리 리스트
            
        Returns:
            pd.DataFrame: 변환된 DataFrame
        """
        return SmileCommonUtils.convert_to_dataframe(data)
    
    async def get_erp_data_from_db(self, site: Optional[str] = None) -> pd.DataFrame:
        """
        데이터베이스에서 ERP 데이터 조회
        
        Args:
            fld_dsp: 사이트명 (G마켓, 옥션 등), None이면 전체 조회
            
        Returns:
            pd.DataFrame: ERP 데이터 DataFrame
        """
        try:
            if not self.session:
                self.logger.warning("데이터베이스 세션이 없습니다. 빈 DataFrame을 반환합니다.")
                return pd.DataFrame()
            
            if site:
                erp_data_list = await self.erp_repository.get_erp_data_by_fld_dsp(site)
            else:
                erp_data_list = await self.erp_repository.get_all_erp_data()
            
            # ORM 객체를 딕셔너리로 변환
            erp_data_dicts = []
            for erp_data in erp_data_list:
                erp_data_dicts.append({
                    '날짜': erp_data.date.strftime('%Y-%m-%d') if erp_data.date else None,
                    '사이트': erp_data.site,
                    '고객성함': erp_data.customer_name,
                    '주문번호': erp_data.order_number,
                    'ERP': erp_data.erp_code
                })
            
            df = pd.DataFrame(erp_data_dicts)
            self.logger.info(f"데이터베이스에서 ERP 데이터 {len(df)} 건 조회 완료")
            return df
            
        except Exception as e:
            self.logger.error(f"데이터베이스에서 ERP 데이터 조회 중 오류: {str(e)}")
            return pd.DataFrame()
    
    async def get_settlement_data_from_db(self, fld_dsp: Optional[str] = None) -> pd.DataFrame:
        """
        데이터베이스에서 정산 데이터 조회
        
        Args:
            fld_dsp: 사이트명 (G마켓, 옥션 등), None이면 전체 조회
            
        Returns:
            pd.DataFrame: 정산 데이터 DataFrame
        """
        try:
            if not self.session:
                self.logger.warning("데이터베이스 세션이 없습니다. 빈 DataFrame을 반환합니다.")
                return pd.DataFrame()
            
            if fld_dsp:
                settlement_data_list = await self.settlement_repository.get_settlement_data_by_site(fld_dsp)
            else:
                settlement_data_list = await self.settlement_repository.get_all_settlement_data()
            
            # ORM 객체를 딕셔너리로 변환
            settlement_data_dicts = []
            for settlement_data in settlement_data_list:
                settlement_data_dicts.append({
                    '주문번호': settlement_data.order_number,
                    '상품번호': settlement_data.product_number,
                    '장바구니번호': settlement_data.cart_number,
                    '상품명': settlement_data.product_name,
                    '구매자명': settlement_data.buyer_name,
                    '입금확인일': settlement_data.payment_confirmation_date.strftime('%Y-%m-%d') if settlement_data.payment_confirmation_date else None,
                    '배송완료일': settlement_data.delivery_completion_date.strftime('%Y-%m-%d') if settlement_data.delivery_completion_date else None,
                    '조기정산일자': settlement_data.early_settlement_date.strftime('%Y-%m-%d') if settlement_data.early_settlement_date else None,
                    '구분': settlement_data.settlement_type,
                    '판매금액': str(settlement_data.sales_amount) if settlement_data.sales_amount else None,
                    '서비스이용료': str(settlement_data.service_fee) if settlement_data.service_fee else None,
                    '정산금액': str(settlement_data.settlement_amount) if settlement_data.settlement_amount else None,
                    '송금대상액': str(settlement_data.transfer_amount) if settlement_data.transfer_amount else None,
                    '결제일': settlement_data.payment_date.strftime('%Y-%m-%d') if settlement_data.payment_date else None,
                    '발송일': settlement_data.shipping_date.strftime('%Y-%m-%d') if settlement_data.shipping_date else None,
                    '환불일': settlement_data.refund_date.strftime('%Y-%m-%d') if settlement_data.refund_date else None,
                    '사이트': settlement_data.site
                })
            
            df = pd.DataFrame(settlement_data_dicts)
            self.logger.info(f"데이터베이스에서 정산 데이터 {len(df)} 건 조회 완료")
            return df
            
        except Exception as e:
            self.logger.error(f"데이터베이스에서 정산 데이터 조회 중 오류: {str(e)}")
            return pd.DataFrame()
    
    async def get_sku_data_from_db(self) -> pd.DataFrame:
        """
        데이터베이스에서 SKU 데이터 조회
        
        Returns:
            pd.DataFrame: SKU 데이터 DataFrame
        """
        try:
            if not self.session:
                self.logger.warning("데이터베이스 세션이 없습니다. 빈 DataFrame을 반환합니다.")
                return pd.DataFrame()
            
            sku_data_list = await self.sku_repository.get_all_sku_data()
            
            # ORM 객체를 DataFrame으로 변환
            sku_data_dicts = []
            for sku_data in sku_data_list:
                sku_data_dicts.append({
                    'sku_number': sku_data.sku_number,
                    'model_name': sku_data.model_name
                })
            
            df = pd.DataFrame(sku_data_dicts)
            self.logger.info(f"데이터베이스에서 SKU 데이터 {len(df)} 건 조회 완료")
            return df
            
        except Exception as e:
            self.logger.error(f"데이터베이스에서 SKU 데이터 조회 중 오류: {str(e)}")
            return pd.DataFrame()
    
    def get_column_mapping(self) -> Dict[str, str]:
        """
        스마일배송 컬럼 매핑 정보 반환
        
        Returns:
            Dict[str, str]: 컬럼 매핑 정보
        """
        return {
            'A': '아이디*',
            'B': '정산예정금??',
            'C': '서비스 이용료',
            'D': '장바구니번호(결제번호)',
            'E': '배송비 금액',
            'F': '구매결정일자',
            'G': '상품번호*',
            'H': '주문번호*',
            'I': '주문옵션',
            'J': '상품명',
            'K': '수량',
            'L': '추가구성',
            'M': '사은품',
            'N': '판매금액',
            'O': '구매자ID',
            'P': '구매자명',
            'Q': '수령인명',
            'R': '배송비',
            'S': '수령인 휴대폰',
            'T': '수령인 전화번호',
            'U': '주소',
            'V': '우편번호',
            'W': '배송시 요구사항',
            'X': '(옥션)복수구매할인',
            'Y': '(옥션)우수회원할인',
            'Z': 'SKU번호 및 수량',
            'AA': '결제완료일',
            'AB': '구매자 전화번호',
            'AC': '구매자 휴대폰',
            'AD': '구매쿠폰적용금액',
            'AE': '발송예정일',
            'AF': '발송일자',
            'AG': '배송구분',
            'AH': '배송번호',
            'AI': '배송상태',
            'AJ': '배송완료일자',
            'AK': '배송지연사유',
            'AL': '배송점포',
            'AM': '상품미수령상세사유',
            'AN': '상품미수령신고사유',
            'AO': '상품미수령신고일자',
            'AP': '상품미수령이의제기일자',
            'AQ': '상품미수령철회요청일자',
            'AR': '송장번호(방문수령인증키)',
            'AS': '일시불할인',
            'AT': '재배송일',
            'AU': '재배송지 우편번호',
            'AV': '재배송지 운송장번호',
            'AW': '재배송지 주소',
            'AX': '재배송택배사명',
            'AY': '정산완료일',
            'AZ': '주문일자(결제확인전)',
            'BA': '주문종류',
            'BB': '주문확인일자',
            'BC': '택배사명(발송방법)',
            'BD': '판매단가',
            'BE': '판매방식',
            'BF': '판매자 관리코드',
            'BG': '판매자 상세관리코드',
            'BH': '판매자북캐시적립',
            'BI': '판매자쿠폰할인',
            'BJ': '판매자포인트적립'
        } 

    async def _save_macro_handler_to_batch_process(
        self, 
        macro_handler: SmileMacroHandler, 
        batch_id: int, 
        file_url: str, 
        file_size: int
    ):
        """
        macro_handler 데이터를 기반으로 전체 파일을 저장하여 batch_process에 입력
        
        Args:
            macro_handler: 매크로 핸들러
            batch_id: 배치 ID
            file_url: 파일 URL
            file_size: 파일 크기
        """
        try:
            # macro_handler의 전체 데이터를 DataFrame으로 변환
            import pandas as pd
            from utils.excels.excel_handler import ExcelHandler
            
            # macro_handler의 워크시트를 DataFrame으로 변환
            data = []
            for row in range(2, macro_handler.ws.max_row + 1):  # 헤더 제외
                row_data = []
                for col in range(1, macro_handler.ws.max_column + 1):
                    row_data.append(macro_handler.ws.cell(row=row, column=col).value)
                data.append(row_data)
            
            # 컬럼명 가져오기
            headers = []
            for col in range(1, macro_handler.ws.max_column + 1):
                headers.append(macro_handler.ws.cell(row=1, column=col).value)
            
            # DataFrame 생성
            df = pd.DataFrame(data, columns=headers)
            
            # 임시 파일로 저장
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            temp_file.close()
            
            # Excel 파일로 저장
            df.to_excel(temp_file.name, index=False)
            
            # MinIO에 업로드
            upload_result = self._upload_single_file_to_minio(
                temp_file.name, "smile_macro_full", "full"
            )
            full_file_url = upload_result.get('full_file_url')
            full_file_size = upload_result.get('full_file_size')
            file_name = f"smile_macro_full_batch_{batch_id}.xlsx"
            
            # batch_process에 전체 파일 정보 추가
            from repository.batch_info_repository import BatchInfoRepository
            batch_repository = BatchInfoRepository(self.session)
            
            # 전체 파일 정보로 batch 업데이트
            batch_dto = BatchProcessDto(
                batch_id=batch_id,
                file_url=full_file_url,
                file_size=full_file_size,
                file_name=file_name
            )
            await batch_repository.update_batch_info(batch_dto)
            
            # 임시 파일 삭제
            try:
                os.remove(temp_file.name)
            except:
                pass
            
            self.logger.info(f"전체 파일 batch_process 저장 완료: batch_id={batch_id}, file_url={full_file_url}")
            
        except Exception as e:
            self.logger.error(f"전체 파일 batch_process 저장 실패: {str(e)}")
            raise e 

    async def _update_smile_macro_batch_id(self, old_batch_id: int, new_batch_id: int):
        """smile_macro 테이블의 batch_id 업데이트"""
        try:
            if self.smile_macro_repository:
                await self.smile_macro_repository.update_batch_id(old_batch_id, new_batch_id)
                self.logger.info(f"smile_macro batch_id 업데이트 완료: {old_batch_id} -> {new_batch_id}")
            else:
                self.logger.warning("smile_macro_repository가 없습니다. batch_id 업데이트를 건너뜁니다.")
        except Exception as e:
            self.logger.error(f"smile_macro batch_id 업데이트 실패: {str(e)}")
            raise e

    async def _update_down_form_orders_batch_id(self, order_date_from: date, order_date_to: date, batch_id: int):
        """down_form_orders 테이블의 batch_id 업데이트"""
        try:
            if self.down_form_order_repository:
                await self.down_form_order_repository.update_batch_id_by_date_range(
                    order_date_from, order_date_to, batch_id
                )
                self.logger.info(f"down_form_orders batch_id 업데이트 완료: {batch_id}")
            else:
                self.logger.warning("down_form_order_repository가 없습니다. batch_id 업데이트를 건너뜁니다.")
        except Exception as e:
            self.logger.error(f"down_form_orders batch_id 업데이트 실패: {str(e)}")
            raise e

    async def _upload_files_to_minio(
        self, 
        a_output_path: str, 
        g_output_path: str, 
        bundle_output_path: str,
        full_saved_path: str, 
    ) -> dict:
        """파일들을 MinIO에 업로드"""
        try:
            # 파일 정보 리스트 생성
            files_info = [
                (a_output_path, 'a'),
                (g_output_path, 'g'),
                (bundle_output_path, 'bundle'),
                (full_saved_path, 'full')
            ]
            
            # 다중 파일 업로드
            result = self._upload_multiple_files_to_minio(files_info)
            
            return result
            
        except Exception as e:
            self.logger.error(f"MinIO 업로드 실패: {str(e)}")
            raise e

    async def _update_batch_process_files(self, batch_id: int, file_url: str, minio_object_name: str, file_size: int):
        """batch_process에 파일 정보 업데이트"""
        try:
            from repository.batch_info_repository import BatchInfoRepository
            batch_repository = BatchInfoRepository(self.session)
            
            # A 파일 정보로 batch 업데이트
            batch_dto = BatchProcessDto(
                batch_id=batch_id,
                file_url=file_url,
                file_size=file_size,
                file_name=os.path.basename(minio_object_name),
                original_filename=os.path.basename(minio_object_name)
            )
            await batch_repository.update_batch_info(batch_dto)
            self.logger.info(f"배치 정보 업데이트 완료: batch_id={batch_id}")
            
        except Exception as e:
            self.logger.error(f"배치 정보 업데이트 실패: {str(e)}")
            raise e

    def convert_to_smile_bundle_data(self, smile_macro_data_list: List[dict]) -> List[dict]:
        """
        smile_macro_data_list를 smile_bundle 형식으로 변환
        VBA 코드의 Sub Macro4() 로직을 Python으로 구현
        
        Args:
            smile_macro_data_list: 원본 smile_macro 데이터 리스트
            
        Returns:
            List[dict]: bundle 형식으로 변환된 데이터 리스트
        """
        try:
            if not smile_macro_data_list:
                self.logger.warning("변환할 데이터가 없습니다.")
                return []
            
            # 그룹화 키를 기준으로 데이터 그룹화
            grouped_data = self._group_data_by_key(smile_macro_data_list)
            
            # 그룹화된 데이터를 bundle 형식으로 변환
            bundle_data_list = []
            for group_key, group_items in grouped_data.items():
                bundle_item = self._create_bundle_item(group_key, group_items)
                if bundle_item:
                    bundle_data_list.append(bundle_item)
            
            self.logger.info(f"smile_bundle 데이터 변환 완료: {len(bundle_data_list)}개 그룹")
            return bundle_data_list
            
        except Exception as e:
            self.logger.error(f"smile_bundle 데이터 변환 중 오류: {str(e)}")
            return []
    
    def _group_data_by_key(self, data_list: List[dict]) -> Dict[str, List[dict]]:
        """
        사이트, 수취인명, 주소를 기준으로 데이터 그룹화
        VBA 코드의 strT = T(i, 2) & T(i, 3) & T(i, 10) 로직
        
        Args:
            data_list: 원본 데이터 리스트
            
        Returns:
            Dict[str, List[dict]]: 그룹화된 데이터
        """
        grouped = {}
        
        for item in data_list:
            # 그룹화 키 생성 (사이트 + 수취인명 + 주소)
            site = str(item.get('fld_dsp', ''))
            receiver = str(item.get('receive_name', ''))
            address = str(item.get('receive_addr', ''))
            group_key = f"{site}_{receiver}_{address}"
            
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(item)
        
        return grouped
    
    def _create_bundle_item(self, group_key: str, group_items: List[dict]) -> Optional[dict]:
        """
        그룹화된 아이템들을 bundle 형식으로 변환
        VBA 코드의 SumIfs 로직을 Python으로 구현
        
        Args:
            group_key: 그룹 키
            group_items: 그룹에 속한 아이템들
            
        Returns:
            Optional[dict]: bundle 형식의 데이터
        """
        try:
            if not group_items:
                return None
            
            # 첫 번째 아이템을 기준으로 기본 정보 설정
            base_item = group_items[0]
            
            # 합산 필드들 계산
            total_pay_cost = sum(float(item.get('pay_cost', 0) or 0) for item in group_items)
            total_sale_cnt = sum(int(item.get('sale_cnt', 0) or 0) for item in group_items)
            total_expected_payout = sum(float(item.get('expected_payout', 0) or 0) for item in group_items)
            total_service_fee = sum(float(item.get('service_fee', 0) or 0) for item in group_items)
            
            # 제품명들을 연결 (ConcatTxt 함수 로직)
            concatenated_item_names = self._concatenate_item_names(group_items)
            
            # bundle 형식으로 데이터 구성
            bundle_item = {
                # 기본 정보 (첫 번째 아이템 기준)
                'fld_dsp': base_item.get('fld_dsp'),                    # 사이트
                'receive_name': base_item.get('receive_name'),          # 수취인명
                'pay_cost': total_pay_cost,                             # 금액 (합산)
                'order_id': base_item.get('order_id'),                  # 주문번호 (첫 번째 것 사용)
                'item_name': concatenated_item_names,                   # 제품명 (연결된 문자열)
                'sale_cnt': total_sale_cnt,                             # 수량 (합산)
                'receive_cel': base_item.get('receive_cel'),            # 전화번호1
                'receive_tel': base_item.get('receive_tel'),            # 전화번호2
                'receive_addr': base_item.get('receive_addr'),          # 수취인주소
                'receive_zipcode': base_item.get('receive_zipcode'),    # 우편번호
                'delivery_method_str': base_item.get('delivery_method_str'),  # 선/착불
                'mall_product_id': base_item.get('mall_product_id'),    # 상품번호
                'delv_msg': base_item.get('delv_msg'),                  # 배송메세지
                'expected_payout': total_expected_payout,               # 정산예정금액 (합산)
                'service_fee': total_service_fee,                       # 서비스이용료 (합산)
                'mall_order_id': base_item.get('mall_order_id'),        # 장바구니번호
                'invoice_no': base_item.get('invoice_no'),              # 운송장번호
                'order_etc_7': base_item.get('order_etc_7'),            # 판매자관리코드
                'sku_no': base_item.get('sku_no'),                      # SKU번호
                
                # 추가 필드들 (첫 번째 아이템 기준)
                'sku_value': base_item.get('sku_value'),
                'product_name': base_item.get('product_name'),
                'delv_cost': base_item.get('delv_cost'),
                'sale_cost': base_item.get('sale_cost'),
                'mall_user_id': base_item.get('mall_user_id'),
                'user_name': base_item.get('user_name'),
                'sku1_no': base_item.get('sku1_no'),
                'sku1_cnt': base_item.get('sku1_cnt'),
                'sku2_no': base_item.get('sku2_no'),
                'sku2_cnt': base_item.get('sku2_cnt'),
                'pay_dt': base_item.get('pay_dt'),
                'user_tel': base_item.get('user_tel'),
                'user_cel': base_item.get('user_cel'),
                'buy_coupon': base_item.get('buy_coupon'),
                'delv_status': base_item.get('delv_status'),
                'order_dt': base_item.get('order_dt'),
                'order_method': base_item.get('order_method'),
                'delv_method_id': base_item.get('delv_method_id'),
                'sale_method': base_item.get('sale_method'),
                'sale_coupon': base_item.get('sale_coupon'),
                'batch_id': base_item.get('batch_id'),
                'reg_date': base_item.get('reg_date'),
            }
            
            return bundle_item
            
        except Exception as e:
            self.logger.error(f"bundle 아이템 생성 중 오류: {str(e)}")
            return None
    
    def _concatenate_item_names(self, group_items: List[dict]) -> str:
        """
        그룹 내 제품명들을 '+'로 연결
        VBA 코드의 ConcatTxt 함수 로직
        
        Args:
            group_items: 그룹에 속한 아이템들
            
        Returns:
            str: 연결된 제품명 문자열
        """
        try:
            item_names = []
            for item in group_items:
                item_name = item.get('item_name')
                if item_name and str(item_name).strip():
                    item_names.append(str(item_name).strip())
            
            # 중복 제거 후 연결
            unique_item_names = list(dict.fromkeys(item_names))  # 순서 유지하면서 중복 제거
            return '+'.join(unique_item_names)
            
        except Exception as e:
            self.logger.error(f"제품명 연결 중 오류: {str(e)}")
            return ""

    def _save_data_file(self, handler: SmileMacroHandler, file_type: str, merged_file_path: str) -> str:
        """
        데이터 파일을 저장하는 메서드
        
        Args:
            handler: SmileMacroHandler 객체
            file_type: 파일 타입 ('A', 'G', 'full', 'bundle')
            merged_file_path: 병합된 파일 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        filename = self._generate_filename(file_type)
        output_path = os.path.join(os.path.dirname(merged_file_path), filename)
        saved_path = handler.save_file(output_path)
        return saved_path
    
    def _save_bundle_data_to_excel(self, smile_macro_data_list_bundle: List[dict], file_type: str, merged_file_path: str) -> str:
        """
        bundle 데이터를 DataFrame으로 변환하여 Excel 파일로 저장하는 메서드
        
        Args:
            smile_macro_data_list_bundle: bundle 데이터 리스트
            file_type: 파일 타입 ('bundle')
            merged_file_path: 병합된 파일 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        bundle_filename = self._generate_filename(file_type)
        bundle_output_path = os.path.join(os.path.dirname(merged_file_path), bundle_filename)
        
        if smile_macro_data_list_bundle:
            df_bundle = pd.DataFrame(smile_macro_data_list_bundle)
            df_bundle.to_excel(bundle_output_path, index=False)
        else:
            # 빈 DataFrame 생성
            df_bundle = pd.DataFrame()
            df_bundle.to_excel(bundle_output_path, index=False)
        
        return bundle_output_path
    
    def _calculate_processed_rows(self, a_handler: SmileMacroHandler, g_handler: SmileMacroHandler, 
                                smile_macro_data_list_bundle: List[dict]) -> Tuple[int, int, int, int]:
        """
        처리된 행 수를 계산하는 메서드
        
        Args:
            a_handler: A 데이터 핸들러
            g_handler: G 데이터 핸들러
            smile_macro_data_list_bundle: bundle 데이터 리스트
            
        Returns:
            Tuple[int, int, int, int]: (a_processed_rows, g_processed_rows, bundle_processed_rows, total_processed_rows)
        """
        a_processed_rows = a_handler.ws.max_row - 1  # 헤더 제외
        g_processed_rows = g_handler.ws.max_row - 1  # 헤더 제외
        bundle_processed_rows = len(smile_macro_data_list_bundle) if smile_macro_data_list_bundle else 0
        total_processed_rows = a_processed_rows + g_processed_rows + bundle_processed_rows
        
        return a_processed_rows, g_processed_rows, bundle_processed_rows, total_processed_rows

    def _upload_single_file_to_minio(self, file_path: str, template_code: str, file_type: str) -> dict:
        """
        단일 파일을 MinIO에 업로드하는 메서드
        
        Args:
            file_path: 업로드할 파일 경로
            template_code: 템플릿 코드
            file_type: 파일 타입 ('a', 'g', 'bundle', 'full')
            
        Returns:
            dict: 업로드 결과 (file_url, minio_object_name, file_size)
        """
        try:
            file_name = os.path.basename(file_path)
            file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                file_path, template_code, file_name
            )
            file_url = url_arrange(file_url)
            
            return {
                f'{file_type}_file_url': file_url,
                f'{file_type}_minio_object_name': minio_object_name,
                f'{file_type}_file_size': file_size
            }
        except Exception as e:
            self.logger.error(f"{file_type} 파일 MinIO 업로드 실패: {str(e)}")
            raise e
    
    def _upload_multiple_files_to_minio(self, files_info: List[tuple]) -> dict:
        """
        여러 파일을 MinIO에 업로드하는 메서드
        
        Args:
            files_info: [(file_path, file_type), ...] 형태의 파일 정보 리스트
            
        Returns:
            dict: 모든 파일의 업로드 결과
        """
        try:
            template_code = "smile_macro"
            result = {}
            
            for file_path, file_type in files_info:
                if file_path and os.path.exists(file_path):
                    upload_result = self._upload_single_file_to_minio(file_path, template_code, file_type)
                    result.update(upload_result)
                else:
                    self.logger.warning(f"{file_type} 파일이 존재하지 않습니다: {file_path}")
                    # 빈 값으로 설정
                    result[f'{file_type}_file_url'] = None
                    result[f'{file_type}_minio_object_name'] = None
                    result[f'{file_type}_file_size'] = 0
            
            return result
            
        except Exception as e:
            self.logger.error(f"다중 파일 MinIO 업로드 실패: {str(e)}")
            raise e