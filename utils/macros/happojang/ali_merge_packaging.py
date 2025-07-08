from __future__ import annotations

import os
import re
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border
from openpyxl.utils import get_column_letter


FONT_MALGUN = Font(name="맑은 고딕", size=9)
HDR_FILL = PatternFill(start_color="006100",
                       end_color="006100", fill_type="solid")
BLUE_FILL = PatternFill(start_color="CCE8FF",
                        end_color="CCE8FF", fill_type="solid")
JEJU_FILL = PatternFill(start_color="DDEBF7",
                        end_color="DDEBF7", fill_type="solid")
NO_BORDER = Border()

STAR_QTY_RE = re.compile(r"\* ?(\d+)")
DUP_QTY_RE = re.compile(r"\d+개")
MULTI_SEP_RE = re.compile(r"[\/;]")


def to_num(val) -> float:
    """'12,345원' → 12345.0 (실패 시 0)."""
    try:
        return float(re.sub(r"[^\d.-]", "", str(val))) if str(val).strip() else 0.0
    except ValueError:
        return 0.0


def fmt_phone(val: str | None) -> str:
    """전화번호 01012345678 → 010-1234-5678."""
    if not val:
        return ""
    digits = re.sub(r"\D", "", str(val))
    if digits.startswith("10"):          # 10xxxxxxxx → 010xxxxxxxx
        digits = "0" + digits
    return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}" if len(digits) == 11 else digits


def clean_item(txt: str) -> str:
    """F셀 문자열 정리"""
    if txt is None:
        return ""
    txt = MULTI_SEP_RE.sub(" + ", str(txt))
    # *n 의 수량 치환

    def repl(m):
        n = m.group(1).strip()
        return "" if n == "1" else f" {n}개"
    txt = STAR_QTY_RE.sub(repl, txt)
    txt = txt.replace(" 1개", "").strip()
    return txt


