from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from pathlib import Path
import pandas as pd
import re

def format_phone(phone):
    phone = re.sub(r"\D", "", str(phone))
    if len(phone) == 11 and phone.startswith("010"):
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    return phone

def extract_bracket_text(text):
    match = re.search(r"\[(.*?)\]", str(text))
    return match.group(1) if match else ""

def etc_site_merge_packaging(input_path: str) -> str:
    # 1: 엑셀 파일 정렬(B, C) 및 서식 적용, 첫행 색상, 열너비 설정
    df = pd.read_excel(input_path, engine="openpyxl")
    df.sort_values(by=[df.columns[1], df.columns[2]], ascending=[True, True], inplace=True)

    temp_path = "_temp_sorted.xlsx"
    df.to_excel(temp_path, index=False)
    wb = load_workbook(temp_path)
    ws = wb.active
    last_row = ws.max_row

    for row in ws.iter_rows():
        for cell in row:
            cell.font = Font(name="맑은 고딕", size=9)
            cell.alignment = Alignment(wrap_text=False)
    for cell in ws[1]:
        cell.fill = PatternFill(start_color="006100", end_color="006100", fill_type="solid")

    ws.column_dimensions['E'].width = 25
    ws.column_dimensions['F'].width = 40

    # 2: D열 값을 U열 + V열의 합으로 계산
    for i in range(2, last_row + 1):
        u_raw = ws[f"U{i}"].value or 0
        v_raw = ws[f"V{i}"].value or 0
        # 숫자 이외의 문자(쉼표, 원화기호 등)가 있으면 제거하고 float 변환
        try:
            u_val = float(re.sub(r"[^\d.-]", "", str(u_raw))) if str(u_raw).strip() != "" else 0
        except ValueError:
            u_val = 0
        try:
            v_val = float(re.sub(r"[^\d.-]", "", str(v_raw))) if str(v_raw).strip() != "" else 0
        except ValueError:
            v_val = 0
        ws[f"D{i}"].value = u_val + v_val

    # 3: A열 순번 부여
    for i in range(2, last_row + 1):
        ws[f"A{i}"].value = i - 1

    # 4~8: 배송비/금액 조건별 처리 (롯데온 외 배송비 나누기, 오늘의집/토스/현대몰 등)
    for i in range(2, last_row + 1):
        site = str(ws[f"B{i}"].value or "")
        order_text = str(ws[f"X{i}"].value or "")
        v_val = ws[f"V{i}"].value or 0
        u_val = ws[f"U{i}"].value or 0

        # 6: 롯데온 외 배송비 나누기
        if any(s in site for s in ["롯데온", "보리보리", "스마트스토어", "톡스토어"]) and "/" in order_text:
            count = len(order_text.split("/"))
            if v_val > 3000 and count > 0:
                ws[f"V{i}"].value = round(v_val / count)
                ws[f"V{i}"].font = Font(color="FF0000", bold=True)

        # 7: 오늘의집 배송비 0 처리
        if "오늘의집" in site:
            ws[f"V{i}"].value = 0
            ws[f"V{i}"].font = Font(color="FF0000", bold=True)

        # 8: 토스 배송비 조건
        if "토스" in site:
            ws[f"V{i}"].value = 0 if u_val > 30000 else 3000
            ws[f"V{i}"].font = Font(color="FF0000", bold=True)

    # 9: 전화번호 포맷(H, I)
    for i in range(2, last_row + 1):
        ws[f"H{i}"].value = format_phone(ws[f"H{i}"].value)
        ws[f"I{i}"].value = format_phone(ws[f"I{i}"].value)

    # 10~13: 사이트별 주문번호 자르기 (F열 임시 사용, 쿠팡 등)
    ws.insert_cols(6)
    ws["F1"] = "주문번호(단일)"
    for i in range(2, last_row + 1):
        site = str(ws[f"B{i}"].value or "")
        order_raw = str(ws[f"E{i}"].value or "")

        if "YES24" in site:
            ws[f"F{i}"].value = order_raw[:11]
        elif "CJ온스타일" in site:
            ws[f"F{i}"].value = order_raw[:26]
        elif "GSSHOP" in site:
            ws[f"F{i}"].value = order_raw[:21]
        elif "스마트스토어" in site:
            ws[f"F{i}"].value = order_raw[:16]
        elif "에이블리" in site:
            ws[f"F{i}"].value = order_raw[:13]
        elif "올웨이즈" in site:
            ws[f"F{i}"].value = order_raw[:36]
        elif "카카오선물하기" in site or "카카오톡스토어" in site:
            ws[f"F{i}"].value = order_raw[:10]
        elif "쿠팡" in site:
            slash_count = order_raw.count("/")
            pure_length = len(order_raw.replace("/", ""))
            each_len = pure_length // (slash_count + 1) if slash_count > 0 else pure_length
            ws[f"F{i}"].value = order_raw[:each_len]

        ws[f"E{i}"].value = ws[f"F{i}"].value

    # 14: F열 삭제
    ws.delete_cols(6)

    # 15: 특정 사이트 주문번호 숫자 서식 변환
    targets = ["에이블리", "오늘의집", "쿠팡", "텐바이텐", "NS홈쇼핑", "그립", "보리보리", "카카오선물하기", "톡스토어", "토스"]
    for i in range(2, last_row + 1):
        site = str(ws[f"B{i}"].value or "")
        if any(t in site for t in targets):
            try:
                ws[f"E{i}"].number_format = '0'
                ws[f"E{i}"].value = int(re.sub(r"\D", "", str(ws[f"E{i}"].value)))
            except:
                pass

    # 16: 두번째 행부터 Z열까지 배경색 제거
    for row in ws.iter_rows(min_row=2, max_row=last_row, min_col=1, max_col=26):
        for cell in row:
            cell.fill = PatternFill(fill_type=None)

    # 18: G열 텍스트 정리 (" 1개" 제거, "/"를 "+"로)
    for i in range(2, last_row + 1):
        val = str(ws[f"G{i}"].value or "")
        val = val.replace(" 1개", "").replace("/", " + ")
        ws[f"G{i}"].value = val

    # 19: L열 '신용'은 빈값, '착불'은 빨간색/굵게
    for i in range(2, last_row + 1):
        val = str(ws[f"L{i}"].value or "")
        if val == "신용":
            ws[f"L{i}"].value = ""
        elif val == "착불":
            ws[f"L{i}"].font = Font(color="FF0000", bold=True)

    # 20: B에 '카카오', J에 '제주' 포함시 G 수정 및 J 강조
    for i in range(2, last_row + 1):
        site = str(ws[f"B{i}"].value or "")
        addr = str(ws[f"J{i}"].value or "")
        if "카카오" in site and "제주" in addr:
            ws[f"G{i}"].value = str(ws[f"G{i}"].value) + " [3000원 연락해야함]"
            ws[f"G{i}"].fill = PatternFill(start_color="CCFFFF", end_color="CCFFFF", fill_type="solid")
            ws[f"J{i}"].font = Font(color="FF0000", bold=True)

    # 21: 열 정렬
    for col in ["A", "B"]:
        for cell in ws[col]:
            cell.alignment = Alignment(horizontal="center")
    for col in ["D", "E", "G"]:
        for cell in ws[col]:
            cell.alignment = Alignment(horizontal="right")
    for cell in ws[1]:
        cell.alignment = Alignment(horizontal="center")

    # 22: 시트 분리(OK, IY, BB) + 열너비 유지 + A열 순번 재설정
    site_filter = ["오케이마트", "아이예스", "베이지베이글"]
    site_code = ["OK", "IY", "BB"]
    total_cols = ws.max_column
    col_widths = [ws.column_dimensions[get_column_letter(i+1)].width for i in range(total_cols)]

    for keyword, code in zip(site_filter, site_code):
        if code in wb.sheetnames:
            del wb[code]
        dest = wb.create_sheet(title=code)
        for col_idx, width in enumerate(col_widths):
            dest.column_dimensions[get_column_letter(col_idx+1)].width = width
        for col in range(1, total_cols + 1):
            dest.cell(row=1, column=col).value = ws.cell(row=1, column=col).value
        row_index = 2
        for r in range(2, last_row + 1):
            if extract_bracket_text(ws[f"B{r}"].value) == keyword:
                for c in range(1, total_cols + 1):
                    dest.cell(row=row_index, column=c).value = ws.cell(row=r, column=c).value
                dest[f"A{row_index}"].value = row_index - 1
                row_index += 1

    output_path = str(Path(input_path).with_name("기타사이트_합포장_자동화_" + Path(input_path).name))

    wb.save(output_path)
    return output_path

if __name__ == "__main__":
    excel_file_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    processed_file = etc_site_merge_packaging(excel_file_path)
    print("모든 처리가 완료되었습니다!")