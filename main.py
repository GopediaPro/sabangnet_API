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


from fastapi.responses import RedirectResponse
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.products import router as products_router
from api.product_api import router as product_router


streamlit_process = None

# 앱 시작 시 Streamlit 백그라운드에서 실행
@asynccontextmanager
async def lifespan(app: FastAPI):
    global streamlit_process
    if platform.system() == "Windows":
        streamlit_process = subprocess.Popen("streamlit run ui.py --server.address 0.0.0.0 --server.port 8501", shell=True)
    else:
        streamlit_process = subprocess.Popen(["streamlit", "run", "ui.py", "--server.address", "0.0.0.0", "--server.port", "8501"])

    yield
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
    allow_origins=[
        "http://mhd.hopto.org:8501",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
def root(request: Request):
    # 요청한 호스트와 같은 주소로 Streamlit 주소 동적 생성
    host = request.url.hostname
    return RedirectResponse(url=f"http://{host}:8501")