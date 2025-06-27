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


from fastapi.responses import RedirectResponse
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.products import router as products_router
from api.product_registration_api import router as product_registration_router



# 앱 시작 시 Streamlit 백그라운드에서 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 서버 시작 전 작업영역
    yield
    # FastAPI 서버 종료 후 작업영역


master_router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
)


app = FastAPI(
    title="SabangNet API <-> n8n 연결 테스트",
    description="SabangNet API <-> n8n 연결 테스트를 위한 테스트 서버",
    version="0.1.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# API 프리픽스 라우터
master_router.include_router(products_router)


app.include_router(master_router)
app.include_router(product_registration_router)
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
