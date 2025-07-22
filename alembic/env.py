import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. 프로젝트 루트 경로를 sys.path에 추가 (core, models import를 위해)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. settings import 및 DB URL 구성
from core.settings import SETTINGS

# Alembic은 동기 드라이버(psycopg2) 사용
DATABASE_URL = (
    f"postgresql+psycopg2://{SETTINGS.DB_USER}:{SETTINGS.DB_PASSWORD}"
    f"@{SETTINGS.DB_HOST}:{SETTINGS.DB_PORT}/{SETTINGS.DB_NAME}"
)

# 3. Alembic config 객체에 DB URL 주입
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 4. 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 5. SQLAlchemy 모델 import 및 metadata 지정
import models
from models.base_model import Base  # Base.metadata 사용

target_metadata = Base.metadata

# 6. (Alembic 기본 코드) 오프라인/온라인 마이그레이션 함수
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
