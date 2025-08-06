def average_duplicate_cart_address_amounts(ws):
    """
    Q셀(장바구니번호)과 J셀(수취인주소)이 같은 값들의 D셀(금액)을 평균내는 메서드
    
    Args:
        ws: openpyxl의 worksheet 객체
    """
    # 장바구니번호와 수취인주소 조합으로 그룹화
    duplicate_groups = {}
    
    for row in range(2, ws.max_row + 1):
        cart_number = str(ws[f"Q{row}"].value).strip()
        address = str(ws[f"J{row}"].value).strip()
        amount = ws[f"D{row}"].value
        
        # 빈 값이 아닌 경우에만 처리
        if cart_number and cart_number != "None" and address and address != "None":
            key = f"{cart_number}_{address}"
            
            if key not in duplicate_groups:
                duplicate_groups[key] = []
            
            duplicate_groups[key].append({
                'row': row,
                'amount': int(amount) if amount is not None else 0
            })
    
    # 2개 이상인 그룹에 대해 평균 계산 및 적용
    for key, group in duplicate_groups.items():
        if len(group) >= 2:
            total_amount = sum(item['amount'] for item in group)
            average_amount = total_amount / len(group)
            
            # 모든 행에 평균값 적용
            for item in group:
                ws[f"D{item['row']}"].value = average_amount
            
            print(f"장바구니번호-주소 조합 '{key}'의 {len(group)}개 행에 평균 금액 {average_amount:.2f} 적용")
