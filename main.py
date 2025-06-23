################################################
################################################
################################################
################################################
################### FASTAPI ####################
################################################
################################################
################################################
################################################


import platform
import subprocess
from contextlib import asynccontextmanager


from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.products import router as products_router
from api.product_api import router as product_router


streamlit_process = None

# 앱 시작 시 Streamlit 백그라운드에서 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("startup")
    global streamlit_process
    if platform.system() == "Windows":
        print("Windows")
        streamlit_process = subprocess.Popen("streamlit run ui.py", shell=True)
    else:
        print("Linux | Mac")
        streamlit_process = subprocess.Popen(["streamlit", "run", "ui.py"])
    yield
    print("shutdown")
    if streamlit_process and streamlit_process.poll() is None:
        streamlit_process.terminate()
        streamlit_process.wait()


master_router = APIRouter(
    prefix="/api/v1",
    tags=["api"],
)


app = FastAPI(
    title="SabangNet API <-> n8n 연결 테스트",
    description="SabangNet API <-> n8n 연결 테스트를 위한 테스트 서버",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

master_router.include_router(products_router)


app.include_router(master_router)
app.include_router(product_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    # allow_origins=["*"], # 개발 환경에서는 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return RedirectResponse(url="http://localhost:8501")
