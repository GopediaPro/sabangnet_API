import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class ProductTextProcessor:
    """
    제품명 텍스트 처리 유틸리티 클래스
    "+" 구분자로 분리된 제품명을 처리하고 중복 제품을 통합하는 기능 제공
    """
    
    def __init__(self):
        self.excluded_keywords = ['[사은품]', '[증정품]', '[무료]']
    
    def process_product_text(
        self, 
        product_text: str, 
        excluded_keywords: Optional[List[str]] = None
    ) -> str:
        """
        제품명 텍스트를 처리하여 중복 제품을 통합하고 수량을 계산합니다.
        
        Args:
            product_text (str): 처리할 제품명 텍스트 (예: "OMS-703(BL) + OMS-703(BL)")
            excluded_keywords (Optional[List[str]]): 제외할 키워드 리스트 (기본값: ['[사은품]', '[증정품]', '[무료]'])
        
        Returns:
            str: 처리된 제품명 (예: "OMS-703(BL) 2개")
        
        Examples:
            >>> processor = ProductTextProcessor()
            >>> processor.process_product_text("OMS-703(BL) + OMS-703(BL)")
            "OMS-703(BL) 2개"
            >>> processor.process_product_text("OSA-146 + OSA-D717 + OSA-146")
            "OSA-146 2개 + OSA-D717"
        """
        if not product_text or not isinstance(product_text, str):
            logger.warning(f"유효하지 않은 product_text: {product_text}")
            return ""
        
        # 제외 키워드 설정
        if excluded_keywords is not None:
            self.excluded_keywords = excluded_keywords
        
        logger.info(f"[제품명처리] 원본 텍스트: {product_text}")
        
        # 1. "+" 구분자로 분리
        parts = self._split_by_plus(product_text)
        if not parts:
            return product_text
        
        # 2. 제외 키워드가 포함된 항목 필터링
        filtered_parts = self._filter_excluded_items(parts)
        if not filtered_parts:
            logger.info(f"[제품명처리] 모든 항목이 제외됨: {product_text}")
            return ""
        
        # 3. 각 항목에서 제품명과 수량 추출
        extracted_items = self._extract_product_and_quantity(filtered_parts)
        
        # 4. 중복 제품 통합 및 수량 계산
        merged_items = self._merge_duplicate_products(extracted_items)
        
        # 5. 최종 결과 문자열 생성
        result = self._build_final_result(merged_items)
        
        logger.info(f"[제품명처리] 처리 결과: {result}")
        return result
    
    def _split_by_plus(self, text: str) -> List[str]:
        """'+' 구분자로 텍스트를 분리합니다."""
        if '+' not in text:
            return [text.strip()]
        
        parts = [part.strip() for part in text.split('+')]
        logger.debug(f"[분리] 분리된 부분들: {parts}")
        return parts
    
    def _filter_excluded_items(self, parts: List[str]) -> List[str]:
        """제외 키워드가 포함된 항목들을 필터링합니다."""
        filtered = []
        for part in parts:
            if not any(keyword in part for keyword in self.excluded_keywords):
                filtered.append(part)
            else:
                logger.info(f"[필터링] 제외된 항목: {part}")
        
        logger.debug(f"[필터링] 필터링 후: {filtered}")
        return filtered
    
    def _extract_product_and_quantity(self, parts: List[str]) -> List[Dict[str, any]]:
        """각 항목에서 제품명과 수량을 추출합니다."""
        extracted_items = []
        
        for part in parts:
            # 기존 수량 패턴 확인 (예: "제품명 2개")
            qty_match = re.search(r'(.+?)\s*(\d+)개\s*$', part.strip())
            
            if qty_match:
                product_name = qty_match.group(1).strip()
                quantity = int(qty_match.group(2))
            else:
                # 수량이 명시되지 않은 경우 기본값 1
                product_name = part.strip()
                quantity = 1
            
            extracted_items.append({
                'product_name': product_name,
                'quantity': quantity,
                'original_text': part
            })
            
            logger.debug(f"[추출] 제품명: '{product_name}', 수량: {quantity}")
        
        return extracted_items
    
    def _merge_duplicate_products(self, items: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """중복 제품을 통합하고 수량을 합산합니다."""
        # 제품명을 키로 하는 딕셔너리로 그룹화
        product_groups = defaultdict(list)
        
        for item in items:
            product_name = item['product_name']
            product_groups[product_name].append(item)
        
        merged_items = []
        
        for product_name, group_items in product_groups.items():
            # 수량 합산
            total_quantity = sum(item['quantity'] for item in group_items)
            
            merged_item = {
                'product_name': product_name,
                'quantity': total_quantity,
                'original_texts': [item['original_text'] for item in group_items]
            }
            
            merged_items.append(merged_item)
            logger.debug(f"[통합] {product_name}: {len(group_items)}개 항목 → 수량 {total_quantity}")
        
        return merged_items
    
    def _build_final_result(self, merged_items: List[Dict[str, any]]) -> str:
        """통합된 항목들로 최종 결과 문자열을 생성합니다."""
        if not merged_items:
            return ""
        
        result_parts = []
        
        for item in merged_items:
            product_name = item['product_name']
            quantity = item['quantity']
            
            if quantity == 1:
                # 수량이 1인 경우 "개" 표시 생략
                result_parts.append(product_name)
            else:
                # 수량이 1보다 큰 경우 "개" 표시 포함
                result_parts.append(f"{product_name} {quantity}개")
        
        result = " + ".join(result_parts)
        logger.debug(f"[결과생성] 최종 결과: {result}")
        return result
    
    def get_quantity_count(self, product_text: str) -> int:
        """
        제품명에서 총 수량을 계산합니다.
        
        Args:
            product_text (str): 처리할 제품명 텍스트
        
        Returns:
            int: 총 수량
        """
        if not product_text:
            return 0
        
        parts = self._split_by_plus(product_text)
        filtered_parts = self._filter_excluded_items(parts)
        extracted_items = self._extract_product_and_quantity(filtered_parts)
        merged_items = self._merge_duplicate_products(extracted_items)
        
        total_quantity = sum(item['quantity'] for item in merged_items)
        logger.debug(f"[수량계산] 총 수량: {total_quantity}")
        return total_quantity
    
    def has_multiple_products(self, product_text: str) -> bool:
        """
        제품명에 여러 제품이 포함되어 있는지 확인합니다.
        
        Args:
            product_text (str): 확인할 제품명 텍스트
        
        Returns:
            bool: 여러 제품이 포함되어 있으면 True
        """
        if not product_text:
            return False
        
        parts = self._split_by_plus(product_text)
        filtered_parts = self._filter_excluded_items(parts)
        
        return len(filtered_parts) > 1


# 편의 함수들
def process_product_text(
    product_text: str, 
    excluded_keywords: Optional[List[str]] = None
) -> str:
    """
    제품명 텍스트를 처리하는 편의 함수
    
    Args:
        product_text (str): 처리할 제품명 텍스트
        excluded_keywords (Optional[List[str]]): 제외할 키워드 리스트
    
    Returns:
        str: 처리된 제품명
    """
    processor = ProductTextProcessor()
    return processor.process_product_text(product_text, excluded_keywords)


def get_product_quantity_count(product_text: str) -> int:
    """
    제품명에서 총 수량을 계산하는 편의 함수
    
    Args:
        product_text (str): 처리할 제품명 텍스트
    
    Returns:
        int: 총 수량
    """
    processor = ProductTextProcessor()
    return processor.get_quantity_count(product_text)


def has_multiple_products(product_text: str) -> bool:
    """
    제품명에 여러 제품이 포함되어 있는지 확인하는 편의 함수
    
    Args:
        product_text (str): 확인할 제품명 텍스트
    
    Returns:
        bool: 여러 제품이 포함되어 있으면 True
    """
    processor = ProductTextProcessor()
    return processor.has_multiple_products(product_text)