def ali_merge_packaging(input_path: str) -> str:
    """
    실행 진입점
    """
    # 0: 엑셀 로드
    wb = load_workbook(input_path)
    ws = wb.active
    last_row, last_col = ws.max_row, ws.max_column

    # 1: 기본 서식
    for row in ws.iter_rows():
        for cell in row:
            cell.font = FONT_MALGUN
            cell.alignment = Alignment(wrap_text=False)
        ws.row_dimensions[row[0].row].height = 15
    for cell in ws[1]:
        cell.fill = HDR_FILL

    # 2: B‧C 정렬 (openpyxl: manual sort)
    rows = [
        [ws.cell(row=r, column=c).value for c in range(1, last_col + 1)]
        for r in range(2, last_row + 1)
    ]
    rows.sort(key=lambda x: (str(x[1]), str(x[2])))          # B, C 기준
    ws.delete_rows(2, last_row - 1)
    for ridx, row in enumerate(rows, start=2):
        for cidx, val in enumerate(row, start=1):
            ws.cell(row=ridx, column=cidx, value=val)
    last_row = ws.max_row

    # P열 “/” 금액 합산  → P 갱신
    for r in range(2, last_row + 1):
        p_raw = str(ws[f"P{r}"].value or "")
        if "/" in p_raw:
            nums = [float(n) for n in p_raw.split("/") if n.strip().isdigit()]
            ws[f"P{r}"].value = sum(nums) if nums else 0
        else:
            ws[f"P{r}"].value = to_num(p_raw)

    # 3: Z → F 복사, 열너비
    for r in range(2, last_row + 1):
        ws[f"F{r}"].value = ws[f"Z{r}"].value
    ws.column_dimensions["F"].width = 45

    # 4: F 문자열 정리
    for r in range(2, last_row + 1):
        ws[f"F{r}"].value = clean_item(ws[f"F{r}"].value)

    # 5: 배경색 제거
    for row in ws.iter_rows(min_row=2, max_row=last_row, max_col=last_col):
        for cell in row:
            cell.fill = PatternFill(fill_type=None)

    # 6: 수량 중복 행 파란색
    for r in range(2, last_row + 1):
        txt = str(ws[f"F{r}"].value or "")
        parts = [p.strip() for p in txt.split("+")]
        if sum(1 for p in parts if DUP_QTY_RE.search(p)) >= 2:
            ws[f"F{r}"].fill = BLUE_FILL

    # 7: I 전화번호 포맷 & 8. I → H 복사
    for r in range(2, last_row + 1):
        phone = fmt_phone(ws[f"I{r}"].value)
        ws[f"I{r}"].value = phone
        ws[f"H{r}"].value = phone
    ws.column_dimensions["H"].width = ws.column_dimensions["I"].width

    # 9: F 열 삽입 + LEFT(E,16)
    ws.insert_cols(6)
    ws["F1"].value = "TrimE"
    for r in range(2, last_row + 1):
        ws[f"F{r}"].value = str(ws[f"G{r}"].value)[:16]
    # 10: F → G(E) 복사 후 F 삭제
    for r in range(2, last_row + 1):
        ws[f"G{r}"].value = ws[f"F{r}"].value
    ws.delete_cols(6)
    last_col = ws.max_column

    # 12: D = U + V (as formula)
    for r in range(2, last_row + 1):
        ws[f"D{r}"].value = f"=U{r}+V{r}"

    # 13: A 순번
    for r in range(2, last_row + 1):
        ws[f"A{r}"].value = "=ROW()-1"

    # 14: 서식 정렬
    center = Alignment(horizontal="center")
    right = Alignment(horizontal="right")
    for col in ("A", "B"):
        for cell in ws[col]:
            cell.alignment = center
    for col in ("D", "E", "G"):
        for cell in ws[col]:
            cell.alignment = right
    for cell in ws[1]:
        cell.alignment = center
    ws.column_dimensions["E"].width = 20
    for row in ws.iter_rows():
        for cell in row:
            cell.border = NO_BORDER

    # 18: 다시 B,C 정렬 보증 (이미 정렬됨)

    # 19: 제주 처리
    for r in range(2, last_row + 1):
        if "제주" in str(ws[f"J{r}"].value or ""):
            ws[f"J{r}"].font = Font(color="FF0000", bold=True)
            if "[3000원 환불처리]" not in str(ws[f"F{r}"].value):
                ws[f"F{r}"].value = f"{ws[f'F{r}'].value} [3000원 환불처리]"
            ws[f"F{r}"].fill = JEJU_FILL
    
    # E, M, P, Q, W 열 String숫자 to 숫자 변환
    for r in range(2, last_row + 1):
        for col in ("E", "M", "P", "Q", "W"):
            cell = ws[f"{col}{r}"]
            cell.number_format = "General"

    # 21: VLOOKUP(F, Sheet1!A:B) → 다음 열(S)
    if "Sheet1" in wb.sheetnames:
        lookup_ws = wb["Sheet1"]
        vmap = {
            str(r[0].value): r[1].value
            for r in lookup_ws.iter_rows(min_row=2, max_col=2, values_only=True)
            if r[0] is not None
        }
        col_s = get_column_letter(last_col + 1)
        ws[f"{col_s}1"].value = "S"
        for r in range(2, last_row + 1):
            ws[f"{col_s}{r}"].value = vmap.get(str(ws[f"F{r}"].value), "S")
        last_col += 1

    # 22: 사이트별 시트 분리
    site_rows = defaultdict(list)
    for r in range(2, last_row + 1):
        text = str(ws[f"B{r}"].value or "")
        if "오케이마트" in text:
            site_rows["OK"].append(r)
        elif "아이예스" in text:
            site_rows["IY"].append(r)

    col_widths = [ws.column_dimensions[get_column_letter(
        c)].width for c in range(1, last_col + 1)]

    def copy_rows(dst, rows_idx):
        for c in range(1, last_col + 1):
            dst.cell(row=1, column=c, value=ws.cell(row=1, column=c).value)
        for i, r in enumerate(rows_idx, start=2):
            for c in range(1, last_col + 1):
                dst.cell(row=i, column=c, value=ws.cell(row=r, column=c).value)
            dst[f"A{i}"].value = i - 1

    for name in ("OK", "IY"):
        if name in wb.sheetnames:
            del wb[name]
        sheet = wb.create_sheet(name)
        copy_rows(sheet, site_rows.get(name, []))
        for idx, w in enumerate(col_widths, start=1):
            sheet.column_dimensions[get_column_letter(idx)].width = w

    # 24: 시트 순서
    desired = ["알리합포장", "OK", "IY", "Sheet1"]
    for name in reversed(desired):
        if name in wb.sheetnames:
            wb._sheets.insert(0, wb._sheets.pop(wb.sheetnames.index(name)))

    # 저장
    output_path = str(Path(input_path).with_name("알리_합포장_자동화_" + Path(input_path).name))
    wb.save(output_path)
    wb.close()
    print(f"Ali 합포장 자동화 완료: {output_path}")
    return output_path


if __name__ == "__main__":
    test_file = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    ali_merge_packaging(test_file)
    print("모든 처리가 완료되었습니다!")