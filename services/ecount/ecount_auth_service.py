"""
이카운트 인증 서비스
"""
from typing import Optional, Tuple

from core.settings import SETTINGS
from schemas.ecount.auth_schemas import (
    EcountAuthInfo,
    LoginRequest,
    LoginResponse,
    ZoneRequest,
    ZoneResponse,
)
from utils.api_client import aiohttp_post
from utils.logs.sabangnet_logger import get_logger


logger = get_logger(__name__)


class EcountAuthService:
    """이카운트 인증 서비스"""

    def __init__(self):
        self.test_zone_url = "https://sboapi.ecount.com/OAPI/V2/Zone"
        self.prod_zone_url = "https://oapi.ecount.com/OAPI/V2/Zone"
        self.test_login_base_url = "https://sboapi{}.ecount.com/OAPI/V2/OAPILogin"
        self.prod_login_base_url = "https://oapi{}.ecount.com/OAPI/V2/OAPILogin"
        self.session_timeout = 30  # seconds
    
    async def get_zone_info(self, com_code: str, is_test: bool = True) -> Optional[ZoneResponse]:
        """Zone 정보를 가져옵니다.
        
        Args:
            com_code: 회사 코드
            is_test: 테스트 환경 여부
            
        Returns:
            ZoneResponse: Zone 정보 응답 객체
        """
        zone_request = ZoneRequest(COM_CODE=com_code)
        url = self.test_zone_url if is_test else self.prod_zone_url
        data, status, error = await aiohttp_post(
            url,
            zone_request.model_dump(),
            timeout=self.session_timeout,
            logger=logger
        )
        if status == 200 and data:
            zone_response = ZoneResponse(**data)
            logger.info(f"Zone 정보 조회 성공: {zone_response}")
            return zone_response
        logger.error(f"Zone 정보 조회 실패: {error or status}")
        return None
    
    async def login(self, auth_info: EcountAuthInfo, is_test: bool = True) -> Optional[LoginResponse]:
        """이카운트 로그인을 수행합니다.
        
        Args:
            auth_info: 인증 정보
            is_test: 테스트 환경 여부
            
        Returns:
            LoginResponse: 로그인 응답 객체
        """
        login_request = LoginRequest(
            COM_CODE=auth_info.com_code,
            USER_ID=auth_info.user_id,
            API_CERT_KEY=auth_info.api_cert_key,
            LAN_TYPE="ko-KR",
            ZONE=auth_info.zone
        )
        base_url = self.test_login_base_url if is_test else self.prod_login_base_url
        url = base_url.format(auth_info.zone + auth_info.domain)
        data, status, error = await aiohttp_post(
            url,
            login_request.model_dump(),
            timeout=self.session_timeout,
            logger=logger
        )
        if status == 200 and data:
            login_response = LoginResponse(**data)
            logger.info(f"로그인 성공: {auth_info.user_id}")
            return login_response
        logger.error(f"로그인 실패: {error or status}")
        return None
    
    async def authenticate(
        self,
        com_code: str,
        user_id: str,
        api_cert_key: str,
        is_test: bool = True
    ) -> Tuple[Optional[str], Optional[EcountAuthInfo]]:
        """
        완전한 인증 프로세스를 수행합니다.
        Returns: (session_id, auth_info)
        """
        zone_response = await self.get_zone_info(com_code, is_test)
        if not zone_response or not zone_response.Data:
            logger.error("Zone 정보 조회 실패")
            return None, None
        auth_info = EcountAuthInfo(
            com_code=com_code,
            user_id=user_id,
            api_cert_key=api_cert_key,
            zone=zone_response.Data.ZONE,
            domain=zone_response.Data.DOMAIN
        )
        login_response = await self.login(auth_info, is_test)
        if not login_response or not login_response.Data:
            logger.error("로그인 실패")
            return None, None
        session_id = login_response.Data.Datas.SESSION_ID
        auth_info.session_id = session_id
        logger.info(f"인증 완료: {user_id}, Session: {session_id}")
        return session_id, auth_info
    
    async def authenticate_with_env(
        self, is_test: bool = True
    ) -> Tuple[Optional[str], Optional[EcountAuthInfo]]:
        """
        환경변수를 사용하여 자동 인증을 수행합니다.
        Returns: (session_id, auth_info)
        """
        # 환경변수에서 인증 정보 가져오기
        com_code = SETTINGS.ECOUNT_COM_CODE
        user_id = SETTINGS.ECOUNT_USER_ID  
        zone = SETTINGS.ECOUNT_ZONE
        domain = SETTINGS.ECOUNT_DOMAIN or ""
        if is_test:
            api_cert_key = SETTINGS.ECOUNT_API_TEST
        else:
            api_cert_key = SETTINGS.ECOUNT_API
        
        if not all([com_code, user_id, api_cert_key]):
            logger.error("환경변수에서 이카운트 인증 정보를 찾을 수 없습니다.")
            logger.error(
                f"ECOUNT_COM_CODE: {com_code}, "
                f"ECOUNT_USER_ID: {user_id}, "
                f"ECOUNT_API: {'설정됨' if api_cert_key else '설정되지 않음'}"
            )
            return None, None
        
        # Zone 정보가 환경변수에 있으면 직접 사용, 없으면 조회
        if zone:
            auth_info = EcountAuthInfo(
                com_code=com_code,
                user_id=user_id,
                api_cert_key=api_cert_key,
                zone=zone,
                domain=domain
            )
            login_response = await self.login(auth_info, is_test)
            if not login_response or not login_response.Data:
                logger.error("환경변수 Zone으로 로그인 실패")
                return None, None
            session_id = login_response.Data.Datas.SESSION_ID
            auth_info.session_id = session_id
            logger.info(f"환경변수 인증 완료: {user_id}, Session: {session_id}")
            return session_id, auth_info
        else:
            # Zone 정보 조회 후 인증
            return await self.authenticate(com_code, user_id, api_cert_key, is_test)
    
    async def authenticate_with_env_with_template_code(
        self,
        is_test: bool = True,
        template_code: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[EcountAuthInfo]]:
        """환경변수를 사용하여 자동 인증을 수행합니다.
        
        Args:
            is_test: 테스트 환경 여부
            template_code: 템플릿 코드 (okmart 또는 iyes)
            
        Returns:
            Tuple[Optional[str], Optional[EcountAuthInfo]]: (세션 ID, 인증 정보)
        """
        # template_code가 okmart로 시작하면 okmart 인증, 아니면 iyes 인증
        # template_code가 없으면 error
        if not template_code:
            logger.error("template_code가 없습니다.")
            return None, None
        if template_code.startswith("okmart"):
            return await self.authenticate_with_env(is_test)
        elif template_code.startswith("iyes"):
            com_code = SETTINGS.ECOUNT_COM_CODE_IYES
            user_id = SETTINGS.ECOUNT_USER_ID_IYES
            zone = SETTINGS.ECOUNT_ZONE_IYES
            if is_test:
                api_cert_key = SETTINGS.ECOUNT_API_IYES_TEST
            else:
                api_cert_key = SETTINGS.ECOUNT_API_IYES
        else:
            logger.error("template_code가 올바르지 않습니다.")
            return None, None
        
        if not all([com_code, user_id, api_cert_key]):
            logger.error("환경변수에서 이카운트 인증 정보를 찾을 수 없습니다.")
            logger.error(
                f"ECOUNT_COM_CODE: {com_code}, "
                f"ECOUNT_USER_ID: {user_id}, "
                f"ECOUNT_API: {'설정됨' if api_cert_key else '설정되지 않음'}"
            )
            return None, None
        
        # Zone 정보가 환경변수에 있으면 직접 사용, 없으면 조회
        if zone:
            auth_info = EcountAuthInfo(
                com_code=com_code,
                user_id=user_id,
                api_cert_key=api_cert_key,
                zone=zone,
                domain=""
            )
            login_response = await self.login(auth_info, is_test)
            if not login_response or not login_response.Data:
                logger.error("환경변수 Zone으로 로그인 실패")
                return None, None
            session_id = login_response.Data.Datas.SESSION_ID
            auth_info.session_id = session_id
            logger.info(f"환경변수 인증 완료: {user_id}, Session: {session_id}")
            return session_id, auth_info
        else:
            # Zone 정보 조회 후 인증
            return await self.authenticate(com_code, user_id, api_cert_key, is_test)
    
    async def validate_session(
        self,
        session_id: str,
        auth_info: EcountAuthInfo,
        is_test: bool = True
    ) -> bool:
        """세션의 유효성을 검증합니다.
        
        Args:
            session_id: 세션 ID
            auth_info: 인증 정보
            is_test: 테스트 환경 여부
            
        Returns:
            bool: 세션 유효성 여부
        """
        login_response = await self.login(auth_info, is_test)
        if not login_response or not login_response.Data:
            logger.error("로그인 실패")
            return False
        session_id = login_response.Data.Datas.SESSION_ID
        return session_id is not None and len(session_id) > 0


