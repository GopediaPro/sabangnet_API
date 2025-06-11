#!/usr/bin/env python3
"""
사방넷 쇼핑몰 코드 조회 API 클라이언트
"""

import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import logging
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.util.ssl_ import create_urllib3_context
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

SABANG_COMPANY_ID = os.getenv('SABANG_COMPANY_ID')
SABANG_AUTH_KEY = os.getenv('SABANG_AUTH_KEY')
SABANG_ADMIN_URL = os.getenv('SABANG_ADMIN_URL')

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SSL 경고 무시 (필요한 경우)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LegacyHTTPSAdapter(HTTPAdapter):
    """레거시 SSL을 지원하는 HTTPAdapter"""
    
    def init_poolmanager(self, *args, **kwargs):
        # 레거시 SSL 재협상을 허용하는 컨텍스트 생성
        ctx = create_urllib3_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')  # 보안 레벨을 낮춤
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


class SabangNetMallAPI:
    """사방넷 쇼핑몰 API 클라이언트"""
    
    def __init__(self, company_id: str = None, auth_key: str = None, admin_url: str = None):
        """
        Args:
            company_id: 사방넷 로그인 아이디 (환경변수에서 가져올 수 있음)
            auth_key: 사방넷 인증키 (환경변수에서 가져올 수 있음)
            admin_url: 사방넷 어드민 URL (환경변수에서 가져올 수 있음)
        """
        self.company_id = company_id or os.getenv('SABANG_COMPANY_ID')
        self.auth_key = auth_key or os.getenv('SABANG_AUTH_KEY')
        self.admin_url = admin_url or os.getenv('SABANG_ADMIN_URL')
        
        if not self.company_id or not self.auth_key:
            raise ValueError("SABANG_COMPANY_ID와 SABANG_AUTH_KEY는 필수입니다.")
        
        # SSL 문제 해결을 위한 requests 세션 설정
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """SSL 문제를 해결하기 위한 세션 생성"""
        session = requests.Session()
        
        # 재시도 전략 설정
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # 레거시 HTTPS 어댑터 적용
        session.mount("https://", LegacyHTTPSAdapter(max_retries=retry_strategy))
        session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        
        return session
    
    def create_request_xml(self, send_date: str = None) -> str:
        """요청 XML 생성
        
        Args:
            send_date: 전송일자 (YYYYMMDD), None이면 오늘 날짜 사용
            
        Returns:
            XML 문자열
        """
        if not send_date:
            send_date = datetime.now().strftime('%Y%m%d')
        
        xml_content = f"""<?xml version="1.0" encoding="EUC-KR"?>
<SABANG_MALL_LIST>
    <HEADER>
        <SEND_COMPAYNY_ID>{self.company_id}</SEND_COMPAYNY_ID>
        <SEND_AUTH_KEY>{self.auth_key}</SEND_AUTH_KEY>
        <SEND_DATE>{send_date}</SEND_DATE>
    </HEADER>
</SABANG_MALL_LIST>"""
        
        return xml_content
    
    def save_xml_to_file(self, xml_content: str, file_path: str = 'mall_request.xml'):
        """XML 내용을 파일로 저장
        
        Args:
            xml_content: XML 문자열
            file_path: 저장할 파일 경로
        """
        try:
            with open(file_path, 'w', encoding='euc-kr') as f:
                f.write(xml_content)
            logger.info(f"XML 파일이 저장되었습니다: {file_path}")
        except Exception as e:
            logger.error(f"XML 파일 저장 실패: {e}")
            raise
    
    def get_mall_list_via_url(self, xml_url: str) -> List[Dict[str, str]]:
        """XML URL을 통해 쇼핑몰 목록 조회
        
        Args:
            xml_url: 쇼핑몰코드조회xml주소
            
        Returns:
            쇼핑몰 정보 리스트 [{'mall_id': 'shop0002', 'mall_name': '지마켓'}, ...]
        """
        return self._make_api_request(
            method='GET',
            params={'xml_url': xml_url},
            description=f"XML URL 방식 (URL: {xml_url})"
        )
    
    def get_mall_list_direct(self, send_date: str = None) -> List[Dict[str, str]]:
        """직접 API 호출로 쇼핑몰 목록 조회 (XML URL 불필요)
        
        Args:
            send_date: 전송일자 (YYYYMMDD), None이면 오늘 날짜 사용
            
        Returns:
            쇼핑몰 정보 리스트 [{'mall_id': 'shop0002', 'mall_name': '지마켓'}, ...]
        """
        try:
            # 방법 1: POST 요청으로 XML 전송
            xml_content = self.create_request_xml(send_date)
            
            headers = {
                'Content-Type': 'application/xml; charset=euc-kr',
                'Accept': 'application/xml'
            }
            
            logger.info("POST 방식으로 직접 API 호출 시도")
            result = self._make_api_request(
                method='POST',
                data=xml_content.encode('euc-kr'),
                headers=headers,
                description="POST 방식 (XML 본문 전송)"
            )
            
            if result:
                return result
            
        except Exception as e:
            logger.warning(f"POST 방식 실패: {e}")
        
        # 방법 2: GET 파라미터 방식
        logger.info("GET 파라미터 방식으로 재시도")
        return self._try_get_params_method(send_date)
    
    def _make_api_request(self, method: str, params: dict = None, data: bytes = None, 
                         headers: dict = None, description: str = "") -> List[Dict[str, str]]:
        """API 요청 공통 함수 - SSL 문제 해결 포함
        
        Args:
            method: HTTP 메서드 ('GET' 또는 'POST')
            params: GET 파라미터
            data: POST 데이터
            headers: HTTP 헤더
            description: 로깅용 설명
            
        Returns:
            쇼핑몰 정보 리스트
        """
        api_url = urljoin(self.admin_url, '/RTL_API/xml_mall_info.html')
        
        # 여러 방법으로 시도
        methods = [
            ('secure', self._try_secure_request),
            ('insecure', self._try_insecure_request),
            ('http', self._try_http_request)
        ]
        
        for method_name, request_func in methods:
            try:
                logger.info(f"{description} - {method_name} 방식 시도: {api_url}")
                
                response = request_func(api_url, method, params, data, headers)
                
                if response and response.status_code == 200:
                    logger.info(f"성공: {method_name} 방식")
                    return self.parse_response_xml(response.text)
                    
            except Exception as e:
                logger.warning(f"{method_name} 방식 실패: {e}")
                continue
        
        raise Exception(f"모든 연결 방법이 실패했습니다: {description}")
    
    def _try_secure_request(self, api_url: str, method: str, params: dict = None, 
                          data: bytes = None, headers: dict = None) -> requests.Response:
        """보안 연결 시도 (레거시 SSL 지원)"""
        if method == 'GET':
            return self.session.get(api_url, params=params, headers=headers, timeout=30)
        else:
            return self.session.post(api_url, data=data, headers=headers, timeout=30)
    
    def _try_insecure_request(self, api_url: str, method: str, params: dict = None, 
                            data: bytes = None, headers: dict = None) -> requests.Response:
        """비보안 연결 시도 (SSL 검증 무시)"""
        if method == 'GET':
            return self.session.get(api_url, params=params, headers=headers, 
                                  timeout=30, verify=False)
        else:
            return self.session.post(api_url, data=data, headers=headers, 
                                   timeout=30, verify=False)
    
    def _try_http_request(self, api_url: str, method: str, params: dict = None, 
                        data: bytes = None, headers: dict = None) -> requests.Response:
        """HTTP 연결 시도 (HTTPS 대신)"""
        http_url = api_url.replace('https://', 'http://')
        
        if method == 'GET':
            return self.session.get(http_url, params=params, headers=headers, timeout=30)
        else:
            return self.session.post(http_url, data=data, headers=headers, timeout=30)
    
    def _try_get_params_method(self, send_date: str = None) -> List[Dict[str, str]]:
        """GET 파라미터 방식으로 API 호출
        
        Args:
            send_date: 전송일자 (YYYYMMDD)
            
        Returns:
            쇼핑몰 정보 리스트
        """
        try:
            if not send_date:
                send_date = datetime.now().strftime('%Y%m%d')
            
            # 다양한 API 엔드포인트 시도
            endpoints = [
                '/RTL_API/xml_mall_info.html',
                '/RTL_API/mall_list.html',
                '/api/mall_list',
                '/RTL_API/get_mall_info'
            ]
            
            params = {
                'company_id': self.company_id,
                'auth_key': self.auth_key,
                'send_date': send_date,
                'format': 'xml'
            }
            
            for endpoint in endpoints:
                try:
                    api_url = urljoin(self.admin_url, endpoint)
                    result = self._make_api_request(
                        method='GET',
                        params=params,
                        description=f"GET 파라미터 방식 ({endpoint})"
                    )
                    
                    if result:
                        logger.info(f"성공: {endpoint}")
                        return result
                        
                except Exception as e:
                    logger.warning(f"엔드포인트 {endpoint} 실패: {e}")
                    continue
            
            # 모든 방법이 실패하면 예외 발생
            raise Exception("모든 직접 API 호출 방법이 실패했습니다. XML URL 방식을 사용해주세요.")
            
        except Exception as e:
            logger.error(f"GET 파라미터 방식 실패: {e}")
            raise
    
    def parse_response_xml(self, xml_content: str) -> List[Dict[str, str]]:
        """응답 XML 파싱
        
        Args:
            xml_content: XML 응답 문자열
            
        Returns:
            쇼핑몰 정보 리스트
        """
        try:
            # XML 파싱
            root = ET.fromstring(xml_content.encode('euc-kr'))
            
            mall_list = []
            
            # DATA 노드들 찾기
            for data_node in root.findall('DATA'):
                mall_id_node = data_node.find('MALL_ID')
                mall_name_node = data_node.find('MALL_NAME')
                
                if mall_id_node is not None and mall_name_node is not None:
                    mall_info = {
                        'mall_id': mall_id_node.text.strip() if mall_id_node.text else '',
                        'mall_name': mall_name_node.text.strip() if mall_name_node.text else ''
                    }
                    mall_list.append(mall_info)
            
            logger.info(f"총 {len(mall_list)}개의 쇼핑몰 정보를 파싱했습니다.")
            return mall_list
            
        except ET.ParseError as e:
            logger.error(f"XML 파싱 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {e}")
            raise
    
    def display_mall_list(self, mall_list: List[Dict[str, str]]):
        """쇼핑몰 목록 출력
        
        Args:
            mall_list: 쇼핑몰 정보 리스트
        """
        if not mall_list:
            print("조회된 쇼핑몰이 없습니다.")
            return
        
        print(f"\n{'='*50}")
        print(f"{'쇼핑몰 목록':^20}")
        print(f"{'='*50}")
        print(f"{'몰 ID':<15} {'몰 이름'}")
        print(f"{'-'*50}")
        
        for mall in mall_list:
            print(f"{mall['mall_id']:<15} {mall['mall_name']}")
        
        print(f"{'-'*50}")
        print(f"총 {len(mall_list)}개 쇼핑몰")


