"""
ProductTextProcessor 단위 테스트
"""

import pytest
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from utils.product_text_processor import (
    ProductTextProcessor, 
    process_product_text, 
    get_product_quantity_count, 
    has_multiple_products
)


class TestProductTextProcessor:
    """ProductTextProcessor 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.processor = ProductTextProcessor()
    
    def test_basic_duplicate_merge(self):
        """기본 중복 제품 통합 테스트"""
        # 예시 1: OMS-703(BL) + OMS-703(BL) >> OMS-703(BL) 2개
        result = self.processor.process_product_text("OMS-703(BL) + OMS-703(BL)")
        assert result == "OMS-703(BL) 2개"
    
    def test_mixed_duplicate_merge(self):
        """혼합 제품 중 일부 중복 통합 테스트"""
        # 예시 2: OSA-146 + OSA-D717 + OSA-146 >> OSA-146 2개 + OSA-D717
        result = self.processor.process_product_text("OSA-146 + OSA-D717 + OSA-146")
        assert result == "OSA-146 2개 + OSA-D717"
    
    def test_quantity_explicit_products(self):
        """수량이 명시된 제품들 통합 테스트"""
        result = self.processor.process_product_text("제품A 3개 + 제품B 2개 + 제품A 1개")
        assert result == "제품A 4개 + 제품B 2개"
    
    def test_single_product(self):
        """단일 제품 테스트"""
        result = self.processor.process_product_text("단일제품")
        assert result == "단일제품"
    
    def test_no_duplicates(self):
        """중복 없는 다중 제품 테스트"""
        result = self.processor.process_product_text("제품A + 제품B + 제품C")
        assert result == "제품A + 제품B + 제품C"
    
    def test_excluded_keywords_default(self):
        """기본 제외 키워드 테스트"""
        # 사은품 제외
        result = self.processor.process_product_text("제품A + [사은품]제품B + 제품C")
        assert result == "제품A + 제품C"
        
        # 증정품 제외
        result = self.processor.process_product_text("제품A + [증정품]제품B + 제품C")
        assert result == "제품A + 제품C"
        
        # 무료 제품 제외
        result = self.processor.process_product_text("제품A + [무료]제품B + 제품C")
        assert result == "제품A + 제품C"
    
    def test_excluded_keywords_custom(self):
        """사용자 정의 제외 키워드 테스트"""
        custom_keywords = ['[할인]', '[특가]']
        result = self.processor.process_product_text(
            "제품A + [할인]제품B + 제품C", 
            excluded_keywords=custom_keywords
        )
        assert result == "제품A + 제품C"
    
    def test_all_items_excluded(self):
        """모든 항목이 제외되는 경우 테스트"""
        result = self.processor.process_product_text("[사은품]제품A + [사은품]제품B")
        assert result == ""
    
    def test_empty_input(self):
        """빈 입력 테스트"""
        result = self.processor.process_product_text("")
        assert result == ""
        
        result = self.processor.process_product_text(None)
        assert result == ""
    
    def test_invalid_input(self):
        """유효하지 않은 입력 테스트"""
        result = self.processor.process_product_text(123)
        assert result == ""
    
    def test_quantity_calculation(self):
        """수량 계산 테스트"""
        # 기본 수량 계산
        quantity = self.processor.get_quantity_count("제품A 2개 + 제품B 3개 + 제품A 1개")
        assert quantity == 6
        
        # 기본 수량 1인 경우
        quantity = self.processor.get_quantity_count("제품A + 제품B + 제품C")
        assert quantity == 3
        
        # 단일 제품 수량
        quantity = self.processor.get_quantity_count("제품A 5개")
        assert quantity == 5
    
    def test_multiple_products_detection(self):
        """다중 제품 감지 테스트"""
        # 다중 제품
        assert self.processor.has_multiple_products("제품A + 제품B") == True
        
        # 단일 제품
        assert self.processor.has_multiple_products("단일제품") == False
        
        # 제외 후 단일 제품
        assert self.processor.has_multiple_products("제품A + [사은품]제품B") == False
        
        # 빈 입력
        assert self.processor.has_multiple_products("") == False


class TestConvenienceFunctions:
    """편의 함수들 테스트"""
    
    def test_process_product_text_function(self):
        """process_product_text 편의 함수 테스트"""
        result = process_product_text("제품A + 제품A")
        assert result == "제품A 2개"
    
    def test_get_product_quantity_count_function(self):
        """get_product_quantity_count 편의 함수 테스트"""
        quantity = get_product_quantity_count("제품A 2개 + 제품B 3개")
        assert quantity == 5
    
    def test_has_multiple_products_function(self):
        """has_multiple_products 편의 함수 테스트"""
        assert has_multiple_products("제품A + 제품B") == True
        assert has_multiple_products("단일제품") == False


class TestEdgeCases:
    """엣지 케이스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.processor = ProductTextProcessor()
    
    def test_whitespace_handling(self):
        """공백 처리 테스트"""
        result = self.processor.process_product_text("  제품A  +  제품A  ")
        assert result == "제품A 2개"
    
    def test_mixed_quantity_formats(self):
        """혼합된 수량 형식 테스트"""
        result = self.processor.process_product_text("제품A 2개 + 제품B + 제품A 3개")
        assert result == "제품A 5개 + 제품B"
    
    def test_special_characters(self):
        """특수 문자 포함 제품명 테스트"""
        result = self.processor.process_product_text("제품(A) + 제품(B) + 제품(A)")
        assert result == "제품(A) 2개 + 제품(B)"
    
    def test_korean_and_english_mixed(self):
        """한글과 영문 혼합 제품명 테스트"""
        result = self.processor.process_product_text("상품A + Product B + 상품A")
        assert result == "상품A 2개 + Product B"
    
    def test_numbers_in_product_names(self):
        """제품명에 숫자가 포함된 경우 테스트"""
        result = self.processor.process_product_text("제품123 + 제품456 + 제품123")
        assert result == "제품123 2개 + 제품456"


