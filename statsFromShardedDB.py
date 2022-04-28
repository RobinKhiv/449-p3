# Science Fiction Novel API - FastAPI Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#


import contextlib
import logging.config
import sqlite3

import operator
import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseSettings, BaseModel


class Settings(BaseSettings):
    database: str
    shard1: str
    shard2: str
    shard3: str
    shard4: str
    logging_config: str

    class Config:
        env_file = ".env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_shard1():
    with contextlib.closing(sqlite3.connect(settings.shard1)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_shard2():
    with contextlib.closing(sqlite3.connect(settings.shard2)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_shard3():
    with contextlib.closing(sqlite3.connect(settings.shard3)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app = FastAPI()
#app = FastAPI(root_path="/api/v1")

logging.config.fileConfig(settings.logging_config)
def get_top10usersFromShard1(
         db: sqlite3.Connection = Depends(get_shard1)
):
    cur = db.execute("select user_id,wins from wins limit 10")
    rows = cur.fetchall()
    dicts = {}
    print(rows)
    for row in rows:
        dicts[row["user_id"]] = row["wins"]
    return dicts


def get_top10usersFromShard2(
            db: sqlite3.Connection = Depends(get_shard2)
):
    cur = db.execute("select user_id,wins from wins limit 10")
    rows = cur.fetchall()
    dicts = {}
    print(rows)
    for row in rows:
        dicts[row["user_id"]] = row["wins"]
    return dicts


def get_top10usersFromShard3(
         db: sqlite3.Connection = Depends(get_shard3)
):
    cur = db.execute("select user_id,wins from wins limit 10")
    rows = cur.fetchall()
    dicts = {}
    print(rows)
    for row in rows:
        dicts[row["user_id"]] = row["wins"]
    return dicts

# top 10 users by number of wins
@app.get("/stats/top10wins")
def get_top10users(db1: sqlite3.Connection = Depends(get_shard1),db2: sqlite3.Connection = Depends(get_shard2),db3: sqlite3.Connection = Depends(get_shard3)):
    dicts_4=get_top10usersFromShard1(db1)|get_top10usersFromShard2(db2)|get_top10usersFromShard3(db3)
    sorted_d = sorted(dicts_4.items(), key = lambda x: x[1],reverse=True)
    return {"Top 10 users by number of wins are": sorted_d}



if __name__ == "__main__":
    uvicorn.run("statsFromShardedDB:app", host="0.0.0.0", port=8001, log_level="info")
