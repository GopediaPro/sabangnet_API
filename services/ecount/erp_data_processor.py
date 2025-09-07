"""
ERP Data Processor
VBA 매크로 로직을 기반으로 한 데이터 처리 서비스
"""

import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from models.down_form_orders.down_form_order import BaseDownFormOrder
from models.ecount.erp_partner_code import EcountErpPartnerCode
from models.ecount.iyes_cost import EcountIyesCost
from schemas.ecount.erp_data_processing_dto import (
    ProcessedOrderData,
    OKMartProcessedData,
    IYESProcessedData,
    EcountSaleData,
    EcountPurchaseData,
    ERPProcessingResult
)
from schemas.ecount.erp_transfer_dto import FormNameType
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class ERPDataProcessor:
    """ERP 데이터 처리기 (VBA 매크로 로직 구현)"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def process_orders(
        self, 
        orders: List[BaseDownFormOrder], 
        form_name: FormNameType,
        batch_id: str
    ) -> ERPProcessingResult:
        """
        주문 데이터를 VBA 매크로 로직에 따라 처리
        
        Args:
            orders: 원본 주문 데이터
            form_name: Form Name 타입
            batch_id: 배치 ID
            
        Returns:
            처리된 ERP 데이터
        """
        try:
            logger.info(f"Starting ERP data processing for {form_name.value}, {len(orders)} orders")
            
            # Step 1-2: 원본 데이터 복사 및 노란색 행 삭제 (실제로는 필터링)
            filtered_orders = self._filter_yellow_rows(orders)
            
            # Step 3-14: 공통 처리 로직
            processed_orders = await self._process_common_steps(filtered_orders)
            
            # Form Name에 따른 차별화 처리
            if form_name == FormNameType.OKMART_ERP_SALE_OK:
                final_orders = await self._process_okmart_specific(processed_orders)
            else:  # IYES 계열
                final_orders = await self._process_iyes_specific(processed_orders)
            
            # EcountSale/Purchase 데이터 생성
            if 'sale' in form_name.value:
                ecount_erp_data = self._create_ecount_sale_data(final_orders, batch_id, form_name)
            elif 'purchase' in form_name.value:
                ecount_erp_data = self._create_ecount_purchase_data(final_orders, batch_id, form_name)
            else:
                ecount_erp_data = []
            # Excel 데이터 생성
            excel_data = self._create_excel_data(final_orders, ecount_erp_data, form_name)
            
            logger.info(f"ERP data processing completed. Processed {len(final_orders)} orders")
            
            return ERPProcessingResult(
                excel_data=excel_data,
                ecount_erp_data=ecount_erp_data,
                batch_id=batch_id,
                form_name=form_name.value,
                total_records=len(orders),
                processed_records=len(final_orders)
            )
            
        except Exception as e:
            logger.error(f"ERP data processing failed: {str(e)}")
            raise e
    
    def _filter_yellow_rows(self, orders: List[BaseDownFormOrder]) -> List[BaseDownFormOrder]:
        """
        Step 2: 노란색 행 삭제 (실제로는 특정 조건으로 필터링)
        VBA에서는 노란색 셀을 찾아서 삭제하지만, 여기서는 특정 조건으로 필터링
        """
        # 실제 구현에서는 노란색 셀 조건을 정의해야 함
        # 예시: 특정 상태나 조건의 데이터를 제외
        filtered = []
        for order in orders:
            # 예시 조건: work_status가 특정 값이 아닌 경우만 포함
            if order.work_status not in ['삭제', '취소']:  # 실제 조건에 맞게 수정
                filtered.append(order)
        
        logger.info(f"Filtered {len(orders)} orders to {len(filtered)} orders")
        return filtered
    
    async def _process_common_steps(self, orders: List[BaseDownFormOrder]) -> List[ProcessedOrderData]:
        """
        Step 3-14: 공통 처리 로직
        """
        processed_orders = []
        
        for order in orders:
            try:
                # Step 3-6: "+" 모델명 분리 및 수량 계산
                divided_orders = self._split_models_and_calculate_qty(order)
                
                for divided_order in divided_orders:
                    # Step 7: 실수량 계산
                    real_qty = self._calculate_real_qty(divided_order)
                    
                    # logger.info(f"[주문분할처리] 주문ID: {divided_order.order_id}, 상품명: {divided_order.item_name}, "
                    #           f"etc_cost: {str(divided_order.etc_cost) if divided_order.etc_cost else 'None'}, sale_cnt: {divided_order.sale_cnt}, "
                    #           f"실수량: {real_qty}")
                    
                    # Step 8: 단가/공급가액/부가세 계산
                    price_info = self._calculate_price_info(divided_order, real_qty)
                    
                    # Step 9: 제품명에서 수량 텍스트 제거
                    clean_item_name = self._remove_qty_text(divided_order.item_name)
                    
                    # Step 10: ERP품목명 조회
                    erp_product_name = await self._get_erp_product_name(clean_item_name)
                    
                    # Step 11: 사이트코드 조회
                    site_code = await self._get_site_code(divided_order.fld_dsp)
                    
                    # Step 12: 적요 생성
                    remarks = self._create_remarks(divided_order, clean_item_name)
                    
                    # Step 14: 상품번호_SKU 생성
                    mall_product_id_sku = self._create_mall_product_id_sku(
                        divided_order.mall_product_id, 
                        divided_order.sku_no
                    )
                    
                    # ProcessedOrderData 생성
                    processed_data = ProcessedOrderData(
                        seq=divided_order.seq,
                        fld_dsp=divided_order.fld_dsp,
                        receive_name=divided_order.receive_name,
                        etc_cost=divided_order.etc_cost,
                        order_id=divided_order.order_id,
                        item_name_only_name=clean_item_name,
                        erp_product_name=erp_product_name,
                        devided_cnt=divided_order.sale_cnt,
                        real_cnt=real_qty,
                        price=price_info['price'],
                        supply_amt=price_info['supply_amt'],
                        vat_amt=price_info['vat_amt'],
                        remarks=remarks,
                        receive_cel=divided_order.receive_cel,
                        receive_tel=divided_order.receive_tel,
                        receive_addr=divided_order.receive_addr,
                        receive_zipcode=divided_order.receive_zipcode,
                        delivery_method_str=divided_order.delivery_method_str,
                        mall_product_id=divided_order.mall_product_id,
                        mall_product_id_sku=mall_product_id_sku,
                        delv_msg=divided_order.delv_msg,
                        expected_payout=divided_order.expected_payout,
                        service_fee=divided_order.service_fee,
                        mall_order_id=divided_order.mall_order_id,
                        invoice_no=divided_order.invoice_no,
                        order_etc_7=divided_order.order_etc_7,
                        sku_no=divided_order.sku_no,
                        site_code=site_code
                    )
                    
                    processed_orders.append(processed_data)
                    
            except Exception as e:
                logger.error(f"Error processing order {order.id}: {str(e)}")
                continue
        
        return processed_orders
    
    def _split_models_and_calculate_qty(self, order: BaseDownFormOrder) -> List[BaseDownFormOrder]:
        """
        Step 3-6: "+" 모델명 분리 및 수량 계산
        """
        # logger.info(f"[모델분리] 원본 주문ID: {order.order_id}, 상품명: {order.item_name}, "
        #            f"etc_cost: {str(order.etc_cost) if order.etc_cost else 'None'}, sale_cnt: {order.sale_cnt}")
        
        if not order.item_name or '+' not in order.item_name:
            # logger.info(f"[모델분리] 분리 불필요 - 단일 상품: {order.item_name}")
            return [order]
        
        # "+"로 분리
        parts = order.item_name.split('+')
        divided_orders = []
        
        # logger.info(f"[모델분리] 분리된 부분들: {parts}")
        
        for part in parts:
            part = part.strip()
            if '[사은품]' in part:
                logger.info(f"[모델분리] 사은품 제외: {part}")
                continue  # 사은품 제외
            
            # 새로운 주문 객체 생성 (복사)
            new_order = BaseDownFormOrder()
            for attr in dir(order):
                if not attr.startswith('_') and not callable(getattr(order, attr)):
                    setattr(new_order, attr, getattr(order, attr))
            
            new_order.item_name = part
            divided_orders.append(new_order)
            logger.info(f"[모델분리] 분리된 주문 생성: {part}")
        
        result = divided_orders if divided_orders else [order]
        logger.info(f"[모델분리] 최종 분리 결과: {len(result)}개 주문")
        return result
    
    def _calculate_real_qty(self, order: BaseDownFormOrder) -> int:
        """
        Step 7: 실수량 계산
        """
        if not order.item_name:
            logger.info(f"[실수량계산] 상품명 없음 - 기본값 1 반환")
            return 1
        
        # 정규식으로 "숫자개" 패턴 찾기
        qty_pattern = r'(\d+)개'
        match = re.search(qty_pattern, order.item_name, re.IGNORECASE)
        
        if match:
            qty = int(match.group(1))
            # logger.info(f"[실수량계산] 상품명: {order.item_name}, 추출된 수량: {qty}")
            return qty
        else:
            # logger.info(f"[실수량계산] 수량 패턴 없음 - 기본값 1 반환: {order.item_name}")
            return 1
    
    def _calculate_price_info(self, order: BaseDownFormOrder, real_qty: int) -> Dict[str, Decimal]:
        """
        Step 8: 단가/공급가액/부가세 계산
        """
        # logger.info(f"[가격계산] 주문ID: {order.order_id}, 상품명: {order.item_name}, 실수량: {real_qty}")
        
        if '[사은품]' in (order.item_name or ''):
            logger.info(f"[가격계산] 사은품으로 인해 0 반환: {order.item_name}")
            return {
                'price': Decimal('0'),
                'supply_amt': Decimal('0'),
                'vat_amt': Decimal('0')
            }
        
        # etc_cost가 문자열이거나 None인 경우 처리
        if order.etc_cost and str(order.etc_cost).strip():
            try:
                etc_cost = Decimal(str(order.etc_cost))
            except (ValueError, TypeError):
                logger.warning(f"[가격계산] etc_cost 변환 실패: {order.etc_cost}")
                etc_cost = Decimal('0')
        else:
            logger.info(f"[가격계산] etc_cost가 None/빈값: {order.etc_cost}")
            etc_cost = Decimal('0')
        
        sale_cnt = int(order.sale_cnt or 1)
        
        # logger.info(f"[가격계산] etc_cost: {etc_cost}, sale_cnt: {sale_cnt}")
        
        # 단가 = ROUND(etc_cost / sale_cnt, 0)
        price = round(etc_cost / sale_cnt, 0)
        
        # 공급가액 = 단가 * 실수량
        supply_amt = price * real_qty
        
        # 부가세 = 공급가액 / 10
        vat_amt = supply_amt / 10
        
        # logger.info(f"[가격계산] 계산결과 - 단가: {price}, 공급가액: {supply_amt}, 부가세: {vat_amt}")
        
        return {
            'price': price,
            'supply_amt': supply_amt,
            'vat_amt': vat_amt
        }
    
    def _remove_qty_text(self, item_name: Optional[str]) -> Optional[str]:
        """
        Step 9: 제품명에서 수량 텍스트 제거
        """
        if not item_name:
            return item_name
        
        # 정규식으로 "숫자개" 패턴 제거
        qty_pattern = r'\s*\d{1,4}개(?=\s*[\(<])|\s*\d{1,4}개$'
        clean_name = re.sub(qty_pattern, '', item_name, flags=re.IGNORECASE)
        
        return clean_name.strip()
    
    async def _get_erp_product_name(self, item_name: Optional[str]) -> Optional[str]:
        """
        Step 10: ERP품목명 조회
        """
        if not item_name:
            return None
        
        try:
            # ecount_erp_partner_code 테이블에서 조회
            query = select(EcountErpPartnerCode.product_nm).where(
                EcountErpPartnerCode.product_nm.like(f'%{item_name}%')
            ).limit(1)
            
            result = await self.session.execute(query)
            product_nm = result.scalar_one_or_none()
            
            return product_nm
            
        except Exception as e:
            logger.error(f"Error getting ERP product name for {item_name}: {str(e)}")
            return None
    
    async def _get_site_code(self, fld_dsp: Optional[str]) -> Optional[str]:
        """
        Step 11: 사이트코드 조회
        """
        if not fld_dsp:
            return None
        
        try:
            # ecount_erp_partner_code 테이블에서 조회
            query = select(EcountErpPartnerCode.partner_code).where(
                EcountErpPartnerCode.fld_dsp == fld_dsp
            ).limit(1)
            
            result = await self.session.execute(query)
            partner_code = result.scalar_one_or_none()
            
            return partner_code
            
        except Exception as e:
            logger.error(f"Error getting site code for {fld_dsp}: {str(e)}")
            return None
    
    def _create_remarks(self, order: BaseDownFormOrder, clean_item_name: Optional[str]) -> str:
        """
        Step 12: 적요 생성
        """
        parts = [
            order.fld_dsp or '',
            str(order.etc_cost or ''),
            clean_item_name or '',
            str(order.expected_payout or ''),
            str(order.service_fee or ''),
            order.mall_order_id or '',
            order.delv_msg or ''
        ]
        
        return '/'.join(parts)
    
    def _create_mall_product_id_sku(self, mall_product_id: Optional[str], sku_no: Optional[str]) -> str:
        """
        Step 14: 상품번호_SKU 생성
        """
        if not mall_product_id:
            return ''
        
        if sku_no and sku_no.strip():
            return f"{mall_product_id}/{sku_no}"
        else:
            return mall_product_id
    
    async def _process_okmart_specific(self, orders: List[ProcessedOrderData]) -> List[OKMartProcessedData]:
        """
        Step 15-16: OKMart 특화 처리
        """
        okmart_orders = []
        
        for order in orders:
            # Step 15: 창고 조회
            warehouse = await self._get_warehouse(order.fld_dsp)
            
            okmart_order = OKMartProcessedData(**order.model_dump())
            okmart_order.warehouse = warehouse
            okmart_orders.append(okmart_order)
        
        return okmart_orders
    
    async def _process_iyes_specific(self, orders: List[ProcessedOrderData]) -> List[IYESProcessedData]:
        """
        Step 15-17: IYES 특화 처리
        """
        iyes_orders = []
        
        for order in orders:
            # Step 15: 창고 조회 및 조정
            warehouse = await self._get_warehouse(order.fld_dsp)
            warehouse_adjustment = self._adjust_warehouse(warehouse)
            
            # Step 16: 구매단가 조회 및 계산
            purchase_info = await self._calculate_purchase_info(order.item_name_only_name, order.real_cnt)
            
            # Step 17: 사이트 코드 추가
            iyes_order = IYESProcessedData(**order.model_dump())
            iyes_order.warehouse = warehouse
            iyes_order.warehouse_adjustment = warehouse_adjustment
            iyes_order.purchase_price = purchase_info['price']
            iyes_order.purchase_supply_amt = purchase_info['supply_amt']
            iyes_order.purchase_vat_amt = purchase_info['vat_amt']
            iyes_order.site_okmart = "1198652000"
            iyes_order.site_iyes = "8768600978"
            
            iyes_orders.append(iyes_order)
        
        return iyes_orders
    
    async def _get_warehouse(self, fld_dsp: Optional[str]) -> Optional[str]:
        """
        창고 코드 조회
        """
        if not fld_dsp:
            return None
        
        try:
            query = select(EcountErpPartnerCode.wh_cd).where(
                EcountErpPartnerCode.fld_dsp == fld_dsp
            ).limit(1)
            
            result = await self.session.execute(query)
            wh_cd = result.scalar_one_or_none()
            
            return wh_cd
            
        except Exception as e:
            logger.error(f"Error getting warehouse for {fld_dsp}: {str(e)}")
            return None
    
    def _adjust_warehouse(self, warehouse: Optional[str]) -> Optional[str]:
        """
        창고 조정: 10→100, 16→160
        """
        if warehouse == "10":
            return "100"
        elif warehouse == "16":
            return "160"
        else:
            return ""
    
    async def _calculate_purchase_info(self, item_name: Optional[str], real_qty: int) -> Dict[str, Decimal]:
        """
        구매단가/구매공급가/구매부가세 계산
        """
        if not item_name:
            return {
                'price': Decimal('0'),
                'supply_amt': Decimal('0'),
                'vat_amt': Decimal('0')
            }
        
        try:
            # ecount_iyes_cost 테이블에서 조회
            query = select(EcountIyesCost.price).where(
                EcountIyesCost.product_nm.like(f'%{item_name}%')
            ).limit(1)
            
            result = await self.session.execute(query)
            purchase_price = result.scalar_one_or_none()
            
            if purchase_price:
                purchase_price = Decimal(str(purchase_price))
                purchase_supply_amt = purchase_price * real_qty
                purchase_vat_amt = purchase_supply_amt / 10
            else:
                purchase_price = Decimal('0')
                purchase_supply_amt = Decimal('0')
                purchase_vat_amt = Decimal('0')
            
            return {
                'price': purchase_price,
                'supply_amt': purchase_supply_amt,
                'vat_amt': purchase_vat_amt
            }
            
        except Exception as e:
            logger.error(f"Error calculating purchase info for {item_name}: {str(e)}")
            return {
                'price': Decimal('0'),
                'supply_amt': Decimal('0'),
                'vat_amt': Decimal('0')
            }
    
    def _create_excel_data(self, orders: List, ecount_erp_data: List, form_name: FormNameType) -> Dict[str, List[Dict[str, Any]]]:
        """
        Excel 데이터 생성 (메인 데이터 + EcountSale/Purchase 데이터)
        """
        excel_data = {
            'main_data': [],
            'ecount_data': []
        }
        
        # 메인 데이터 생성
        for order in orders:
            if form_name == FormNameType.OKMART_ERP_SALE_OK:
                # OKMart 방식: okmart_sheet.txt 기준
                row_data = self._create_okmart_excel_row(order)
            else:
                # IYES 방식: iyes_sheet.txt 기준
                row_data = self._create_iyes_excel_row(order)
            
            excel_data['main_data'].append(row_data)
        
        # EcountSale/Purchase 데이터 생성
        if ecount_erp_data:
            if 'sale' in form_name.value:
                # 판매 데이터: 1_판매입력.txt 기준
                ecount_sheet_data = self._create_ecount_sale_sheet_data(ecount_erp_data)
            elif 'purchase' in form_name.value:
                # 구매 데이터: 구매입력.txt 기준
                ecount_sheet_data = self._create_ecount_purchase_sheet_data(ecount_erp_data)
            else:
                ecount_sheet_data = []
            
            excel_data['ecount_data'] = ecount_sheet_data
        
        return excel_data
    
    def _create_okmart_excel_row(self, order: OKMartProcessedData) -> Dict[str, Any]:
        """
        OKMart Excel 행 데이터 생성 (okmart_sheet.txt 기준)
        """
        return {
            '순번': order.seq,  # A
            '사이트': order.fld_dsp,  # B
            '사이트코드': order.site_code,  # C
            '창고': order.warehouse,  # D
            '수취인명': order.receive_name,  # E
            '금액': order.etc_cost,  # F
            '주문번호': order.order_id,  # G
            '제품명': order.item_name_only_name,  # H
            'ERP품목명': order.erp_product_name,  # I
            '나눈수량': order.devided_cnt,  # J
            '실수량': order.real_cnt,  # K
            '단가': order.price,  # L
            '공급가액': order.supply_amt,  # M
            '부가세': order.vat_amt,  # N
            '적요': order.remarks,  # O
            '전화번호1': order.receive_cel,  # P
            '전화번호2': order.receive_tel,  # Q
            '수취인주소': order.receive_addr,  # R
            '우편번호': order.receive_zipcode,  # S
            '선/착불': order.delivery_method_str,  # T
            '상품번호': order.mall_product_id,  # U
            '상품번호_SKU': order.mall_product_id_sku,  # V
            '배송메세지': order.delv_msg,  # W
            '정산예정금액': int(order.expected_payout) if order.expected_payout is not None else None,  # X
            '서비스이용료': int(order.service_fee) if order.service_fee is not None else None,  # Y
            '장바구니번호': order.mall_order_id,  # Z
            '운송장번호': order.invoice_no,  # AA
            '판매자관리코드': order.order_etc_7,  # AB
            'SKU번호': order.sku_no,  # AC
        }
    
    def _create_iyes_excel_row(self, order: IYESProcessedData) -> Dict[str, Any]:
        """
        IYES Excel 행 데이터 생성 (iyes_sheet.txt 기준)
        """
        return {
            '순번': order.seq,  # A
            '사이트': order.fld_dsp,  # B
            '사이트코드': order.site_code,  # C
            '사이트-오케이마트': order.site_okmart,  # D
            '사이트-아이예스': order.site_iyes,  # E
            '창고': order.warehouse,  # F
            '창고조정': order.warehouse_adjustment,  # G
            '수취인명': order.receive_name,  # H
            '금액': order.etc_cost,  # I
            '주문번호': order.order_id,  # J
            '제품명': order.item_name_only_name,  # K
            'ERP품목명': order.erp_product_name,  # L
            '나눈수량': order.devided_cnt,  # M
            '실수량': order.real_cnt,  # N
            '단가': order.price,  # O
            '공급가액': order.supply_amt,  # P
            '부가세': order.vat_amt,  # Q
            '구매단가': order.purchase_price,  # R
            '구매공급가': order.purchase_supply_amt,  # S
            '구매부가세': order.purchase_vat_amt,  # T
            '적요': order.remarks,  # U
            '전화번호1': order.receive_cel,  # V
            '전화번호2': order.receive_tel,  # W
            '수취인주소': order.receive_addr,  # X
            '우편번호': order.receive_zipcode,  # Y
            '선/착불': order.delivery_method_str,  # Z
            '상품번호': order.mall_product_id,  # AA
            '상품번호_SKU': order.mall_product_id_sku,  # AB
            '배송메세지': order.delv_msg,  # AC
            '정산예정금액': int(order.expected_payout) if order.expected_payout is not None else None,  # AD
            '서비스이용료': int(order.service_fee) if order.service_fee is not None else None,  # AE
            '장바구니번호': order.mall_order_id,  # AF
            '운송장번호': order.invoice_no,  # AG
            '판매자관리코드': order.order_etc_7,  # AH
            'SKU번호': order.sku_no,  # AI
        }
    
    def _create_ecount_sale_data(
        self, 
        orders: List, 
        batch_id: str, 
        form_name: FormNameType
    ) -> List[EcountSaleData]:
        """
        EcountSale 데이터 생성 (1_판매입력.txt 기준)
        """
        ecount_data = []
        
        for order in orders:
            # 1_판매입력.txt 기준으로 매핑
            ecount_sale = EcountSaleData(
                io_date=None,
                upload_ser_no=order.seq,
                cust=order.site_code,
                cust_des=None,
                emp_cd=None,
                wh_cd=order.warehouse if hasattr(order, 'warehouse') else None,
                io_type=None,
                exchange_type=None,
                exchange_rate=None,
                u_memo1=None,
                u_memo2=None,
                u_memo3=order.receive_cel,
                u_txt1=order.receive_addr,
                u_memo4=None,
                u_memo5=None,
                prod_cd=order.erp_product_name,
                prod_des=order.erp_product_name,
                qty=Decimal(str(order.real_cnt)) if order.real_cnt else Decimal('0'),
                price=order.price,
                exchange_cost=None,
                supply_amt=order.supply_amt,
                vat_amt=order.vat_amt,
                remarks=order.remarks,
                p_remarks2=order.delv_msg,
                p_remarks1=order.invoice_no,
                p_remarks3=order.mall_product_id_sku,
                size_des=order.order_id,
                p_amt1=int(order.expected_payout) if order.expected_payout is not None else None,
                p_amt2=int(order.service_fee) if order.service_fee is not None else None,
                batch_id=batch_id,
                template_code=form_name.value,
                work_status="ERP 업로드 전"
            )
            
            
            ecount_data.append(ecount_sale)
        
        return ecount_data
    
    def _create_ecount_purchase_data(
        self, 
        orders: List, 
        batch_id: str, 
        form_name: FormNameType
    ) -> List[EcountPurchaseData]:
        """
        EcountPurchase 데이터 생성 (구매입력.txt 기준)
        """
        ecount_data = []
        
        for order in orders:
            # 구매입력.txt 기준으로 매핑
            ecount_purchase = EcountPurchaseData(
                io_date=None,
                upload_ser_no=order.seq,
                cust=order.site_code,
                cust_des=None,
                emp_cd=None,
                wh_cd=order.warehouse if hasattr(order, 'warehouse') else None,
                io_type=None,
                exchange_type=None,
                exchange_rate=None,
                u_memo1=None,
                u_memo2=None,
                u_memo3=order.receive_cel,
                u_txt1=order.receive_addr,
                prod_cd=order.erp_product_name,
                prod_des=order.erp_product_name,
                qty=Decimal(str(order.real_cnt)) if order.real_cnt else Decimal('0'),
                price=order.purchase_price if hasattr(order, 'purchase_price') else order.price,
                exchange_cost=None,
                supply_amt=order.purchase_supply_amt if hasattr(order, 'purchase_supply_amt') else order.supply_amt,
                vat_amt=order.purchase_vat_amt if hasattr(order, 'purchase_vat_amt') else order.vat_amt,
                remarks=order.remarks,
                batch_id=batch_id,
                template_code=form_name.value,
                work_status="ERP 업로드 전"
            )
            
            ecount_data.append(ecount_purchase)
        
        return ecount_data
    
    def _create_ecount_sale_sheet_data(self, ecount_erp_data: List[EcountSaleData]) -> List[Dict[str, Any]]:
        """
        EcountSale 시트 데이터 생성 (1_판매입력.txt 기준)
        """
        sheet_data = []
        
        for ecount_data in ecount_erp_data:
            row_data = {
                '일자': None,  # A
                '순번': ecount_data.upload_ser_no,  # B
                '거래처코드': ecount_data.cust,  # C
                '거래처명': ecount_data.cust_des,  # D
                '담당자': ecount_data.emp_cd,  # E
                '출하창고': ecount_data.wh_cd,  # F
                '거래유형': ecount_data.io_type,  # G
                '통화': ecount_data.exchange_type,  # H
                '환율': ecount_data.exchange_rate,  # I
                'E-MAIL': ecount_data.u_memo1,  # J
                'FAX': ecount_data.u_memo2,  # K
                '연락처': ecount_data.u_memo3,  # L
                '주소': ecount_data.u_txt1,  # M
                '매장판매 결제구분(입금/현금/카드)': ecount_data.u_memo4,  # N
                '매장판매 거래구분(매장판매/매장구매)': ecount_data.u_memo5,  # O
                '품목코드': ecount_data.prod_cd,  # P
                '품목명': ecount_data.prod_des,  # Q
                '수량': ecount_data.qty,  # R
                '단가': ecount_data.price,  # S
                '외화금액': ecount_data.exchange_cost,  # T
                '공급가액': ecount_data.supply_amt,  # U
                '부가세': ecount_data.vat_amt,  #V
                '고객정보(이름/주문번호/연락처/주소/관리코드/장바구니번호)': ecount_data.remarks,  # W
                '배송메시지': ecount_data.p_remarks2,  # X
                '송장번호': ecount_data.p_remarks1,  # Y
                '상품번호': ecount_data.p_remarks3,  # Z
                '주문번호': ecount_data.size_des,  # AA
                '정산예정금액': int(ecount_data.p_amt1) if ecount_data.p_amt1 is not None else None,  # AB
                '서비스이용료': int(ecount_data.p_amt2) if ecount_data.p_amt2 is not None else None,  # AC
                '운임비타입': ecount_data.item_cd,  # AD
                '생산전표생성': None,  # 생산전표생성
            }
            sheet_data.append(row_data)
        
        return sheet_data
    
    def _create_ecount_purchase_sheet_data(self, ecount_erp_data: List[EcountPurchaseData]) -> List[Dict[str, Any]]:
        """
        EcountPurchase 시트 데이터 생성 (구매입력.txt 기준)
        """
        sheet_data = []
        
        for ecount_data in ecount_erp_data:
            row_data = {
                '일자': None,  # A
                '순번': ecount_data.upload_ser_no,  # B
                '거래처코드': ecount_data.cust,  # C
                '거래처명': ecount_data.cust_des,  # D
                '담당자': ecount_data.emp_cd,  # E
                '입고창고': ecount_data.wh_cd,  # F
                '거래유형': ecount_data.io_type,  # G
                '통화': ecount_data.exchange_type,  # H
                '환율': ecount_data.exchange_rate,  # I
                'E-MAIL': ecount_data.u_memo1,  # J
                'FAX': ecount_data.u_memo2,  # K
                '연락처': ecount_data.u_memo3,  # L
                '주소': ecount_data.u_txt1,  # M
                '품목코드': ecount_data.prod_cd,  # N
                '품목명': ecount_data.prod_des,  # O
                '규격': None,  # P
                '수량': ecount_data.qty,  # Q
                '단가': ecount_data.price,  # R
                '외화금액': ecount_data.exchange_cost,  # S
                '공급가액': ecount_data.supply_amt,  # T
                '부가세': ecount_data.vat_amt,  # U
                '적요': ecount_data.remarks,  # V
            }
            sheet_data.append(row_data)
        
        return sheet_data
