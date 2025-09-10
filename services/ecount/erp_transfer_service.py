"""
ERP Transfer Service
ERP 데이터 전송을 위한 서비스 로직
"""

import pandas as pd
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from models.down_form_orders.down_form_order import BaseDownFormOrder
from models.ecount.ecount_models import EcountSale, EcountPurchase
from repository.down_form_order_repository import DownFormOrderRepository
from repository.ecount_sale_repository import EcountSaleRepository
from repository.ecount_purchase_repository import EcountPurchaseRepository
from services.ecount.erp_data_processor import ERPDataProcessor
from schemas.ecount.erp_transfer_dto import (
    ErpTransferRequestDto, 
    ErpTransferResponseDto, 
    ErpTransferDataDto,
    FormNameType
)
from utils.logs.sabangnet_logger import get_logger
from minio_handler import upload_and_get_url_and_size, url_arrange

logger = get_logger(__name__)


class ErpTransferService:
    """ERP 전송 서비스"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.down_form_order_repo = DownFormOrderRepository(session)
        self.erp_data_processor = ERPDataProcessor(session)
        self.ecount_sale_repo = EcountSaleRepository(session)
        self.ecount_purchase_repo = EcountPurchaseRepository(session)
    
    async def process_erp_transfer(
        self, 
        request: ErpTransferRequestDto
    ) -> ErpTransferResponseDto:
        """
        ERP 전송 처리
        
        Args:
            request: ERP 전송 요청 데이터
            
        Returns:
            ERP 전송 응답 데이터
        """
        try:
            # 1. 배치 ID 생성
            batch_id = self._generate_batch_id()
            
            # 2. 데이터 조회
            orders_data = await self._query_orders_data(request)
            
            if not orders_data:
                logger.warning(f"No data found for the given criteria: {request}")
                return ErpTransferResponseDto(
                    batch_id=batch_id,
                    total_records=0,
                    processed_records=0,
                    excel_file_name="",
                    form_name=request.form_name.value,
                    date_range={
                        "from": request.date_from.isoformat(),
                        "to": request.date_to.isoformat()
                    }
                )
            
            # 3. VBA 매크로 로직으로 데이터 처리
            processing_result = await self.erp_data_processor.process_orders(
                orders_data, 
                request.form_name, 
                batch_id
            )
            
            # 4. Excel 파일 생성
            excel_filename = await self._generate_excel_file_from_processed_data(
                processing_result.excel_data, 
                batch_id, 
                request.form_name.value
            )
            
            # 5. Excel 파일을 MinIO에 업로드
            download_url, file_size = await self._upload_excel_to_minio(
                excel_filename, 
                request.form_name.value
            )
            
            # 6. EcountSale/Purchase 데이터 저장 (upsert)
            await self._save_ecount_data_with_upsert(processing_result.ecount_erp_data, request.form_name)
            
            logger.info(f"ERP transfer completed successfully. Batch ID: {batch_id}, Records: {len(orders_data)}")
            
            return ErpTransferResponseDto(
                batch_id=processing_result.batch_id,
                total_records=processing_result.total_records,
                processed_records=processing_result.processed_records,
                excel_file_name=excel_filename,
                download_url=download_url,
                file_size=file_size,
                form_name=processing_result.form_name,
                date_range={
                    "from": request.date_from.isoformat(),
                    "to": request.date_to.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"ERP transfer failed: {str(e)}")
            raise e
    
    def _generate_batch_id(self) -> str:
        """배치 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"batch_{timestamp}_{unique_id}"
    
    async def _query_orders_data(self, request: ErpTransferRequestDto) -> List[BaseDownFormOrder]:
        """
        주문 데이터 조회
        
        Args:
            request: ERP 전송 요청 데이터
            
        Returns:
            조회된 주문 데이터 리스트
        """
        try:
            # 날짜 범위를 문자열로 변환
            date_from_str = request.date_from.strftime("%Y%m%d%H%M%S")
            date_to_str = request.date_to.strftime("%Y%m%d%H%M%S")
            
            # 기본 조건: 날짜 범위 및 work_status
            conditions = [
                BaseDownFormOrder.reg_date >= date_from_str,
                BaseDownFormOrder.reg_date <= date_to_str,
                BaseDownFormOrder.work_status == 'macro_run'
            ]
            
            # Form Name에 따른 추가 조건
            if request.form_name == FormNameType.OKMART_ERP_SALE_OK:
                # "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함되지 않은 데이터
                conditions.extend([
                    BaseDownFormOrder.form_name.like('%erp%'),
                    or_(
                        BaseDownFormOrder.fld_dsp.is_(None),
                        ~BaseDownFormOrder.fld_dsp.like('%아이예스%')
                    )
                ])
            elif request.form_name in [FormNameType.OKMART_ERP_SALE_IYES, FormNameType.IYES_ERP_SALE_IYES]:
                # "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함된 데이터
                conditions.extend([
                    BaseDownFormOrder.form_name.like('%erp%'),
                    BaseDownFormOrder.fld_dsp.like('%아이예스%')
                ])
            elif request.form_name == FormNameType.IYES_ERP_PURCHASE_IYES:
                # "erp"가 포함되고 "fld_dsp"에 "아이예스"가 포함된 데이터 (구매용)
                conditions.extend([
                    BaseDownFormOrder.form_name.like('%erp%'),
                    BaseDownFormOrder.fld_dsp.like('%아이예스%')
                ])
            
            # 쿼리 실행
            query = select(BaseDownFormOrder).where(and_(*conditions)).order_by(BaseDownFormOrder.id.desc())
            result = await self.session.execute(query)
            orders = result.scalars().all()
            
            logger.info(f"Found {len(orders)} orders for form_name: {request.form_name.value}")
            return orders
            
        except Exception as e:
            logger.error(f"Failed to query orders data: {str(e)}")
            raise e
    
    async def _create_dataframe(self, orders_data: List[BaseDownFormOrder]) -> pd.DataFrame:
        """
        주문 데이터를 DataFrame으로 변환
        
        Args:
            orders_data: 주문 데이터 리스트
            
        Returns:
            처리된 DataFrame
        """
        try:
            # 주문 데이터를 딕셔너리 리스트로 변환
            data_list = []
            for order in orders_data:
                data_dict = {
                    'idx': order.idx,
                    'order_id': order.order_id,
                    'mall_order_id': order.mall_order_id,
                    'product_id': order.product_id,
                    'product_name': order.product_name,
                    'mall_product_id': order.mall_product_id,
                    'item_name': order.item_name,
                    'sku_value': order.sku_value,
                    'sku_alias': order.sku_alias,
                    'sku_no': order.sku_no,
                    'barcode': order.barcode,
                    'model_name': order.model_name,
                    'erp_model_name': order.erp_model_name,
                    'sale_cnt': order.sale_cnt,
                    'pay_cost': int(order.pay_cost) if order.pay_cost else None,
                    'delv_cost': int(order.delv_cost) if order.delv_cost else None,
                    'total_cost': int(order.total_cost) if order.total_cost else None,
                    'expected_payout': int(order.expected_payout) if order.expected_payout else None,
                    'service_fee': int(order.service_fee) if order.service_fee else None,
                    'receive_name': order.receive_name,
                    'receive_cel': order.receive_cel,
                    'receive_tel': order.receive_tel,
                    'receive_addr': order.receive_addr,
                    'receive_zipcode': order.receive_zipcode,
                    'delv_msg': order.delv_msg,
                    'delivery_id': order.delivery_id,
                    'delivery_class': order.delivery_class,
                    'invoice_no': order.invoice_no,
                    'fld_dsp': order.fld_dsp,
                    'order_date': order.order_date.isoformat() if order.order_date else None,
                    'reg_date': order.reg_date,
                    'form_name': order.form_name
                }
                data_list.append(data_dict)
            
            # DataFrame 생성
            df = pd.DataFrame(data_list)
            
            # 데이터 정제 및 변환
            df = self._clean_dataframe(df)
            
            logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to create DataFrame: {str(e)}")
            raise e
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame 데이터 정제
        
        Args:
            df: 원본 DataFrame
            
        Returns:
            정제된 DataFrame
        """
        try:
            # NaN 값을 빈 문자열로 변환
            df = df.fillna('')
            
            # 숫자 컬럼의 타입 변환
            numeric_columns = ['pay_cost', 'delv_cost', 'total_cost', 'expected_payout', 'service_fee']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 날짜 컬럼 처리
            if 'order_date' in df.columns:
                df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
            
            # 문자열 길이 제한 (Excel 호환성)
            string_columns = df.select_dtypes(include=['object']).columns
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str[:32767]  # Excel 최대 문자 길이
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to clean DataFrame: {str(e)}")
            raise e
    
    async def _generate_excel_file_from_processed_data(
        self, 
        excel_data: Dict[str, List[Dict[str, Any]]], 
        batch_id: str, 
        form_name: str
    ) -> str:
        """
        처리된 데이터로부터 Excel 파일 생성 (여러 시트 포함)
        
        Args:
            excel_data: 처리된 Excel 데이터 (main_data, ecount_data 포함)
            batch_id: 배치 ID
            form_name: Form Name
            
        Returns:
            생성된 Excel 파일명
        """
        try:
            # 파일명 생성
            filename = f"ERP업로드용_{form_name}.xlsx"
            filepath = f"files/excel/{filename}"
            
            # 디렉토리 생성 (존재하지 않는 경우)
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Excel 파일 생성
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 메인 데이터 시트
                if excel_data.get('main_data'):
                    main_df = pd.DataFrame(excel_data['main_data'])
                    main_df.to_excel(writer, sheet_name='ERP_Data', index=False)
                
                # EcountSale/Purchase 데이터 시트
                if excel_data.get('ecount_data'):
                    ecount_df = pd.DataFrame(excel_data['ecount_data'])
                    if 'sale' in form_name:
                        sheet_name = '1_판매입력'
                    elif 'purchase' in form_name:
                        sheet_name = '구매입력'
                    else:
                        sheet_name = 'Ecount_Data'
                    ecount_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 요약 정보 시트
                total_records = len(excel_data.get('main_data', []))
                ecount_records = len(excel_data.get('ecount_data', []))
                summary_data = {
                    '항목': ['총 레코드 수', 'Ecount 레코드 수', '배치 ID', 'Form Name', '생성일시'],
                    '값': [total_records, ecount_records, batch_id, form_name, datetime.now().isoformat()]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Excel file generated: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate Excel file: {str(e)}")
            raise e
    
    async def _upload_excel_to_minio(
        self, 
        excel_filename: str, 
        form_name: str
    ) -> Tuple[str, int]:
        """
        Excel 파일을 MinIO에 업로드하고 URL과 파일 크기 반환
        
        Args:
            excel_filename: Excel 파일명
            form_name: Form Name
            
        Returns:
            (다운로드 URL, 파일 크기)
        """
        try:
            # 파일 경로 생성
            file_path = f"files/excel/{excel_filename}"
            
            # MinIO에 업로드
            file_url, minio_object_name, file_size = upload_and_get_url_and_size(
                file_path, 
                form_name, 
                excel_filename
            )
            
            # URL 정리 (쿼리스트링 제거)
            clean_url = url_arrange(file_url)
            
            logger.info(f"Excel file uploaded to MinIO: {clean_url}, size: {file_size} bytes")
            
            return clean_url, file_size
            
        except Exception as e:
            logger.error(f"Failed to upload Excel file to MinIO: {str(e)}")
            raise e

    async def _generate_excel_file(
        self, 
        df: pd.DataFrame, 
        batch_id: str, 
        form_name: str
    ) -> str:
        """
        Excel 파일 생성
        
        Args:
            df: 데이터 DataFrame
            batch_id: 배치 ID
            form_name: Form Name
            
        Returns:
            생성된 Excel 파일명
        """
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"erp_transfer_{form_name}_{timestamp}.xlsx"
            filepath = f"files/excel/{filename}"
            
            # 디렉토리 생성 (존재하지 않는 경우)
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Excel 파일 생성
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 메인 데이터 시트
                df.to_excel(writer, sheet_name='ERP_Data', index=False)
                
                # 요약 정보 시트
                summary_data = {
                    '항목': ['총 레코드 수', '배치 ID', 'Form Name', '생성일시'],
                    '값': [len(df), batch_id, form_name, datetime.now().isoformat()]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Excel file generated: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate Excel file: {str(e)}")
            raise e
    
    async def _save_ecount_data_with_upsert(
        self, 
        ecount_erp_data: List, 
        form_name: FormNameType
    ) -> None:
        """
        EcountSale/Purchase 데이터를 upsert로 저장
        
        Args:
            ecount_erp_data: 처리된 EcountSale/Purchase 데이터 리스트
            form_name: Form Name 타입
        """
        try:
            if not ecount_erp_data:
                logger.info("No ecount data to save")
                return
            
            if 'sale' in form_name.value:
                # SALE 데이터: EcountSale 테이블에 upsert (size_des 기준)
                created_count, updated_count = await self.ecount_sale_repo.upsert_sale_data(ecount_erp_data)
                logger.info(f"EcountSale upsert completed: {created_count} created, {updated_count} updated")
                
            elif 'purchase' in form_name.value:
                # PURCHASE 데이터: EcountPurchase 테이블에 upsert (prod_des 기준)
                created_count, updated_count = await self.ecount_purchase_repo.upsert_purchase_data(ecount_erp_data)
                logger.info(f"EcountPurchase upsert completed: {created_count} created, {updated_count} updated")
            
            else:
                logger.warning(f"Unknown form_name type: {form_name.value}")
                
        except Exception as e:
            logger.error(f"Failed to save ecount data with upsert: {str(e)}")
            raise e

    async def _save_ecount_sale_data_from_processed(
        self, 
        ecount_erp_data: List
    ) -> None:
        """
        처리된 EcountSale 데이터 저장
        
        Args:
            ecount_erp_data: 처리된 EcountSale 데이터 리스트
        """
        try:
            ecount_sale_records = []
            
            for ecount_data in ecount_erp_data:
                # EcountSale 레코드 생성
                ecount_sale = EcountSale(
                    com_code=ecount_data.com_code,
                    user_id=ecount_data.user_id,
                    emp_cd=ecount_data.emp_cd,
                    wh_cd=ecount_data.wh_cd,
                    io_type=ecount_data.io_type,
                    exchange_type=ecount_data.exchange_type,
                    exchange_rate=ecount_data.exchange_rate,
                    
                    # 주문 정보 매핑
                    io_date=ecount_data.io_date,
                    upload_ser_no=ecount_data.upload_ser_no,
                    cust=ecount_data.cust,
                    cust_des=ecount_data.cust_des,
                    
                    # 상품 정보
                    prod_cd=ecount_data.prod_cd,
                    prod_des=ecount_data.prod_des,
                    qty=ecount_data.qty,
                    price=ecount_data.price,
                    exchange_cost=ecount_data.exchange_cost,
                    supply_amt=ecount_data.supply_amt,
                    vat_amt=ecount_data.vat_amt,
                    
                    # 고객 정보
                    u_memo1=ecount_data.u_memo1,
                    u_memo2=ecount_data.u_memo2,
                    u_memo3=ecount_data.u_memo3,
                    u_txt1=ecount_data.u_txt1,
                    u_memo4=ecount_data.u_memo4,
                    u_memo5=ecount_data.u_memo5,
                    
                    # 기타 정보
                    remarks=ecount_data.remarks,
                    p_remarks2=ecount_data.p_remarks2,
                    p_remarks1=ecount_data.p_remarks1,
                    p_remarks3=ecount_data.p_remarks3,
                    size_des=ecount_data.size_des,
                    p_amt1=ecount_data.p_amt1,
                    p_amt2=ecount_data.p_amt2,
                    item_cd=ecount_data.item_cd,
                    
                    # 메타 정보
                    is_test=ecount_data.is_test,
                    work_status=ecount_data.work_status,
                    batch_id=ecount_data.batch_id,
                    template_code=ecount_data.template_code
                )
                
                ecount_sale_records.append(ecount_sale)
            
            # 배치 저장
            self.session.add_all(ecount_sale_records)
            await self.session.commit()
            
            logger.info(f"Saved {len(ecount_sale_records)} EcountSale records with batch_id: {ecount_erp_data[0].batch_id if ecount_erp_data else 'N/A'}")
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save EcountSale data: {str(e)}")
            raise e

    async def _save_ecount_sale_data(
        self, 
        orders_data: List[BaseDownFormOrder], 
        batch_id: str, 
        form_name: str
    ) -> None:
        """
        EcountSale 데이터 저장
        
        Args:
            orders_data: 주문 데이터 리스트
            batch_id: 배치 ID
            form_name: Form Name
        """
        try:
            ecount_sale_records = []
            
            for order in orders_data:
                # EcountSale 레코드 생성
                ecount_sale = EcountSale(
                    com_code="000001",  # 기본 회사코드
                    user_id="system",   # 기본 사용자ID
                    emp_cd="system",    # 기본 담당자
                    wh_cd="01",         # 기본 출하창고
                    io_type="1",        # 기본 거래유형 (판매)
                    exchange_type="KRW", # 기본 통화
                    exchange_rate=1.0,   # 기본 환율
                    
                    # 주문 정보 매핑
                    io_date=order.reg_date[:8] if order.reg_date else None,  # YYYYMMDD 형식
                    upload_ser_no=order.seq,
                    cust="",  # 거래처코드 (필요시 매핑)
                    cust_des="",  # 거래처명 (필요시 매핑)
                    
                    # 상품 정보
                    prod_cd=order.product_id or "",
                    prod_des=order.product_name or "",
                    qty=float(order.sale_cnt) if order.sale_cnt else 0,
                    price=float(order.pay_cost) if order.pay_cost else 0,
                    exchange_cost=float(order.pay_cost) if order.pay_cost else 0,
                    supply_amt=float(order.pay_cost) if order.pay_cost else 0,
                    vat_amt=0,  # 부가세 (필요시 계산)
                    
                    # 고객 정보
                    u_memo1="",  # E-MAIL
                    u_memo2="",  # FAX
                    u_memo3=order.receive_cel or "",  # 연락처
                    u_txt1=order.receive_addr or "",  # 주소
                    u_memo4="",  # 매장판매 결제구분
                    u_memo5="",  # 매장판매 거래구분
                    
                    # 기타 정보
                    remarks=f"{order.receive_name or ''}/{order.order_id or ''}/{order.receive_cel or ''}/{order.receive_addr or ''}",
                    p_remarks2=order.delv_msg or "",  # 배송메시지
                    p_remarks1=order.invoice_no or "",  # 송장번호
                    p_remarks3=order.mall_product_id or "",  # 상품번호
                    size_des=order.order_id or "",  # 주문번호
                    p_amt1=float(order.expected_payout) if order.expected_payout else 0,  # 정산예정금액
                    p_amt2=float(order.service_fee) if order.service_fee else 0,  # 서비스이용료
                    item_cd="",  # 운임비타입
                    
                    # 메타 정보
                    is_test=True,
                    work_status="ERP 업로드 전",
                    batch_id=batch_id,
                    template_code=form_name
                )
                
                ecount_sale_records.append(ecount_sale)
            
            # 배치 저장
            self.session.add_all(ecount_sale_records)
            await self.session.commit()
            
            logger.info(f"Saved {len(ecount_sale_records)} EcountSale records with batch_id: {batch_id}")
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to save EcountSale data: {str(e)}")
            raise e
