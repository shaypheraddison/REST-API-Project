from fastapi import FastAPI, Body, HTTPException
from typing import Optional
import json
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import random 
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password0123",
    database="to_do_items"
)
mycursor = mydb.cursor()
mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {mydb.database}")

app = FastAPI()

class To_Do(BaseModel):
    id: Optional[str] | None = None
    category: str
    title: str
    message: str
    is_completed: bool

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def gen_rando_id():
    random_id = (''.join(random.choices(letters, k=2) + random.choices(numbers, k=2)))
    return random_id

def calc_timestamp():
    dt = datetime.now()
    time_stamp = dt.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    real_time = date_time.strftime('%m/%d/%y at %H:%M')
    return real_time

@app.get("/to-do")
async def get_all_to_do():
    mycursor.execute("SELECT * FROM things_to_do")
    things_to_do = mycursor.fetchall()

    for thing in things_to_do:
        return thing
    
    mycursor.close

@app.get("/to-do")
async def get_certain_to_do(id: Optional[str] | None=None, category: Optional[str] | None=None, title: Optional[str] | None=None, is_completed: Optional[bool] | None=None):
    mycursor.execute("SELECT * FROM things_to_do")
    things_to_do = mycursor.fetchall()

    new_list = []
    for thing in things_to_do:
        if thing["id"] == id:
            new_list.append(thing)
        elif thing["category"] == category:
            new_list.append(thing)
        elif thing["title"] == title:
            new_list.append(thing)
        elif thing["is_completed"] == is_completed:
            new_list.append(thing)
    
    if not any ((id, category, title, is_completed)):
        return things_to_do
    
    return new_list
 
@app.post("/to-do")
async def post_entry(new_entry: To_Do):

    to_do_entry_dict = new_entry.model_dump()
    to_do_entry_dict.update({"id": gen_rando_id()})
    to_do_entry_dict.update({"Created": calc_timestamp()})

    with open(path, "r") as reader:
        data = json.loads(reader.read())
 
    data.append(to_do_entry_dict)

    with open(path, "w") as writer:
        writer.write(json.dumps(data, indent=4))
    return to_do_entry_dict
    

@app.delete("/to-do")
async def delete_to_do(id: Optional[str] | None=None, category: Optional[str] | None=None, title: Optional[str] | None=None, is_completed: Optional[bool] | None=None):

    with open(path, "r") as reader:
        to_do_items = json.loads(reader.read())

    new_items = []
    for item in to_do_items:
        if item and item["id"] == id:
            continue
        elif category and item["category"] == category:
            continue
        elif title and item["title"] == title:
            continue
        elif is_completed is not None and item["is_completed"] == is_completed:
            continue
        else:
            new_items.append(item)
   
    if not new_items:
        raise HTTPException (status_code=404, detail="Item not found")

    with open(path, "w") as writer:
        writer.write(json.dumps(new_items, indent=4))

    return {"message": "Deletion completed."}


@app.get("/to-do/{id}")
async def get_single_to_to(id: str):
    mycursor.execute("SELECT * FROM things_to_do")
    things_to_do = mycursor.fetchall()

    for thing in things_to_do:
        if thing["id"] == id:
            return thing
            
            
@app.put("/to-do/{id}")
async def update_to_do(id: str, updated_entry: To_Do):

    to_do_entry_dict = updated_entry.model_dump()
    to_do_entry_dict["id"] = id
    to_do_entry_dict.update({"Completed": calc_timestamp()})

    with open(path, "r") as reader:
        to_do_items = json.loads(reader.read())
    
    for item in to_do_items:
        if item["id"] == id:
            item.update(to_do_entry_dict)
            break
    
    else:
        raise HTTPException (status_code=404, detail="Item not found")

    with open(path, "w") as writer:
        writer.write(json.dumps(to_do_items, indent=4))
    
    return {"message": "Item has been successfully updated"}
