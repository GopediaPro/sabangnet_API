import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter


FONT_MALGUN = Font(name="맑은 고딕", size=9)
HDR_FILL = PatternFill(start_color="006100", end_color="006100", fill_type="solid")
BLUE_FILL = PatternFill(start_color="CCE8FF", end_color="CCE8FF", fill_type="solid")
NO_BORDER = Border()

STAR_QTY_RE = re.compile(r"\* ?(\d+)")
MULTI_SEP_RE = re.compile(r"[\/;]")


def to_num(val) -> float:
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0.0
    except ValueError:
        return 0.0


def clean_f_text(txt: str) -> str:
    """
    F열 문자열 정리:
    • '/' ';' → ' + '
    • '*n'  → '' 또는 ' n개'
    • ' 1개' 제거
    """
    if txt is None:
        return ""
    txt = MULTI_SEP_RE.sub(" + ", str(txt))
    txt = STAR_QTY_RE.sub(lambda m: "" if m.group(1) == "1" else f" {m.group(1)}개", txt)
    return txt.replace(" 1개", "").strip()


def format_lookup(ws_lookup) -> dict[str, str]:
    """Sheet1 A:B → dict"""
    return {
        str(r[0].value): r[1].value
        for r in ws_lookup.iter_rows(min_row=2, max_col=2, values_only=True)
        if r[0] is not None
    }


def zigzag_merge_packaging(file_path: str) -> str:
    wb = load_workbook(file_path)
    ws = wb.active
    last_row, last_col = ws.max_row, ws.max_column

    # 1: 서식 & 헤더
    for row in ws.iter_rows():
        for cell in row:
            cell.font = FONT_MALGUN
            cell.alignment = Alignment(wrap_text=False)
        ws.row_dimensions[row[0].row].height = 15
    for cell in ws[1]:
        cell.fill = HDR_FILL
        cell.alignment = Alignment(horizontal="center")

    # 2: M열 숫자화
    for r in range(2, last_row + 1):
        try:
            ws[f"M{r}"].value = int(float(ws[f"M{r}"].value))
        except (ValueError, TypeError):
            ws[f"M{r}"].value = 0

    # 3: VLOOKUP(M, Sheet1!A:B) → V열
    if "Sheet1" in wb.sheetnames:
        vmap = format_lookup(wb["Sheet1"])
        for r in range(2, last_row + 1):
            ws[f"V{r}"].value = vmap.get(str(ws[f"M{r}"].value), "")

    # 4: D = U + V
    for r in range(2, last_row + 1):
        ws[f"D{r}"].value = f"=U{r}+V{r}"

    # 5: 테두리 & 배경 제거
    for row in ws.iter_rows(min_row=2, max_row=last_row, max_col=last_col):
        for cell in row:
            cell.border = NO_BORDER
            cell.fill = PatternFill(fill_type=None)

    # 6: F열 문자열 정리 + 파란색 강조(수량 2개 이상)
    for r in range(2, last_row + 1):
        ftxt = clean_f_text(ws[f"F{r}"].value)
        ws[f"F{r}"].value = ftxt
        if ftxt.count("개") >= 2:
            ws[f"F{r}"].fill = BLUE_FILL

    # 7: A열 순번
    for r in range(2, last_row + 1):
        ws[f"A{r}"].value = "=ROW()-1"

    # 8: 열 정렬
    center = Alignment(horizontal="center")
    right = Alignment(horizontal="right")
    for col in ("A", "B"):
        for cell in ws[col]:
            cell.alignment = center
    for col in ("D", "E", "G"):
        if col in ws:
            for cell in ws[col]:
                cell.alignment = right

    # 9: C → B 정렬
    rows = [
        [ws.cell(row=r, column=c).value for c in range(1, last_col + 1)]
        for r in range(2, last_row + 1)
    ]
    rows.sort(key=lambda x: (str(x[2]), str(x[1])))  # C, B 기준
    ws.delete_rows(2, last_row - 1)
    for ridx, row in enumerate(rows, start=2):
        for cidx, val in enumerate(row, start=1):
            ws.cell(row=ridx, column=cidx, value=val)
    last_row = ws.max_row

    #P열 “/” 금액 합산  → P 갱신
    for r in range(2, last_row + 1):
        p_raw = str(ws[f"P{r}"].value or "")
        if "/" in p_raw:
            nums = [float(n) for n in p_raw.split("/") if n.strip().isdigit()]
            ws[f"P{r}"].value = sum(nums) if nums else 0
        else:
            ws[f"P{r}"].value = to_num(p_raw)
    
    # E, Q, W 열 String숫자 to 숫자 변환
    for r in range(2, last_row + 1):
        for col in ("E", "Q", "W"):
            cell = ws[f"{col}{r}"]
            val = str(cell.value).strip()

            if not val or any(op in val for op in ["/", "+", "-", "="]):
                # 변환하지 않고 기존 값 유지 (또는 cell.value = 0으로 초기화 가능)
                continue
            else:
                num_str = re.sub(r"\D", "", val)
                cell.value = int(num_str) if num_str else 0

            cell.number_format = "General"

    # 10: 시트 분리(OK, IY)
    col_widths = [ws.column_dimensions[get_column_letter(c)].width for c in range(1, last_col + 1)]

    def copy_rows(dst_ws, rows_idx):
        for c in range(1, last_col + 1):
            dst_ws.cell(row=1, column=c, value=ws.cell(row=1, column=c).value)
        for idx, r in enumerate(rows_idx, start=2):
            for c in range(1, last_col + 1):
                dst_ws.cell(row=idx, column=c, value=ws.cell(row=r, column=c).value)
            dst_ws[f"A{idx}"].value = idx - 1

    for name in ("OK", "IY"):
        if name in wb.sheetnames:
            del wb[name]

    ok_rows, iy_rows = [], []
    for r in range(2, last_row + 1):
        btxt = str(ws[f"B{r}"].value or "")
        if "[오케이마트]" in btxt:
            ok_rows.append(r)
        elif "[아이예스]" in btxt:
            iy_rows.append(r)

    if ok_rows:
        ws_ok = wb.create_sheet("OK")
        copy_rows(ws_ok, ok_rows)
        for idx, w in enumerate(col_widths, start=1):
            ws_ok.column_dimensions[get_column_letter(idx)].width = w
    if iy_rows:
        ws_iy = wb.create_sheet("IY")
        copy_rows(ws_iy, iy_rows)
        for idx, w in enumerate(col_widths, start=1):
            ws_iy.column_dimensions[get_column_letter(idx)].width = w

    # 저장
    output_path = str(Path(file_path).with_name("지그재그_합포장_자동화_" + Path(file_path).name))
    wb.save(output_path)
    print(f"지그재그 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path


if __name__ == "__main__":
    test_xlsx = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    zigzag_merge_packaging(test_xlsx)
    print("모든 처리가 완료되었습니다!")