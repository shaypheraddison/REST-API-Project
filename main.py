from fastapi import FastAPI, Body
from typing import Optional
import json
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import random 

path = Path("./to-do-list.json")
app = FastAPI()

if path.is_file() == False:
    with open(path, "a+") as writer:
        writer.write("")
else:
    with open(path, "a+") as editor:
        editor.read()

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def gen_rando_id():
    random_id = (''.join(random.choices(letters, k=2) + random.choices(numbers, k=2)))
    return random_id

class To_Do(BaseModel):
    id: Optional[str] | None = None
    title: str
    message: str
    is_completed: bool

def calc_timestamp():
    dt = datetime.now()
    time_stamp = dt.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    real_time = date_time.strftime('%m/%d/%y at %H:%M')
    return real_time

@app.get("/to-do")
async def get_to_do():
    with open(path, "r") as reader:
       return reader.read()

@app.post("/to-do")
async def post_entry(new_entry: To_Do):
    to_do_entry_dict = new_entry.model_dump()
    to_do_entry_dict.update({"id": gen_rando_id()})
    to_do_entry_dict.update({"Created": calc_timestamp()})
    with open(path, "a+") as editor:
        editor.write(json.dumps(to_do_entry_dict, indent=3))




"""
GET - @app.get("/to-do")
GET - @app.get("/to-do/{title}")
POST - @app.post("/to-do")
PUT - @app.put("/to-do/{title}")
DELETE - @app.delete("/to-do/{title}")
"""

