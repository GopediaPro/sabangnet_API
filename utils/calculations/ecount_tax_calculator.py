"""
이카운트 ERP 부가세 계산 유틸리티
부가세 포함 금액을 부가세 제외 금액으로 변환하는 계산 로직
"""

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, Tuple
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class EcountTaxCalculator:
    """이카운트 ERP 부가세 계산기"""
    
    VAT_RATE = Decimal('0.1')  # 10% 부가세율
    VAT_DIVISOR = Decimal('1.1')  # 1 + VAT_RATE
    
    @classmethod
    def calculate_tax_amounts(
        cls, 
        original_price: float, 
        quantity: int = 1,
        is_bulk_purchase: bool = False
    ) -> Dict[str, float]:
        """
        부가세 포함 금액을 부가세 제외 금액으로 변환합니다.
        
        Args:
            original_price: 원단가 (부가세 포함)
            quantity: 수량
            is_bulk_purchase: 복수구매 여부 (A+B, A+B+C 형태)
            
        Returns:
            Dict[str, float]: 계산된 금액 정보
                - unit_price: 단가 (부가세 제외)
                - supply_amt: 공급가액
                - vat_amt: 부가세
                - total_amount: 총액 (부가세 포함)
        """
        try:
            # Decimal로 변환하여 정확한 계산
            original_decimal = Decimal(str(original_price))
            qty_decimal = Decimal(str(quantity))
            
            # 복수구매 케이스 처리
            if is_bulk_purchase:
                # 총액을 수량으로 나눈 금액을 단가 기준으로 사용
                unit_price_with_vat = original_decimal / qty_decimal
            else:
                unit_price_with_vat = original_decimal
            
            # 단가 계산: ROUND(원단가 / 1.1, 0)
            unit_price = cls._round_decimal(unit_price_with_vat / cls.VAT_DIVISOR)
            
            # 공급가액 계산: ROUND((원단가 × 수량) / 1.1, 0)
            total_with_vat = original_decimal
            supply_amt = cls._round_decimal(total_with_vat / cls.VAT_DIVISOR)
            
            # 부가세 계산: ROUND(원단가 × 수량 - 공급가, 0)
            vat_amt = cls._round_decimal(total_with_vat - supply_amt)
            
            result = {
                'unit_price': float(unit_price),
                'supply_amt': float(supply_amt),
                'vat_amt': float(vat_amt),
                'total_amount': float(total_with_vat)
            }
            
            logger.debug(
                f"부가세 계산 완료: 원단가={original_price}, 수량={quantity}, "
                f"단가={result['unit_price']}, 공급가={result['supply_amt']}, "
                f"부가세={result['vat_amt']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"부가세 계산 중 오류 발생: {e}")
            # 오류 시 원본 값 반환
            return {
                'unit_price': original_price,
                'supply_amt': original_price * quantity,
                'vat_amt': 0.0,
                'total_amount': original_price * quantity
            }
    
    @classmethod
    def _round_decimal(cls, value: Decimal) -> Decimal:
        """Decimal 값을 정수로 반올림합니다."""
        return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    @classmethod
    def detect_bulk_purchase(cls, product_name: str) -> bool:
        """
        상품명에서 복수구매 패턴을 감지합니다.
        
        Args:
            product_name: 상품명
            
        Returns:
            bool: 복수구매 여부
        """
        if not product_name:
            return False
        
        # 복수구매 패턴 감지
        bulk_patterns = [
            r'\d+개\s*세트',  # "2개 세트", "3개 세트"
            r'\([A-Z]+\)\s*\+',  # "(A) +", "(B) +"
            r'[A-Z]\s*\+\s*[A-Z]',  # "A + B", "A+B"
            r'[A-Z]\s*\+\s*[A-Z]\s*\+\s*[A-Z]',  # "A + B + C"
            r'복수',  # "복수" 키워드
            r'묶음',  # "묶음" 키워드
        ]
        
        for pattern in bulk_patterns:
            if re.search(pattern, product_name, re.IGNORECASE):
                logger.debug(f"복수구매 패턴 감지: {product_name} -> {pattern}")
                return True
        
        return False
    
    @classmethod
    def extract_quantity_from_product_name(cls, product_name: str) -> Optional[int]:
        """
        상품명에서 수량 정보를 추출합니다.
        
        Args:
            product_name: 상품명
            
        Returns:
            Optional[int]: 추출된 수량, 없으면 None
        """
        if not product_name:
            return None
        
        # 수량 패턴 추출
        quantity_patterns = [
            r'(\d+)개\s*세트',  # "2개 세트"
            r'(\d+)개\s*묶음',  # "3개 묶음"
            r'(\d+)개\s*패키지',  # "5개 패키지"
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, product_name, re.IGNORECASE)
            if match:
                quantity = int(match.group(1))
                logger.debug(f"수량 추출: {product_name} -> {quantity}개")
                return quantity
        
        return None
    
    @classmethod
    def calculate_for_ecount_sale_dto(
        cls, 
        sale_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        EcountSaleDto 데이터에 부가세 계산을 적용합니다.
        
        Args:
            sale_data: 판매 데이터 딕셔너리
            
        Returns:
            Dict[str, Any]: 계산이 적용된 판매 데이터
        """
        try:
            # 기존 값들 가져오기
            original_price = sale_data.get('price', 0)
            quantity = sale_data.get('qty', 1)
            product_name = sale_data.get('prod_des', '')
            
            # 수량이 없거나 0이면 1로 설정
            if not quantity or quantity <= 0:
                quantity = 1
            
            # 복수구매 여부 확인
            is_bulk_purchase = cls.detect_bulk_purchase(product_name)
            
            # 상품명에서 수량 추출 시도
            extracted_quantity = cls.extract_quantity_from_product_name(product_name)
            if extracted_quantity and extracted_quantity > 1:
                quantity = extracted_quantity
                is_bulk_purchase = True
            
            # 부가세 계산
            tax_calculation = cls.calculate_tax_amounts(
                original_price=original_price,
                quantity=quantity,
                is_bulk_purchase=is_bulk_purchase
            )
            
            # 계산 결과를 sale_data에 적용
            updated_sale_data = sale_data.copy()
            updated_sale_data.update({
                'price': tax_calculation['unit_price'],
                'supply_amt': tax_calculation['supply_amt'],
                'vat_amt': tax_calculation['vat_amt'],
                'qty': quantity  # 수량 업데이트
            })
            
            logger.info(
                f"부가세 계산 적용 완료: {product_name} - "
                f"원단가: {original_price} -> 단가: {tax_calculation['unit_price']}, "
                f"공급가: {tax_calculation['supply_amt']}, "
                f"부가세: {tax_calculation['vat_amt']}"
            )
            
            return updated_sale_data
            
        except Exception as e:
            logger.error(f"EcountSaleDto 부가세 계산 중 오류: {e}")
            return sale_data  # 오류 시 원본 데이터 반환