def main():
    """메인 실행 함수"""
    try:
        # 환경변수에서 설정 로드
        api = SabangNetMallAPI()
        
        print("사방넷 쇼핑몰 목록 조회")
        print("=" * 50)
        print("1. 직접 API 호출 (XML URL 불필요)")
        print("2. XML URL을 통한 호출")
        
        choice = input("\n선택하세요 (1 또는 2): ").strip()
        
        if choice == "1":
            # 직접 API 호출 방식
            print("\n직접 API 호출 방식을 사용합니다...")
            mall_list = api.get_mall_list_direct()
            
        elif choice == "2":
            # XML URL 방식
            # 요청 XML 생성
            xml_content = api.create_request_xml()
            
            # XML 파일로 저장 (선택사항)
            xml_file_path = 'mall_request.xml'
            api.save_xml_to_file(xml_content, xml_file_path)
            print(f"\n요청 XML이 {xml_file_path}에 저장되었습니다.")
            print("이 파일을 웹 서버에 업로드하고 URL을 입력해주세요.")
            
            xml_url = input("\nXML 파일의 URL을 입력하세요 (예: http://www.abc.co.kr/aa.xml): ").strip()
            
            if not xml_url:
                print("유효한 XML URL을 입력해주세요.")
                return
            
            # 쇼핑몰 목록 조회
            mall_list = api.get_mall_list_via_url(xml_url)
            
        else:
            print("잘못된 선택입니다.")
            return
        
        # 결과 출력
        api.display_mall_list(mall_list)
        
    except ValueError as e:
        logger.error(f"설정 오류: {e}")
        print("\n환경변수를 확인해주세요:")
        print("- SABANG_COMPANY_ID: 사방넷 로그인 아이디")
        print("- SABANG_AUTH_KEY: 사방넷 인증키")
        print("- SABANG_ADMIN_URL: 사방넷 어드민 URL (선택사항)")
        
    except Exception as e:
        logger.error(f"실행 중 오류: {e}")
        print(f"\n오류가 발생했습니다: {e}")
        print("\n가능한 해결 방법:")
        print("1. 사방넷 계정 정보가 올바른지 확인")
        print("2. 인증키가 유효한지 확인")
        print("3. 네트워크 연결 상태 확인")
        print("4. XML URL 방식으로 다시 시도")


if __name__ == "__main__":
    main()