from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from openpyxl.utils import get_column_letter

from utils.excel_handler import ExcelHandler

MULTI_SEP_RE = re.compile(r"[\/;]")


def clean_f_text(txt: str | None) -> str:
    """
    모델(F열) 문자열 정리:
    - '/' 또는 ';' 구분자는 ' + ' 로 치환
    - ' 1개' 꼬리 텍스트 제거
    """
    if txt is None:
        return ""
    txt = MULTI_SEP_RE.sub(" + ", str(txt))
    return txt.replace(" 1개", "").strip()


def bracket_text(text: str | None) -> str:
    """
    문자열 '[계정]' 형식에서 계정명만 추출
    """
    m = re.search(r"\[(.*?)\]", str(text or ""))
    return m.group(1) if m else ""

def gok_merge_packaging(file_path: str) -> str:
    ex = ExcelHandler.from_file(file_path)
    ws, wb = ex.ws, ex.wb
    last_row, last_col = ws.max_row, ws.max_column

    # 1) 기본 서식
    ex.set_basic_format()

    # 2) P열 “/” 금액 합산
    ex.sum_prow_with_slash()

    # 3) V열 “/” 정제
    for r in range(2, last_row + 1):
        v_raw = str(ws[f"V{r}"].value or "").strip()
        if "/" in v_raw:
            nums = [
                int(n)
                for n in v_raw.split("/")
                if n.strip().isdigit() and int(n) != 0
            ]
            ws[f"V{r}"].value = 0 if not nums else nums[0]

    # 4) F열 문자열 정리
    for r in range(2, last_row + 1):
        ws[f"F{r}"].value = clean_f_text(ws[f"F{r}"].value)

    # 5) E열 주문번호 10글자 자르기
    for r in range(2, last_row + 1):
        ws[f"E{r}"].value = str(ws[f"E{r}"].value)[:10]
        ws[f"E{r}"].number_format = "General"

    # 6) 정렬·A열 순번
    ex.set_column_alignment()
    ex.set_row_number()

    # 7) D열 수식: =O+P+V
    ex.autofill_d_column(formula="=O{row}+P{row}+V{row}")

    # 8) E, M, Q, W 열 문자열 숫자 → 숫자
    ex.convert_numeric_strings(cols=("E", "M", "Q", "W"))

    # 9) C → B 2단계 정렬
    data = [
        [ws.cell(row=r, column=c).value for c in range(1, last_col + 1)]
        for r in range(2, last_row + 1)
    ]
    data.sort(key=lambda x: (str(x[2]), str(x[1])))
    ws.delete_rows(2, last_row - 1)
    for ridx, row in enumerate(data, start=2):
        for cidx, val in enumerate(row, start=1):
            ws.cell(row=ridx, column=cidx, value=val)
    last_row = ws.max_row

    # 10) 배경·테두리 제거, L열 비우기
    ex.clear_fills_from_second_row()
    ex.clear_borders()
    for col_idx in range(1, last_col + 1):
        if str(ws.cell(row=1, column=col_idx).value).strip().upper() == "L":
            for r in range(2, last_row + 1):
                ws.cell(row=r, column=col_idx).value = None
            break

    # 11) 시트 분리 (OK,CL,BB / IY)
    mapping = {
        "OK,CL,BB": ["오케이마트", "클로버프", "베이지베이글"],
        "IY": ["아이예스"],
    }
    col_widths = [
        ws.column_dimensions[get_column_letter(c)].width
        for c in range(1, last_col + 1)
    ]
    rows_by_sheet = defaultdict(list)
    for r in range(2, last_row + 1):
        account = bracket_text(ws[f"B{r}"].value)
        for sh, names in mapping.items():
            if account in names:
                rows_by_sheet[sh].append(r)

    def copy_to(new_ws, src_rows):
        # 헤더 / 열 너비 복사
        for c in range(1, last_col + 1):
            new_ws.cell(row=1, column=c, value=ws.cell(row=1, column=c).value)
            new_ws.column_dimensions[get_column_letter(c)].width = col_widths[c - 1]
        # 데이터 복사
        for idx, r in enumerate(src_rows, start=2):
            for c in range(1, last_col + 1):
                new_ws.cell(row=idx, column=c, value=ws.cell(row=r, column=c).value)
            new_ws[f"A{idx}"].value = "=ROW()-1"

    for sh in mapping.keys():
        if sh in wb.sheetnames:
            del wb[sh]
        if rows_by_sheet[sh]:
            copy_to(wb.create_sheet(sh), rows_by_sheet[sh])

    # 12) 저장
    output_path = str(
        Path(file_path).with_name("G옥_합포장_자동화_" + Path(file_path).name)
    )
    wb.save(output_path)
    wb.close()
    print(f"G·옥 합포장 자동화 완료! 처리된 파일: {output_path}")
    return output_path


if __name__ == "__main__":
    test_file = "/Users/smith/Documents/github/OKMart/sabangnet_API/files/test-[기본양식]-합포장용.xlsx"
    gok_merge_packaging(test_file)
    print("모든 처리가 완료되었습니다!")