class EcountAuthManager:
    """이카운트 인증 관리자 (싱글톤 패턴)"""

    _instance = None
    _auth_cache = {}
    auth_service = EcountAuthService()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.auth_service = EcountAuthService()
        return cls._instance
    
    async def get_authenticated_info(
        self,
        com_code: str,
        user_id: str,
        api_cert_key: str,
        is_test: bool = True
    ) -> Optional[EcountAuthInfo]:
        """인증된 정보를 가져옵니다. 캐시를 확인하고 필요시 새로 인증합니다.
        
        Args:
            com_code: 회사 코드
            user_id: 사용자 ID
            api_cert_key: API 인증 키
            is_test: 테스트 환경 여부
            
        Returns:
            Optional[EcountAuthInfo]: 인증 정보
        """
        cache_key = f"{com_code}_{user_id}_{is_test}"
        
        # 캐시 확인
        if cache_key in self._auth_cache:
            auth_info = self._auth_cache[cache_key]
            # 세션 유효성 검증
            if await self.auth_service.validate_session(auth_info.session_id, auth_info, is_test):
                return auth_info
            else:
                # 세션이 만료된 경우 캐시에서 제거
                del self._auth_cache[cache_key]
        
        # 새로 인증
        session_id, auth_info = await self.auth_service.authenticate(com_code, user_id, api_cert_key, is_test)
        if auth_info:
            self._auth_cache[cache_key] = auth_info
            return auth_info
        
        return None
    
    async def get_authenticated_info_from_env(
        self, is_test: bool = True
    ) -> Optional[EcountAuthInfo]:
        """환경변수를 사용하여 인증된 정보를 가져옵니다.
        
        Args:
            is_test: 테스트 환경 여부
            
        Returns:
            Optional[EcountAuthInfo]: 인증 정보
        """
        cache_key = f"env_auth_{is_test}"
        
        # 캐시 확인
        if cache_key in self._auth_cache:
            auth_info = self._auth_cache[cache_key]
            # 세션 유효성 검증
            if await self.auth_service.validate_session(auth_info.session_id, auth_info, is_test):
                return auth_info
            else:
                # 세션이 만료된 경우 캐시에서 제거
                del self._auth_cache[cache_key]
        
        # 환경변수로 새로 인증
        session_id, auth_info = await self.auth_service.authenticate_with_env(is_test)
        if auth_info:
            self._auth_cache[cache_key] = auth_info
            return auth_info
        
        return None
    
    async def get_authenticated_info_from_env_with_template_code(
        self,
        is_test: bool = True,
        template_code: Optional[str] = None
    ) -> Optional[EcountAuthInfo]:
        """환경변수를 사용하여 인증된 정보를 가져옵니다.
        
        Args:
            is_test: 테스트 환경 여부
            template_code: 템플릿 코드 (okmart 또는 iyes)
            
        Returns:
            Optional[EcountAuthInfo]: 인증 정보
        """
        cache_key = f"env_auth_{template_code}_{is_test}"
        
        # 캐시 확인
        if cache_key in self._auth_cache:
            auth_info = self._auth_cache[cache_key]
            # 세션 유효성 검증
            if await self.auth_service.validate_session(auth_info.session_id, auth_info, is_test):
                return auth_info
            else:
                # 세션이 만료된 경우 캐시에서 제거
                del self._auth_cache[cache_key]
        
        # 환경변수로 새로 인증
        session_id, auth_info = await self.auth_service.authenticate_with_env_with_template_code(is_test, template_code)
        if auth_info:
            self._auth_cache[cache_key] = auth_info
            return auth_info
        
        return None
    
    def clear_cache(
        self,
        com_code: Optional[str] = None,
        user_id: Optional[str] = None,
        is_test: Optional[bool] = None
    ):
        """캐시를 클리어합니다.
        
        Args:
            com_code: 회사 코드 (선택사항)
            user_id: 사용자 ID (선택사항)
            is_test: 테스트 환경 여부 (선택사항)
        """
        if com_code and user_id and is_test is not None:
            cache_key = f"{com_code}_{user_id}_{is_test}"
            if cache_key in self._auth_cache:
                del self._auth_cache[cache_key]
        else:
            self._auth_cache.clear()
