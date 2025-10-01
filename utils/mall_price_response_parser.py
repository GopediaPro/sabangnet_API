import re
from utils.make_xml.sabang_api_result_parser import SabangApiResultParser
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)

def parse_sabangnet_response(response_text: str):
    """
    사방넷 API 응답을 파싱하여 성공/실패 항목을 반환
    
    Args:
        response_text: 사방넷 API 응답 XML 문자열
        
    Returns:
        tuple: (success_items, failed_items)
    """
    try:
        # XML 응답인 경우 SabangApiResultParser 사용
        if response_text.strip().startswith('<?xml') or '<SABANG_RESULT>' in response_text:
            logger.info("XML 응답 감지 - SabangApiResultParser 사용")
            parsed_result = SabangApiResultParser.parse_sabang_api_result(response_text)
            
            if "error" in parsed_result:
                logger.error(f"XML 파싱 오류: {parsed_result['error']}")
                return [], []
            
            success = []
            failed = []
            
            for item in parsed_result.get("data", []):
                result_item = {
                    "product_id": item.get("product_id", ""),
                    "company_goods_cd": item.get("compayny_goods_cd", ""),
                    "result": item.get("result", ""),
                    "mode": item.get("mode", "")
                }
                
                if item.get("result", "").upper() == "SUCCESS":
                    success.append(result_item)
                else:
                    failed.append(result_item)
            
            logger.info(f"XML 파싱 완료 - 성공: {len(success)}개, 실패: {len(failed)}개")
            return success, failed
            
        else:
            # 기존 텍스트 형식 응답 처리 (하위 호환성)
            logger.info("텍스트 응답 감지 - 기존 파싱 로직 사용")
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
            
            logger.info(f"텍스트 파싱 완료 - 성공: {len(success)}개, 실패: {len(failed)}개")
            return success, failed
            
    except Exception as e:
        logger.error(f"응답 파싱 중 오류 발생: {e}")
        return [], []