import os

import sentry_sdk
import uvicorn
from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.router import timetable
from updater.db import check_for_updates

sentry_sdk.init(dsn=os.environ["SENTRY_URL"])

gbu_agenda = FastAPI()
gbu_agenda.include_router(timetable)
SentryAsgiMiddleware(gbu_agenda)

if __name__ == "__main__":
    check_for_updates()
    uvicorn.run("main:gbu_agenda", port=int(os.getenv("PORT", 5000)), host="0.0.0.0", reload=True)
