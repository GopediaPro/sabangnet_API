from typing import Any


async def compare_sample_data_with_expected(
    self,
    sample_dict: list[dict[str, Any]],
    expect_dict_okclbb: list[dict[str, Any]],
    expect_dict_iy: list[dict[str, Any]]
):
    """
    프로세스 거쳐 실제 나온 데이터와 예상 데이터 비교

    1. 순번 잘 들어가있는지
    2. 정렬 잘 됐는지 (순서 2, 3, 5, 6, 4)
    3. 금액 계산 잘 됐는지
    4. 제품명 N개 같이 개수 제거 됐는지
    5. 제품명 숫자만 있는 경우 하늘색으로 배경 있는지 -> dataframe 으로 들어오기 때문에 디자인 확인 불가
    6. 선/착불 신용인 경우 아무 것도 없고 착불인 경우 빨간색으로 금액 표시 -> dataframe 으로 들어오기 때문에 디자인 확인 불가
    7. 시트 분리 여부 (ok, cl, bb, iy)
    """
    
    # 필드 비교 대상
    comparison_fields = [
        "순번",
        "사이트",
        "수취인명",
        "금액",
        "주문번호",
        "제품명",
        "선/착불",
    ]

    # 1. 순번 비교
    

    # 2. 정렬 비교

    # 3. 금액 비교
    [2, 3, 5, 6, 4]
    
    for i, saved_order in enumerate(saved_orders):
        expected_row = expected_data[i]
        
        for field in comparison_fields:
            saved_value = getattr(saved_order, field, None)
            expected_value = expected_row.get(field)
            
            # None 값과 빈 문자열 처리
            if saved_value is None:
                saved_value = ""
            if pd.isna(expected_value):
                expected_value = ""
            
            assert str(saved_value) == str(expected_value), \
                f"행 {i+1}의 {field} 필드가 다릅니다. 저장값: {saved_value}, 예상값: {expected_value}"