"""
사방넷 API 응답 XML 파싱 유틸리티
XML 응답에서 PRODUCT_ID, COMPAYNY_GOODS_CD, RESULT, MODE 정보를 추출하여 JSON 형태로 반환
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from utils.logs.sabangnet_logger import get_logger

logger = get_logger(__name__)


class SabangApiResultParser:
    """
    사방넷 API 응답 XML 파싱 클래스
    """
    
    @staticmethod
    def parse_sabang_api_result(xml_response: str) -> Dict[str, Any]:
        """
        사방넷 API 응답 XML을 파싱하여 JSON 형태로 반환
        
        Args:
            xml_response: 사방넷 API 응답 XML 문자열
            
        Returns:
            {
                "header": {
                    "send_compayny_id": str,
                    "send_date": str,
                    "total_count": int
                },
                "data": [
                    {
                        "result": str,
                        "mode": str,
                        "product_id": str,
                        "compayny_goods_cd": str
                    },
                    ...
                ],
                "summary": {
                    "total_count": int,
                    "success_count": int,
                    "failed_count": int,
                    "update_count": int,
                    "create_count": int
                }
            }
        """
        try:
            # XML 파싱
            root = ET.fromstring(xml_response)
            
            # 헤더 정보 추출
            header_info = SabangApiResultParser._extract_header(root)
            
            # 데이터 정보 추출
            data_list = SabangApiResultParser._extract_data(root)
            
            # 요약 정보 생성
            summary_info = SabangApiResultParser._create_summary(data_list)
            
            result = {
                "header": header_info,
                "data": data_list,
                "summary": summary_info
            }
            
            logger.info(f"XML 파싱 완료 - 총 {len(data_list)}개 항목 처리")
            return result
            
        except ET.ParseError as e:
            logger.error(f"XML 파싱 에러: {e}")
            return {
                "error": "XML 파싱 실패",
                "message": str(e),
                "header": {},
                "data": [],
                "summary": {}
            }
        except Exception as e:
            logger.error(f"예상치 못한 에러: {e}")
            return {
                "error": "처리 중 에러 발생",
                "message": str(e),
                "header": {},
                "data": [],
                "summary": {}
            }
    
    @staticmethod
    def _extract_header(root: ET.Element) -> Dict[str, Any]:
        """헤더 정보 추출"""
        header_info = {}
        
        header_element = root.find("HEADER")
        if header_element is not None:
            # SEND_COMPAYNY_ID
            send_compayny_id_elem = header_element.find("SEND_COMPAYNY_ID")
            if send_compayny_id_elem is not None:
                header_info["send_compayny_id"] = send_compayny_id_elem.text or ""
            
            # SEND_DATE
            send_date_elem = header_element.find("SEND_DATE")
            if send_date_elem is not None:
                header_info["send_date"] = send_date_elem.text or ""
            
            # TOTAL_COUNT
            total_count_elem = header_element.find("TOTAL_COUNT")
            if total_count_elem is not None:
                try:
                    header_info["total_count"] = int(total_count_elem.text or "0")
                except ValueError:
                    header_info["total_count"] = 0
        
        return header_info
    
    @staticmethod
    def _extract_data(root: ET.Element) -> List[Dict[str, str]]:
        """데이터 정보 추출"""
        data_list = []
        
        # 모든 DATA 요소 찾기
        for data_element in root.findall("DATA"):
            data_item = {}
            
            # RESULT
            result_elem = data_element.find("RESULT")
            if result_elem is not None:
                data_item["result"] = result_elem.text or ""
            
            # MODE
            mode_elem = data_element.find("MODE")
            if mode_elem is not None:
                data_item["mode"] = mode_elem.text or ""
            
            # PRODUCT_ID
            product_id_elem = data_element.find("PRODUCT_ID")
            if product_id_elem is not None:
                data_item["product_id"] = product_id_elem.text or ""
            
            # COMPAYNY_GOODS_CD
            compayny_goods_cd_elem = data_element.find("COMPAYNY_GOODS_CD")
            if compayny_goods_cd_elem is not None:
                data_item["compayny_goods_cd"] = compayny_goods_cd_elem.text or ""
            
            # 모든 필수 필드가 있는 경우만 추가
            if all(key in data_item for key in ["result", "mode", "product_id", "compayny_goods_cd"]):
                data_list.append(data_item)
            else:
                logger.warning(f"불완전한 데이터 항목 발견: {data_item}")
        
        return data_list
    
    @staticmethod
    def _create_summary(data_list: List[Dict[str, str]]) -> Dict[str, int]:
        """요약 정보 생성"""
        summary = {
            "total_count": len(data_list),
            "success_count": 0,
            "failed_count": 0,
            "update_count": 0,
            "create_count": 0
        }
        
        for item in data_list:
            # 성공/실패 카운트
            if item.get("result", "").upper() == "SUCCESS":
                summary["success_count"] += 1
            else:
                summary["failed_count"] += 1
            
            # 생성/수정 카운트
            mode = item.get("mode", "").strip()
            if mode == "수정":
                summary["update_count"] += 1
            elif mode == "등록":
                summary["create_count"] += 1
        
        return summary
    
    @staticmethod
    def get_formatted_result(xml_response: str) -> str:
        """
        XML 응답을 파싱하여 포맷된 결과 문자열 반환
        
        Args:
            xml_response: 사방넷 API 응답 XML 문자열
            
        Returns:
            포맷된 결과 문자열
        """
        result = SabangApiResultParser.parse_sabang_api_result(xml_response)
        
        if "error" in result:
            return f"에러 발생: {result['error']} - {result['message']}"
        
        summary = result["summary"]
        header = result["header"]
        
        formatted_result = f"""
=== 사방넷 API 응답 결과 ===
전송일: {header.get('send_date', 'N/A')}
전송업체ID: {header.get('send_compayny_id', 'N/A')}
총 처리 건수: {summary['total_count']}건

=== 처리 결과 ===
성공: {summary['success_count']}건
실패: {summary['failed_count']}건
수정: {summary['update_count']}건
등록: {summary['create_count']}건

=== 상세 결과 ===
"""
        
        for i, item in enumerate(result["data"], 1):
            formatted_result += f"{i}. {item['compayny_goods_cd']} (ID: {item['product_id']}) - {item['result']} ({item['mode']})\n"
        
        return formatted_result 