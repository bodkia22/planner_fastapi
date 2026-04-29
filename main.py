from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.tasks import router
from routers.auth import router as auth_router
from routers.assistant import router as assistance_router
from routers.conversation import router as conversation_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(assistance_router)
app.include_router(conversation_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
