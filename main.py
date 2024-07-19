from pathlib import Path
import pickle
from typing import Annotated, Callable

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, requests, status
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

import uvicorn

from src.models.models import User
from src.database.db import get_db
from src.conf.config import config
from src.routes import auth, users
from src.services.auth import auth_service
from src.conf import messages


# start = True

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware("http")
# async def test(requests: Request, call_next: Callable):
#     # token: Annotated[str, Depends(auth_service.oauth2_scheme)],
#     global start
#     if start:
#         print("Something")
#         start = False
#     else:
#         ban_tocken = auth_service.cache.get("ban_token")
#         if ban_tocken is not None:
#             print(ban_tocken)
#             logout_user = auth_service.cache.get(user.username)
#             print(token)
#             if logout_user:
#                 logout_user = pickle.loads(logout_user)
#                 print(logout_user)
#                 if logout_user == token:
#                     return JSONResponse(
#                         status_code=status.HTTP_403_FORBIDDEN,
#                         content={"detail": messages.LOGOUT},
#                     )
#     response = await call_next(requests)
#     return response

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# static_directory = BASE_DIR.joinpath("src").joinpath("static")
static_directory = BASE_DIR.joinpath("templates").joinpath("css")
app.mount("/css", StaticFiles(directory=static_directory), name="css")

static_directory = BASE_DIR.joinpath("templates").joinpath("js")
app.mount("/js", StaticFiles(directory=static_directory), name="js")

static_directory = BASE_DIR.joinpath("docs")
app.mount("/docs", StaticFiles(directory=static_directory), name="docs")

image_directory = BASE_DIR.joinpath("templates").joinpath("img")
app.mount("/img", StaticFiles(directory=image_directory), name="image")

app.mount("/static", StaticFiles(directory=BASE_DIR / "src" / "static"), name="static")

app.include_router(auth.auth_router, prefix="/api")
app.include_router(users.router, prefix="/api")


# @app.get("/")
# async def read_root(request: Request):
#     """
#     The greeting message.
#     """
#     return templates.TemplateResponse(
#         name="index.html",
#         context={
#             "request": request,
#             "welcome": f"Welcome!",
#             "message": f"This is Imagine from _magic",
#             "about_app": "REST API",
#         },
#     )


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If it doesn't, then we know something is wrong with our connection to the database.

    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary with a message key and value
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Database 'Imagine' is healthy"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
