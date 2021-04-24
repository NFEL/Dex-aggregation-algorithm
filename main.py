from typing import Optional

from fastapi import FastAPI
from utils import Redis, PathFinder, Schema

app = FastAPI()


@app.on_event('startup')
async def sync():
    await Redis.sync_pairs()


@app.post("/path")
async def where_to_go(request: Schema.RequestPath):
    return PathFinder.find(request)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
