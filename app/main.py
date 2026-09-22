from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.api.chat_router import router as chat_router
from app.api.profile import router as profile_router
from app.product.product_router import router as product_router

from app.auth.auth_router import router as auth_router
from app.core.config import settings

app = FastAPI()


@app.on_event("startup")
async def validate_configuration() -> None:
    settings.validate()


app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(product_router)
app.include_router(profile_router)
app.mount("/ui", StaticFiles(directory="app/static/chatbot", html=True), name="ui")


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/ui")
