import contextlib
import logging.config
from mimetypes import guess_extension
import sqlite3
import winsound


import uvicorn
from fastapi import FastAPI, Depends, Response, HTTPException, status
from pydantic import BaseSettings, BaseModel

class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = ".env" 

class Stats(BaseModel):
    currentStreak: int
    maxStreak: int
    guesses: {}
    winpercent: float
    played: int
    wins: int
    averageguesses: int


def get_db():
    with contextlib.closing(sqlite3.connect(settings.word_database)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_logger():
    return logging.getLogger(__name__)


    
       
#retrieve data for player stats 
@app.get("/stats/{id}")
def retrieve_stats(id: int, response: Response, db: sqlite3.Connection = Depends(get_db)):

cur = db.execute("SELECT * FROM games WHERE id = ? LIMIT 1", [id])
stats = cur.fetchall()

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stats for the user not found"
        )
    return {'currentstreak': currentStreak,
            'maxstreak': maxStreak,
            'guesses' :{},
            'game_won': winpercent,
            'games_played': played,
            'won':wins,
            'average_guesses':averageguesses}


#posting wins and losses for the game.
@app.post("/stats/wins")
def get_wins(db: sqlite3.Connection = Depends(get_db)):
  cur = db.execute("select user_id, count from games;")
  rows = cur.fetchall()
  if (wins > 0 == True):
    played = wins + loses
    winpercent= ((wins/played) *100)
    currentStreak= currentStreak+ 1
   

  return {wins, winpercent, currentStreak}


#posting Guesses
@app.get("/stats/guesses")
def get_gusses(db:sqlite3.connection = Depends(get_db)):
    try:
        data=[user_id,game_id]
        cur = db.execute("SELECT guesses FROM games WHERE user_id=(?) AND game_id=(?)",data)
        rows = cur.fetchall()
        return rows
    except Exeption as e:
        return e


def updatestats( word: str, response: Response, db: sqlite3.Connection = Depends(get_db)):

    played= document.getElementById('total-played')
    wins= document.getElementById('game_won') 
    winpercent= document.getElementById('win%')
    currentStreak= document.getElementById('current_streak')
    averageguess= document.getElementByID('average_guesses')




 
    
        
      