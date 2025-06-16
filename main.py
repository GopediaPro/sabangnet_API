from fastapi import FastAPI, Depends
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


app = FastAPI()

@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    stmt = text("SELECT COUNT(*) FROM receive_order")
    result = await db.execute(stmt)
    print(result.scalar_one())
    return {"message": "Hello World"}