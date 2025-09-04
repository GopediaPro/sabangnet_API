def sum_slash_separated_values(value: str) -> str:
    """
    '/' 구분자가 있는 문자열의 숫자들을 합산하는 메서드
    
    Args:
        value (str): 합산할 문자열 (예: "1/1", "2/1", "1/2/1" => 2,3,4)
        
    Returns:
        str: 합산된 결과 문자열. '/' 구분자가 없으면 원래 값 반환
    """
    if not value or '/' not in value:
        return value
    
    try:
        # '/' 구분자로 분리하여 숫자들 추출
        numbers = value.split('/')
        
        # 각 부분을 정수로 변환하여 합산
        total = sum(int(num.strip()) for num in numbers if num.strip().isdigit())
        
        return str(total)
    except (ValueError, TypeError):
        # 변환 실패 시 원래 값 반환
        return value


def process_slash_separated_columns(ws, columns: list, start_row: int = 2) -> None:
    """
    워크시트에서 지정된 열들의 '/' 구분자 합산을 한번에 처리하는 메서드
    
    Args:
        ws: 워크시트 객체
        columns (list): 처리할 열 리스트 (예: ['G', 'H', 'I'] 또는 ['G'])
        start_row (int): 처리 시작 행 (기본값: 2, 헤더 제외)
    """
    max_row = ws.max_row
    
    for col in columns:
        for row in range(start_row, max_row + 1):
            cell = ws[f'{col}{row}']
            cell_value = cell.value
            if cell.value:
                # int, float 타입 문자열로 변환
                if isinstance(cell_value, (int, float)):
                    cell_value = str(int(cell.value))
                # '/' 구분자 합산 처리
                processed_value = sum_slash_separated_values(cell_value)
                cell.value = processed_value
