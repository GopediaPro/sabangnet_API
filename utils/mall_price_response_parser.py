import re

def parse_sabangnet_response(response_text: str):
    success = []
    failed = []
    lines = response_text.strip().split('\n')
    for line in lines:
        match = re.match(r"\[(\d+)\] (수정 성공|수정 실패) : (\d+) \[([A-Z0-9]+)\]", line)
        if match:
            idx, status, product_id, company_goods_cd = match.groups()
            item = {"product_id": product_id, "company_goods_cd": company_goods_cd}
            if status == "수정 성공":
                success.append(item)
            else:
                failed.append(item)
    return success, failed