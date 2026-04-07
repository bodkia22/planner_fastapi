from fastapi import FastAPI
from routers.tasks import router

app = FastAPI()
app.include_router(router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
