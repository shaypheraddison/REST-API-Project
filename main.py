from fastapi import FastAPI, Body, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import random 
import mysql.connector
from mysql.connector import MySQLConnection

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password0123",
    database="to_do_items"
)
mycursor = mydb.cursor()
mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {mydb.database}")
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS things_to_do (id VARCHAR(4), category VARCHAR(20), title VARCHAR(20), message VARCHAR(255), is_completed BOOLEAN, created_timestamp DATETIME, completed_timestamp TIMESTAMP)"
    )
mycursor.execute("SET SQL_MODE='ALLOW_INVALID_DATES';")

app = FastAPI()

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def gen_rando_id():
    random_id = (''.join(random.choices(letters, k=2) + random.choices(numbers, k=2)))
    return random_id

def calc_timestamp():
    dt = datetime.now()
    time_stamp = dt.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    real_time = date_time.strftime('%y/%m/%d %H:%M:%S')
    return real_time

class To_Do(BaseModel):
    id: Optional[str] | None = None
    category: str
    title: str
    message: str
    is_completed: bool

# @app.get("/to-do")
# async def get_all_to_do():
#     mycursor.execute("SELECT * FROM things_to_do")
#     things_to_do = mycursor.fetchall()

#     return things_to_do

@app.get("/to-do")
async def get_certain_to_do(id: Optional[str] | None=None, category: Optional[str] | None=None, title: Optional[str] | None=None, is_completed: Optional[bool] | None=None):
    mycursor.execute("SELECT * FROM things_to_do")
    things_to_do = mycursor.fetchall()

    new_list = []
    for thing in things_to_do:
        if id and thing[0] == id:
            new_list.append(thing)
        elif category and thing[1] == category:
            new_list.append(thing)
        elif title and thing[2] == title:
            new_list.append(thing)
        elif is_completed is not None and thing[4] == is_completed:
            new_list.append(thing)
    
    if not any ((id, category, title, is_completed)):
        return things_to_do

    return new_list


@app.post("/to-do")
async def post_entry(new_entry: To_Do):
    sql_query = (f"INSERT INTO things_to_do (id, category, title, message, is_completed, created_timestamp) VALUES (%s, %s, %s, %s, False, %s)")
    mycursor.execute(
        sql_query, 
        (gen_rando_id(), 
        new_entry.category, 
        new_entry.title,
        new_entry.message,
        calc_timestamp())
    )
    mydb.commit()
    return new_entry

@app.delete("/to-do")
async def delete_to_do(id: Optional[str] | None=None, category: Optional[str] | None=None, title: Optional[str] | None=None, is_completed: Optional[bool] | None=None):

    with open(path, "r") as reader:
        to_do_items = json.loads(reader.read())

    new_items = []
    for item in to_do_items:
        if item and item[0] == id:
            continue
        elif category and item[1] == category:
            continue
        elif title and item[2] == title:
            continue
        elif is_completed is not None and item[4] == is_completed:
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
        if thing[0] == id:
            return thing
    mycursor.close()
            
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
