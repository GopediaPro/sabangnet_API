from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter

FONT_MALGUN = Font(name="맑은 고딕", size=9)
HDR_FILL = PatternFill(start_color="006100",
                       end_color="006100", fill_type="solid")
BLUE_FILL = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")
NO_BORDER = Border()
MULTI_SEP_RE = re.compile(r"[\/;]")


def to_num(val) -> float:
    """'12,345원' → 12345.0 (실패 시 0)"""
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0.0
    except ValueError:
        return 0.0


def bracket_text(text: str) -> str:
    """'[계정]' 안 텍스트 추출"""
    m = re.search(r"\[(.*?)\]", str(text))
    return m.group(1) if m else ""


def clean_f_text(txt: str) -> str:
    """F열 문자열 정리 ('/'‧';' → ' + ', ' 1개' 제거)"""
    if txt is None:
        return ""
    txt = MULTI_SEP_RE.sub(" + ", str(txt))
    return txt.replace(" 1개", "").strip()


def gok_merge_packaging(file_path: str) -> str:
    wb = load_workbook(file_path)
    ws = wb.active
    last_row, last_col = ws.max_row, ws.max_column

    # 1: 서식 & 헤더색
    for row in ws.iter_rows():
        for cell in row:
            cell.font = FONT_MALGUN
            cell.alignment = Alignment(wrap_text=False)
        ws.row_dimensions[row[0].row].height = 15
    for cell in ws[1]:
        cell.fill = HDR_FILL
        cell.alignment = Alignment(horizontal="center")

    # 2: P열 “/” 금액 합산  → P 갱신
    for r in range(2, last_row + 1):
        p_raw = str(ws[f"P{r}"].value or "")
        if "/" in p_raw:
            nums = [float(n) for n in p_raw.split("/") if n.strip().isdigit()]
            ws[f"P{r}"].value = sum(nums) if nums else 0
        else:
            ws[f"P{r}"].value = to_num(p_raw)

    # 3: V열 “/” 정제 (0 제외·전부 같으면 하나만, 다르면 첫 값)
    for r in range(2, last_row + 1):
        v_raw = str(ws[f"V{r}"].value or "").strip()
        if "/" in v_raw:
            nums = [int(n) for n in v_raw.split("/") if n.strip().isdigit() and int(n) != 0]
            ws[f"V{r}"].value = 0 if not nums else nums[0]

    # 5: F열 문자열 정리
    for r in range(2, last_row + 1):
        ws[f"F{r}"].value = clean_f_text(ws[f"F{r}"].value)

    # 6: E열 주문번호 10자(LEFT)
    for r in range(2, last_row + 1):
        ws[f"E{r}"].value = str(ws[f"E{r}"].value)[:10]

    # 7: E열 숫자 서식
    for r in range(2, last_row + 1):
        ws[f"E{r}"].number_format = "General"

    # 8:. 열 정렬
    center, right = Alignment(horizontal="center"), Alignment(horizontal="right")
    for col in ("A", "B"):
        for cell in ws[col]:
            cell.alignment = center
    for col in ("D", "E", "G"):
        for cell in ws[col]:
            cell.alignment = right

    # 9: A열 순번
    for r in range(2, last_row + 1):
        ws[f"A{r}"].value = "=ROW()-1"

    # 10: C → B 정렬 (두 단계)
    rows = [
        [ws.cell(row=r, column=c).value for c in range(1, last_col + 1)]
        for r in range(2, last_row + 1)
    ]
    rows.sort(key=lambda x: (str(x[2]), str(x[1])))
    ws.delete_rows(2, last_row - 1)
    for ridx, row in enumerate(rows, start=2):
        for cidx, val in enumerate(row, start=1):
            ws.cell(row=ridx, column=cidx, value=val)
    last_row = ws.max_row

    # 11: 배경·테두리 제거
    for row in ws.iter_rows(min_row=2, max_row=last_row, max_col=last_col):
        for cell in row:
            cell.fill = PatternFill(fill_type=None)
            cell.border = NO_BORDER

    # 12: L열 내용 삭제 (헤더가 'L'인 실제 열 찾기)
    for col_idx in range(1, last_col + 1):
        if str(ws.cell(row=1, column=col_idx).value).strip().upper() == "L":
            for r in range(2, last_row + 1):
                ws.cell(row=r, column=col_idx).value = None
            break
    
    # 4: **D = O + P + V**
    for r in range(2, last_row + 1):
        ws[f"D{r}"].value = f"=O{r}+P{r}+V{r}" 

    # E, M, Q, W 열 String숫자 to 숫자 변환
    for r in range(2, last_row + 1):
        for col in ("E", "M", "Q", "W"):
            cell = ws[f"{col}{r}"]
            val = cell.value
            if val is None:
                cell.value = 0
            else:
                num_str = re.sub(r"\D", "", str(val))
                cell.value = int(num_str) if num_str else 0
            cell.number_format = "General"

    # 13: 시트 분리 (OK,CL,BB / IY)
    mapping = {
        "OK,CL,BB": ["오케이마트", "클로버프", "베이지베이글"],
        "IY": ["아이예스"],
    }
    col_widths = [ws.column_dimensions[get_column_letter(c)].width for c in range(1, last_col + 1)]

    rows_by_sheet = defaultdict(list)
    for r in range(2, last_row + 1):
        acc = bracket_text(ws[f"B{r}"].value)
        for sh, names in mapping.items():
            if acc in names:
                rows_by_sheet[sh].append(r)

    def copy_to(new_ws, src_rows):
        for c in range(1, last_col + 1):
            new_ws.cell(row=1, column=c, value=ws.cell(row=1, column=c).value)
            new_ws.column_dimensions[get_column_letter(c)].width = col_widths[c - 1]
        for idx, r in enumerate(src_rows, start=2):
            for c in range(1, last_col + 1):
                new_ws.cell(row=idx, column=c, value=ws.cell(row=r, column=c).value)
            new_ws[f"A{idx}"].value = idx - 1

    for sh in mapping.keys():
        if sh in wb.sheetnames:
            del wb[sh]
        if rows_by_sheet[sh]:
            copy_to(wb.create_sheet(sh), rows_by_sheet[sh])

    # 저장
    output_path = str(Path(file_path).with_name("G옥_합포장_자동화_" + Path(file_path).name))
    
    wb.save(output_path)
    wb.close()
    print(f"G·옥 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path


if __name__ == "__main__":
    test_file = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    gok_merge_packaging(test_file)
    print("모든 처리가 완료되었습니다!")