class TestPerformance:
    """성능 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.processor = ProductTextProcessor()
    
    def test_large_input(self):
        """큰 입력 데이터 테스트"""
        # 많은 제품이 포함된 입력
        large_input = " + ".join([f"제품{i}" for i in range(100)])
        result = self.processor.process_product_text(large_input)
        
        # 결과가 올바르게 생성되는지 확인
        assert result is not None
        assert len(result) > 0
    
    def test_repeated_processing(self):
        """반복 처리 테스트"""
        input_text = "제품A + 제품B + 제품A"
        
        # 여러 번 처리해도 결과가 일관되는지 확인
        results = []
        for _ in range(10):
            result = self.processor.process_product_text(input_text)
            results.append(result)
        
        # 모든 결과가 동일한지 확인
        assert all(result == results[0] for result in results)


# 파라미터화된 테스트
class TestParameterized:
    """파라미터화된 테스트"""
    
    @pytest.mark.parametrize("input_text,expected", [
        ("제품A + 제품A", "제품A 2개"),
        ("제품A + 제품B + 제품A", "제품A 2개 + 제품B"),
        ("제품A 2개 + 제품A 3개", "제품A 5개"),
        ("제품A + 제품B + 제품C", "제품A + 제품B + 제품C"),
    ])
    def test_merge_scenarios(self, input_text, expected):
        """다양한 통합 시나리오 테스트"""
        processor = ProductTextProcessor()
        result = processor.process_product_text(input_text)
        assert result == expected
    
    @pytest.mark.parametrize("input_text,expected_quantity", [
        ("제품A + 제품B", 2),
        ("제품A 2개 + 제품B 3개", 5),
        ("제품A + 제품A", 2),
        ("제품A 5개", 5),
    ])
    def test_quantity_calculations(self, input_text, expected_quantity):
        """다양한 수량 계산 테스트"""
        quantity = get_product_quantity_count(input_text)
        assert quantity == expected_quantity
