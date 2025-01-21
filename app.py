from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request


from routes.chat_agent import router as chat_agent_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "chrome-extension://cndgjnbmicicabbpfpjkbpjhahpendnc",
    "chrome-extension://*",
    "https://feat-cloudflare-build.notex-interface.pages.dev",
    "https://dev.notexapp.com",
    "https://notexapp.com",
    "https://notex-interface.pages.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


v1_router = APIRouter(prefix="/v1")


def my_schema():
    openapi_schema = get_openapi(
        title="RaidenX Bot API",
        version="1.0",
        routes=app.routes,
    )
    openapi_schema["info"] = {
        "title": "RaidenX Bot API",
        "version": "1.0",
        "description": """
        RaidenX Bot - Your Professional Meme Coin Trading Assistant

        Features:
        - Search and get information about tokens/cryptocurrencies
        - View wallet balances and positions
        - Execute buy/sell orders for meme coins
        - Real-time trading assistance with AI-powered recommendations

        The bot specializes in meme coin trading and helps users make informed decisions about their cryptocurrency investments.
        """,
        "contact": {
            "name": "Get Help with RaidenX Bot API",
            "url": "mailto:hung.dang@sotatek.com",
            "email": "hung.dang@sotatek.com",
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = my_schema

@app.get("/", include_in_schema=False,  tags=['docs'])
async def redirect():
    return RedirectResponse("/docs")

v1_router.include_router(chat_agent_router, prefix="/chat", tags=["Chat"])

app.include_router(v1_router)

