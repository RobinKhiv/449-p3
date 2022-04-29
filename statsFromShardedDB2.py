# Science Fiction Novel API - FastAPI Edition
#
# Adapted from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#


import contextlib
import logging.config
import sqlite3

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


def get_shard4():
    with contextlib.closing(sqlite3.connect(settings.shard4)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
# Uncomment below line to test without traefik
app = FastAPI()
logging.info(app.docs_url)
# Uncomment below line to test with traefik
# app = FastAPI(root_path="/api/v1")

logging.config.fileConfig(settings.logging_config)


# common function to get records based on user wins
def get_top10WinRecords(
        db: sqlite3.Connection
):
    try:
        cur = db.execute("select user_id,wins from wins limit 10")
        rows = cur.fetchall()
        dicts = {}
        print(rows)
        for row in rows:
            dicts[row["user_id"]] = row["wins"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"information not available"}
        )
    return dicts

# get top10 records for user wins from shard1
def get_top10usersFromShard1(
        db: sqlite3.Connection = Depends(get_shard1)
):
    return get_top10WinRecords(db)


# get top10 records for user wins from shard2
def get_top10usersFromShard2(
        db: sqlite3.Connection = Depends(get_shard2)
):
    return get_top10WinRecords(db)


# get top10 records for user wins from shard3
def get_top10usersFromShard3(
        db: sqlite3.Connection = Depends(get_shard3)
):
    return get_top10WinRecords(db)


# get top10 records for user wins from all the sharded databases,combine the records
# then get the final top 10 users by number of wins from the combined records
@app.get("/stats/top10wins")
def get_top10users(db1: sqlite3.Connection = Depends(get_shard1), db2: sqlite3.Connection = Depends(get_shard2),
                   db3: sqlite3.Connection = Depends(get_shard3)):
    logging.info("inside third instance-getting top10wins")
    combined_records = get_top10usersFromShard1(db1) | get_top10usersFromShard2(db2) | get_top10usersFromShard3(db3)
    sorted_dict = sorted(combined_records.items(), key=lambda x: x[1], reverse=True)
    win_list = []
    top10_initial_dict = {}
    top10_final_dict = {}
    top10_initial_dict.update(sorted_dict)
    for key, val in top10_initial_dict.items():
        win_list.append([key, val])
    for x in range(0, 10):
        top10_final_dict[x] = win_list[x].__getitem__(0)
    return {"Top 10 users by number of wins are": top10_final_dict}


# common function to get records based on user streaks
def get_top10StreakRecords(
        db: sqlite3.Connection
):
    try:
        cur = db.execute("select user_id,streak from streaks order by streak desc LIMIT 10")
        rows = cur.fetchall()
        dicts = {}
        print(rows)
        for row in rows:
            dicts[row["user_id"]] = row["streak"]
    except Exception as e:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"information not available"}
        )
    return dicts
# get top10 records for streaks from shard1
def get_top10streaksFromShard1(
        db: sqlite3.Connection = Depends(get_shard1)
):
    return get_top10StreakRecords(db)


# get top10 records for streaks from shard2
def get_top10streaksFromShard2(
        db: sqlite3.Connection = Depends(get_shard2)
):
    return get_top10StreakRecords(db)


# get top10 records for streaks from shard3
def get_top10streaksFromShard3(
        db: sqlite3.Connection = Depends(get_shard3)
):
    return get_top10StreakRecords(db)


# get top10 records for streaks from all the sharded databases,combine the records
# then get the final top 10 users by streaks from the combined records
@app.get("/stats/top10streaks")
def get_top10streaks(
        db1: sqlite3.Connection = Depends(get_shard1), db2: sqlite3.Connection = Depends(get_shard2),
        db3: sqlite3.Connection = Depends(get_shard3)
):
    logging.info("inside third instance-getting top10streaks")
    combined_records = get_top10streaksFromShard1(db1) | get_top10streaksFromShard2(db2) | get_top10streaksFromShard3(
        db3)
    sorted_dict = sorted(combined_records.items(), key=lambda x: x[1], reverse=True)
    streaks_list = []
    top10_initial_dict = {}
    top10_final_dict = {}
    top10_initial_dict.update(sorted_dict)
    for key, val in top10_initial_dict.items():
        streaks_list.append([key, val])
    for x in range(0, 10):
        top10_final_dict[x] = streaks_list[x].__getitem__(0)
    return {"Top 10 users by longest streak are": top10_final_dict}


if __name__ == "__main__":
    uvicorn.run("statsFromShardedDB2:app", host="0.0.0.0", port=5003, log_level="info")
