import unicodedata
from typing import Optional


def normalize_unicode(text: Optional[str], form: str = 'NFC') -> Optional[str]:
    """
    유니코드 정규화를 수행하는 유틸리티 함수
    
    Args:
        text: 정규화할 텍스트 (None일 수 있음)
        form: 정규화 형태 ('NFC', 'NFD', 'NFKC', 'NFKD')
        
    Returns:
        정규화된 텍스트 또는 None
    """
    if text is None:
        return None
    return unicodedata.normalize(form, text)


def normalize_for_comparison(text: Optional[str]) -> Optional[str]:
    """
    비교를 위한 강화된 유니코드 정규화 함수
    - NFC 정규화 후 공백 정리
    
    Args:
        text: 정규화할 텍스트
        
    Returns:
        정규화된 텍스트 또는 None
    """
    if text is None:
        return None
    
    # NFC 정규화
    normalized = unicodedata.normalize('NFC', text)
    
    # 공백 정리 (앞뒤 공백 제거, 중복 공백 제거)
    cleaned = ' '.join(normalized.split())
    
    return cleaned


def compare_normalized_strings(text1: Optional[str], text2: Optional[str]) -> bool:
    """
    두 문자열을 정규화한 후 비교하는 유틸리티 함수
    
    Args:
        text1: 첫 번째 문자열
        text2: 두 번째 문자열
        
    Returns:
        정규화 후 두 문자열이 같으면 True, 다르면 False
    """
    normalized_text1 = normalize_for_comparison(text1)
    normalized_text2 = normalize_for_comparison(text2)
    return normalized_text1 == normalized_text2


def find_matching_item(items: list, **criteria) -> Optional[object]:
    """
    리스트에서 정규화된 문자열 비교로 매칭되는 아이템을 찾는 유틸리티 함수
    
    Args:
        items: 검색할 아이템 리스트
        **criteria: 검색 조건 (키: 값 형태)
        
    Returns:
        매칭되는 첫 번째 아이템 또는 None
    """
    for item in items:
        match = True
        for key, expected_value in criteria.items():
            if hasattr(item, key):
                actual_value = getattr(item, key)
                
                # 문자열인 경우에만 유니코드 정규화 비교
                if isinstance(expected_value, str) and isinstance(actual_value, str):
                    if not compare_normalized_strings(actual_value, expected_value):
                        match = False
                        break
                else:
                    # 문자열이 아닌 경우 (boolean, int 등) 직접 비교
                    if actual_value != expected_value:
                        match = False
                        break
            else:
                match = False
                break
        if match:
            return item
    return None 