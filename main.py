from fastapi import FastAPI
from routers.tasks import router
from routers.auth import router as auth_router

app = FastAPI()

app.include_router(router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
