import pandas as pd
import os
import random
import string
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logs.sabangnet_logger import get_logger
from utils.macros.smile.smile_macro_handler import SmileMacroHandler
from utils.macros.smile.smile_common_utils import SmileCommonUtils
from repository.smile_erp_data_repository import SmileErpDataRepository
from repository.smile_settlement_data_repository import SmileSettlementDataRepository
from repository.smile_sku_data_repository import SmileSkuDataRepository
from repository.smile_macro_repository import SmileMacroRepository
from schemas.smile.smile_macro_dto import (
    SmileMacroRequestDto, 
    SmileMacroResponseDto, 
    SmileMacroStageRequestDto
)
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
    
    def _generate_random_alphabat(self) -> str:
        """랜덤 알파벳 생성"""
        return ''.join(random.choices(string.ascii_uppercase, k=1))
    
    def _get_site_name_from_column_a(self, first_char: str) -> str:
        """A 컬럼의 첫 글자를 기준으로 사이트명 반환"""
        if first_char.upper() == 'A':
            return "옥션"
        elif first_char.upper() == 'G':
            return "G마켓"
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
    
    async def save_macro_handler_to_db(self, macro_handler: SmileMacroHandler) -> bool:
        """
        매크로 핸들러의 데이터를 DB에 저장
        
        Args:
            macro_handler: 매크로 핸들러
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            if not self.session:
                self.logger.warning("데이터베이스 세션이 없습니다. DB 저장을 건너뜁니다.")
                return False
            
            # 컬럼 매핑 정보 (source_field -> target_column)
            column_mapping = {
                'A': 'fld_dsp',           # 아이디*
                'B': 'expected_payout', # 정산예정금??
                'C': 'service_fee',    # 서비스 이용료
                'D': 'mall_order_id',  # 장바구니번호(결제번호)
                'E': 'pay_cost',       # 금액[배송비미포함]
                'F': 'delv_cost',      # 배송비 금액
                'G': None,             # 구매결정일자 - source_field 없음
                'H': 'mall_product_id', # 상품번호*
                'I': 'order_id',       # 주문번호*
                'J': 'chat_1',         # 주문옵션
                'K': 'product_name',   # 상품명
                'L': 'item_name',      # 제품명
                'M': 'sale_cnt',       # 수량
                'N': None,             # 추가구성 - source_field 없음
                'O': None,             # 사은품 - source_field 없음
                'P': 'sale_cost',      # 판매금액
                'Q': 'mall_user_id',   # 구매자ID
                'R': 'user_name',      # 구매자명
                'S': 'receive_name',   # 수령인명
                'T': 'delivery_method_str', # 배송비
                'U': 'receive_cel',    # 수령인 휴대폰
                'V': 'receive_tel',    # 수령인 전화번호
                'W': 'receive_addr',   # 주소
                'X': 'receive_zipcode', # 우편번호
                'Y': 'delv_msg',       # 배송시 요구사항
                'Z': None,             # (옥션)복수구매할인 - source_field 없음
                'AA': None,            # (옥션)우수회원할인 - source_field 없음
                'AB': 'sku1_num',      # SKU1번호
                'AC': 'sku1_cnt',      # SKU1수량
                'AD': 'sku2_num',      # SKU2번호
                'AE': 'sku2_cnt',      # SKU2수량
                'AF': 'sku_num',       # SKU번호 및 수량
                'AG': 'pay_dt',        # 결제완료일
                'AH': 'user_tel',      # 구매자 전화번호
                'AI': 'user_cel',      # 구매자 휴대폰
                'AJ': 'buy_coupon',    # 구매쿠폰적용금액
                'AK': None,            # 발송예정일 - source_field 없음
                'AL': None,            # 발송일자 - source_field 없음
                'AM': None,            # 배송구분 - source_field 없음
                'AN': 'delv_id',       # 배송번호
                'AO': 'delv_status',   # 배송상태
                'AP': None,            # 배송완료일자 - source_field 없음
                'AQ': None,            # 배송지연사유 - source_field 없음
                'AR': None,            # 배송점포 - source_field 없음
                'AS': None,            # 상품미수령상세사유 - source_field 없음
                'AT': None,            # 상품미수령신고사유 - source_field 없음
                'AU': None,            # 상품미수령신고일자 - source_field 없음
                'AV': None,            # 상품미수령이의제기일자 - source_field 없음
                'AW': None,            # 상품미수령철회요청일자 - source_field 없음
                'AX': None,            # 송장번호(방문수령인증키) - source_field 없음
                'AY': None,            # 일시불할인 - source_field 없음
                'AZ': None,            # 재배송일 - source_field 없음
                'BA': None,            # 재배송지 우편번호 - source_field 없음
                'BB': None,            # 재배송지 운송장번호 - source_field 없음
                'BC': None,            # 재배송지 주소 - source_field 없음
                'BD': None,            # 재배송택배사명 - source_field 없음
                'BE': None,            # 정산완료일 - source_field 없음
                'BF': 'order_dt',      # 주문일자(결제확인전)
                'BG': 'order_method',  # 주문종류
                'BH': None,            # 주문확인일자 - source_field 없음
                'BI': 'delv_method_id', # 택배사명(발송방법)
                'BJ': None,            # 판매단가 - source_field 없음 (sale_cost와 중복)
                'BK': 'sale_method',   # 판매방식
                'BL': 'order_etc_7',   # 판매자 관리코드
                'BM': None,            # 판매자 상세관리코드 - source_field 없음
                'BN': None,            # 판매자북캐시적립 - source_field 없음
                'BO': 'sale_coupon',   # 판매자쿠폰할인
                'BP': None,            # 판매자포인트적립 - source_field 없음
            }
            
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
                    
                    # 데이터 타입 변환
                    if field_name in ['sale_cnt']:
                        # 정수형 필드
                        try:
                            if cell_value is not None and str(cell_value).strip():
                                row_data[field_name] = int(float(cell_value))
                            else:
                                row_data[field_name] = None
                        except (ValueError, TypeError):
                            row_data[field_name] = None
                    elif field_name in ['expected_payout', 'service_fee', 'pay_cost', 'delv_cost', 'sale_cost', 'buy_coupon', 'sale_coupon']:
                        # 숫자형 필드
                        try:
                            if cell_value is not None and str(cell_value).strip():
                                # 문자열 정리 (쉼표, 원화 기호 제거)
                                cleaned_value = str(cell_value).replace(',', '').replace('₩', '').replace('원', '').strip()
                                if cleaned_value:
                                    row_data[field_name] = float(cleaned_value)
                                else:
                                    row_data[field_name] = None
                            else:
                                row_data[field_name] = None
                        except (ValueError, TypeError):
                            row_data[field_name] = None
                    elif field_name in ['pay_dt', 'order_dt']:
                        # 날짜형 필드
                        try:
                            if cell_value is not None and str(cell_value).strip():
                                from datetime import datetime
                                # 다양한 날짜 형식 처리
                                date_str = str(cell_value).strip()
                                if len(date_str) == 10:  # YYYY-MM-DD
                                    row_data[field_name] = datetime.strptime(date_str, '%Y-%m-%d').date()
                                elif len(date_str) == 8:  # YYYYMMDD
                                    row_data[field_name] = datetime.strptime(date_str, '%Y%m%d').date()
                                else:
                                    row_data[field_name] = None
                            else:
                                row_data[field_name] = None
                        except (ValueError, TypeError):
                            row_data[field_name] = None
                    else:
                        # 문자열 필드
                        if cell_value is not None:
                            row_data[field_name] = str(cell_value).strip()
                        else:
                            row_data[field_name] = None
                
                smile_macro_data_list.append(row_data)
            
            # DB에 저장
            if smile_macro_data_list:
                await self.smile_macro_repository.create_multiple_smile_macro(smile_macro_data_list)
                self.logger.info(f"매크로 핸들러 데이터 {len(smile_macro_data_list)}개 DB 저장 완료")
                return True
            else:
                self.logger.warning("저장할 데이터가 없습니다.")
                return False
                
        except Exception as e:
            self.logger.error(f"매크로 핸들러 DB 저장 중 오류: {str(e)}")
            return False
    
    async def process_smile_macro_with_db(self, file_path: str, output_path: Optional[str] = None) -> SmileMacroResponseDto:
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
            
            # 6-8단계 처리 후 데이터 행 수 확인
            after_stage_8_rows = macro_handler.ws.max_row - 1  # 헤더 제외
            self.logger.info(f"6-8단계 처리 후 데이터 행 수: {after_stage_8_rows}")
            
            # macro_handler에 헤더 변경
            SmileCommonUtils.update_smile_macro_headers(macro_handler.ws)

            # A 컬럼을 기준으로 데이터 분리, Header 변경
            a_handler, g_handler = self._split_data_by_column_a(macro_handler)

            # A 데이터 값 변경
            SmileCommonUtils.transform_column_a_data(macro_handler.ws)
            # macro_handler DB에 저장 
            await self.save_macro_handler_to_db(macro_handler)
            
            # A 데이터 파일 저장
            a_filename = self._generate_filename('A')
            a_output_path = os.path.join(os.path.dirname(file_path), a_filename)
            a_saved_path = a_handler.save_file(a_output_path)
            
            # G 데이터 파일 저장
            g_filename = self._generate_filename('G')
            g_output_path = os.path.join(os.path.dirname(file_path), g_filename)
            g_saved_path = g_handler.save_file(g_output_path)
            
            # 처리된 행 수 계산
            a_processed_rows = a_handler.ws.max_row - 1  # 헤더 제외
            g_processed_rows = g_handler.ws.max_row - 1  # 헤더 제외
            total_processed_rows = a_processed_rows + g_processed_rows
            
            self.logger.info(f"데이터베이스 기반 스마일배송 매크로 처리 완료: A파일={a_saved_path}({a_processed_rows}행), G파일={g_saved_path}({g_processed_rows}행)")
            
            return SmileMacroResponseDto(
                success=True,
                message="데이터베이스 기반 스마일배송 매크로 처리가 성공적으로 완료되었습니다.",
                output_path=a_saved_path,
                output_path2=g_saved_path,
                processed_rows=total_processed_rows
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
    
    async def merge_and_process_files_with_minio(self, file_paths: List[str]) -> Dict[str, Any]:
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
            result = await self.process_smile_macro_with_db(merged_file_path, None)
            
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
                template_code = "smile_macro"
                
                # A 파일 업로드
                a_file_name = os.path.basename(result.output_path)
                a_file_url, a_minio_object_name, a_file_size = upload_and_get_url_and_size(
                    result.output_path, template_code, a_file_name
                )
                a_file_url = url_arrange(a_file_url)
                
                # G 파일 업로드
                g_file_name = os.path.basename(result.output_path2)
                g_file_url, g_minio_object_name, g_file_size = upload_and_get_url_and_size(
                    result.output_path2, template_code, g_file_name
                )
                g_file_url = url_arrange(g_file_url)
                
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
                    "output_path2": result.output_path2
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
    
    async def get_erp_data_from_db(self, fld_dsp: Optional[str] = None) -> pd.DataFrame:
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
            
            if fld_dsp:
                erp_data_list = await self.erp_repository.get_erp_data_by_fld_dsp(fld_dsp)
            else:
                erp_data_list = await self.erp_repository.get_all_erp_data()
            
            # ORM 객체를 딕셔너리로 변환
            erp_data_dicts = []
            for erp_data in erp_data_list:
                erp_data_dicts.append({
                    '날짜': erp_data.date.strftime('%Y-%m-%d') if erp_data.date else None,
                    '사이트': erp_data.fld_dsp,
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
            
            # ORM 객체를 딕셔너리로 변환
            sku_data_dicts = []
            for sku_data in sku_data_list:
                sku_data_dicts.append({
                    sku_data.sku_number: sku_data.model_name
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