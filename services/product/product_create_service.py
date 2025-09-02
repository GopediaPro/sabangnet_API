import requests
import aiohttp
from urllib.parse import urljoin
from core.settings import SETTINGS
from pathlib import Path
from utils.logs.sabangnet_logger import get_logger
from utils.make_xml.product_create_xml import ProductCreateXml


logger = get_logger(__name__, level="DEBUG")


class ProductCreateService:

    @staticmethod
    async def request_product_create_via_url(xml_url: str) -> str:
        try:
            api_url = urljoin(SETTINGS.SABANG_ADMIN_URL, '/RTL_API/xml_goods_info.html')
            # post 방식은 됐다 안됐다 함.
            # payload = {
            #     'xml_url': xml_url
            # }
            # response = requests.post(
            #     api_url,
            #     data=payload,
            #     timeout=30
            # )
            # response.raise_for_status()
            # return response.text
            full_url = f"{api_url}?xml_url={xml_url}"
            logger.info(f"최종 요청 URL: {full_url}")

            # response = requests.get(full_url, timeout=30)  # 사방넷 API에 요청을 보내기 전에 URL을 확인하기 위해 호출
            # response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킴
            # # 요청 URL과 응답을 로그에 기록
            # response_text = response.text
            # return response_text
            
            # 비동기 HTTP 요청으로 변경
            async with aiohttp.ClientSession() as session:
                async with session.get(full_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response_text = await response.text()
                    # 로그에는 전체 응답을 기록하되, 너무 길면 일부만 표시
                    log_response = response_text[:3000] + "..." if len(response_text) > 3000 else response_text
                    logger.info(f"API 요청 결과: {log_response}")
                    response.raise_for_status()
                    return response_text
        except Exception as e:
            logger.error(f"사방넷 API 요청 중 오류: {e}")
            
            # 오류 메시지에 API 응답 정보 포함
            error_message = f"사방넷 API 요청 중 오류: {str(e)}"
            
            # HTTP 오류인 경우 추가 정보 포함
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                try:
                    response_text = e.response.text
                    if len(response_text) > 500:
                        response_text = response_text[:500] + "..."
                    error_message += f" (API 응답: {response_text})"
                except:
                    pass
            
            # XML 파싱 오류인 경우 추가 정보 포함
            if "unclosed token" in str(e) or "XML" in str(e):
                error_message += " (XML 파싱 오류가 발생했습니다. 사방넷 API 응답을 확인해주세요.)"
            
            raise Exception(error_message)

    @staticmethod
    def excel_to_xml_file(file_name: str, sheet_name: str, dst_path_name: str = None) -> Path:
        return ProductCreateXml(file_name, sheet_name).make_product_create_xml(dst_path_name=dst_path_name)