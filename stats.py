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
    logging_config: str

    class Config:
        env_file = ".env"


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


def get_logger():
    return logging.getLogger(__name__)


settings = Settings()
app: FastAPI = FastAPI()

logging.config.fileConfig(settings.logging_config)


def check_for_game(game: int, id: int, db: sqlite3.Connection):
    try:
        cur = db.execute("select exists(SELECT * from games WHERE user_id = ? AND game_id = ? LIMIT 1);", (id, game))
        query = cur.fetchone()[0]
        return query
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


def post_game_service(win:bool, guesses: int, user_id: int, game_id:int, db: sqlite3.Connection):
    try:
        cur = db.execute("INSERT into games (user_id, game_id, guesses, won) VALUES (?, ?, ?,?);",(user_id, game_id,guesses,win))
        db.commit()
        return
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


def update_game_service(win:bool, guesses: int, user_id:int, game_id:int, db: sqlite3.Connection):
    try:
        cur = db.execute("UPDATE games SET guesses = ?, won = ? WHERE user_id = ? AND game_id = ?;", (guesses,win,user_id,game_id))
        db.commit()
        return
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


def get_streaks(user_id: int, db: sqlite3.Connection):
    try:
        maxStreak = 0
        currentStreak = 0
        cur = db.execute("select * from streaks where user_id = ?", [user_id])
        query = cur.fetchall()
        dict = {}
        for row in query:
            if maxStreak < int(row[1]):
                maxStreak = int(row[1])
            currentStreak = int(row[1])
        dict.update({"currentStreak": currentStreak, "maxStreak": maxStreak})
        return dict
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


def get_guesses(user_id:int, db: sqlite3.Connection):
    try:
        cur = db.execute("SELECT * from games WHERE user_id = ? ORDER by games.game_id", [user_id])
        query = cur.fetchall()
        dict = {}
        guesses = {}
        wins = 0
        loses = 0
        winPercentage = 0
        gamesPlayed = 0
        i = 1
        for row in query:
            print(row[0], row[1],row[2],row[3],row[4])
            if int(row[4]) == 0:
                loses = loses + 1
            else:
                wins = wins + 1
                guesses[i] = int(row[3])
                i  = i + 1
            gamesPlayed = gamesPlayed + 1
        winPercentage = int(float(wins/gamesPlayed) * 100)
        guesses.update({"fail": loses})
        dict.update({"guesses": guesses, "winPercentage": winPercentage,"gamesPlayed": gamesPlayed})
        return dict
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": type(e).__name__, "msg": str(e)},
        )


#Posting a win or loss for a particular game, along with a timestamp and number of guesses
@app.post("/stats/")
def post_stats_by_userid(win: bool, guesses: int, user_id: int, game_id: int, db: sqlite3.Connection = Depends(get_db)):
    if check_for_game(game_id, user_id, db):
        update_game_service(win, guesses, user_id, game_id, db)
    else:
        post_game_service(win, guesses, user_id, game_id, db)
    return "game posted";


# top 10 users by number of wins
@app.get("/stats/top10wins")
def get_top10users(
         db: sqlite3.Connection = Depends(get_db)
):
    cur = db.execute("select user_id from wins limit 10")
    rows = cur.fetchall()
    dicts = {}
    i=0
    for row in rows:
        i=i+1
        dicts[i] = row["user_id"]
    return {"Top 10 users by number of wins are": dicts}


# top 10 users by longest streak
@app.get("/stats/top10streaks")
def get_top10streaks(
        db: sqlite3.Connection = Depends(get_db)
):
    cur = db.execute("select user_id from streaks order by streak desc LIMIT 10;")
    rows = cur.fetchall()
    dicts = {}
    i=0
    for row in rows:
        i=i+1
        dicts[i] = row["user_id"]
    return {"Top 10 users by longest streak are": dicts}


#retrieve data for player stats
@app.get("/stats/{id}")
def retrieve_stats(id: int, response: Response, db: sqlite3.Connection = Depends(get_db)):
    results = {}
    streak = get_streaks(id, db)
    guesses = get_guesses(id, db)
    results.update(streak)
    results.update(guesses)
    return results

if __name__ == "__main__":
    uvicorn.run("stats:app", host="0.0.0.0", port=8000, log_level="info")
