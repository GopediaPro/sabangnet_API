################################################
################################################
################################################
################################################
################### FASTAPI ####################
################################################
################################################
################################################
################################################


from contextlib import asynccontextmanager


from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.products import router as products_router
from api.v1.endpoints.mall_price import router as mall_price_router
from utils.sabangnet_logger import get_logger, HTTPLoggingMiddleware
from api.v1.endpoints.one_one_price import router as one_one_price_router
from api.v1.endpoints.db_xml import router as db_xml_router
from api.product_registration_api import router as product_registration_router


logger = get_logger(__name__)


# 앱 시작 시 사전 작업 정의용 데코레이터
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 서버 시작 전 작업영역
    yield
    # FastAPI 서버 종료 후 작업영역


# 메인 라우터
master_router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
)


app = FastAPI(
    title="SabangNet API <-> n8n 연결 테스트",
    description="SabangNet API <-> n8n 연결 테스트를 위한 테스트 서버",
    version="0.1.2",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# API 프리픽스 라우터
master_router.include_router(products_router)
master_router.include_router(mall_price_router)
master_router.include_router(one_one_price_router)
master_router.include_router(db_xml_router)


app.include_router(master_router)
app.include_router(product_registration_router)

# HTTP 로깅 미들웨어 추가 (CORS보다 먼저)
app.add_middleware(HTTPLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
def root() -> str:
    return "FastAPI 메인페이지 입니다."
