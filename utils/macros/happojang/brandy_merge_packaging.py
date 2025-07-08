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

def to_num(val):
    """쉼표·원화기호 등을 제거하고 float 변환 (실패 시 0)."""
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0
    except ValueError:
        return 0


def format_phone(val: str) -> str:
    """01012345678  →  010-1234-5678"""
    val = re.sub(r"[^\d]", "", str(val or ""))
    return f"{val[:3]}-{val[3:7]}-{val[7:]}" if len(val) == 11 and val.startswith("010") else val


def brandy_merge_packaging(file_path: str) -> str:
    wb = load_workbook(file_path)
    ws = wb.active

    last_row = ws.max_row
    last_col = ws.max_column

    # 1: 서식 & 헤더색
    for row in ws.iter_rows():
        for cell in row:
            cell.font = FONT_MALGUN
            cell.alignment = Alignment(wrap_text=False)
        ws.row_dimensions[row[0].row].height = 15
    for cell in ws[1]:
        cell.fill = HDR_FILL
        cell.alignment = Alignment(horizontal="center")

    # 2: D열 값을 P열 + V열의 합으로 계산
    for r in range(2, last_row + 1):
        ws[f"D{r}"].value = f"=P{r}+V{r}"

    # 4~6: 그룹핑·금액합산·모델명 병합·중복 삭제
    groups: dict[str, list[int]] = defaultdict(list)
    for i in range(2, last_row + 1):
        key = f"{str(ws[f'C{i}'].value).strip()}|{str(ws[f'J{i}'].value).strip()}"
        groups[key].append(i)

    rows_to_delete = []
    for idx_list in groups.values():
        if len(idx_list) == 1:
            continue

        total_amount = sum(to_num(ws[f"D{r}"].value) for r in idx_list)
        ws[f"D{idx_list[0]}"].value = total_amount

        models = [
            str(ws[f"F{r}"].value).replace(" 1개", "").strip()
            for r in idx_list
            if ws[f"F{r}"].value not in (None, "")
        ]
        ws[f"F{idx_list[0]}"].value = " + ".join(models)
        rows_to_delete.extend(idx_list[1:])

    for r in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(r)
    last_row = ws.max_row

    # 7: F열 ' 1개' 제거 
    for i in range(2, last_row + 1):
        if ws[f"F{i}"].value:
            ws[f"F{i}"].value = str(ws[f"F{i}"].value).replace(" 1개", "")

    # 8: 배경색 제거 
    for row in ws.iter_rows(min_row=2, max_row=last_row, max_col=last_col):
        for cell in row:
            cell.fill = PatternFill(fill_type=None)

    # 9: 전화번호 포맷 
    for i in range(2, last_row + 1):
        ws[f"H{i}"].value = format_phone(ws[f"H{i}"].value)
        ws[f"I{i}"].value = format_phone(ws[f"I{i}"].value)

    # 10: A열 순번 
    for r in range(2, last_row + 1):
        ws[f"A{r}"].value = "=ROW()-1"

    # 11: 테두리 제거 
    border_none = Border()
    for row in ws.iter_rows():
        for cell in row:
            cell.border = border_none

    # 12: 제주 주소 처리 
    for i in range(2, last_row + 1):
        if "제주" in str(ws[f"J{i}"].value or ""):
            if "[3000원 연락해야함]" not in str(ws[f"F{i}"].value):
                ws[f"F{i}"].value = f"{ws[f'F{i}'].value} [3000원 연락해야함]"
            ws[f"F{i}"].fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
            ws[f"J{i}"].font = Font(color="FF0000", bold=True)

    # 13: 열 정렬 
    center_align = Alignment(horizontal="center")
    right_align = Alignment(horizontal="right")
    for col in ("A", "B"):
        for cell in ws[col]:
            cell.alignment = center_align
    for col in ("D", "E", "G"):
        for cell in ws[col]:
            cell.alignment = right_align
    for cell in ws[1]:
        cell.alignment = center_align

    # 14: D열 금액 오름차순 정렬 
    rows = [
        [ws.cell(row=r, column=c).value for c in range(1, last_col + 1)]
        for r in range(2, last_row + 1)
    ]
    rows.sort(key=lambda x: to_num(x[3]))  # D열(4번째) 기준

    ws.delete_rows(2, ws.max_row - 1)
    for r_idx, row_data in enumerate(rows, start=2):
        for c_idx, value in enumerate(row_data, start=1):
            ws.cell(row=r_idx, column=c_idx, value=value)

    # E, M, P, Q, W 열 String숫자 to 숫자 변환 (단, '/' 등 포함 시 변환하지 않음)
    for r in range(2, last_row + 1):
        for col in ("E", "M", "P", "Q", "W"):
            cell = ws[f"{col}{r}"]
            val = str(cell.value).strip()

            if not val or any(op in val for op in ["/", "+", "-", "="]):
                # 변환하지 않고 기존 값 유지 (또는 cell.value = 0으로 초기화 가능)
                continue
            else:
                num_str = re.sub(r"\D", "", val)
                cell.value = int(num_str) if num_str else 0

            cell.number_format = "General"

    # 저장
    output_path = str(Path(file_path).with_name("브랜디_합포장_자동화_" + Path(file_path).name))
    wb.save(output_path)
    print(f"브랜디 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path


if __name__ == "__main__":
    test_path = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    brandy_merge_packaging(test_path)