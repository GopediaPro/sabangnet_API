################################################
################################################
################################################
################################################
################### FASTAPI ####################
################################################
################################################
################################################
################################################


from fastapi import FastAPI, APIRouter
from api.product_api import router as product_router


app = FastAPI(
    title="SabangNet API <-> n8n 연결 테스트",
    description="SabangNet API <-> n8n 연결 테스트를 위한 테스트 서버",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}

# API router 연결
app.include_router(router)
app.include_router(product_router)
