import os
import textwrap
from pathlib import Path


class LegacySSLHandler:
    """
    프로세스 종속적인 레거시 SSL 설정파일 변경.
    """
    def __init__(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.cnf_path = self.config_dir / "openssl.cnf"
        # 파일 내용 정의 및 저장
        self.openssl_config = textwrap.dedent("""\
            openssl_conf = openssl_init
                                              
            [openssl_init]
            ssl_conf = ssl_sect

            [ssl_sect]
            system_default = system_default_sect

            [system_default_sect]
            Options = UnsafeLegacyRenegotiation
        """)

    # 환경변수 OPENSSL_CONF 등록
    def fix_legacy_ssl_config(self):
        self.cnf_path.write_text(self.openssl_config, encoding='utf-8')
        os.environ["OPENSSL_CONF"] = str(self.cnf_path.resolve())