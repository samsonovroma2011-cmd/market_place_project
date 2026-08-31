from fastapi import FastAPI
import uvicorn

from src.api.products import router as products_router


app = FastAPI()

app.include_router(products_router)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", reload=True)