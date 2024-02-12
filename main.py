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
    passwd="password0123"
)
mycursor = mydb.cursor()
mycursor.execute(f"CREATE DATABASE IF NOT EXISTS to_do_items")
mycursor.execute("USE to_do_items")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS things_to_do (
                 id VARCHAR(4) PRIMARY KEY NOT NULL, 
                 category VARCHAR(20) NOT NULL, 
                 title VARCHAR(20) NOT NULL, 
                 message VARCHAR(255) NOT NULL, 
                 is_completed VARCHAR(5), 
                 created_timestamp DATETIME, 
                 completed_timestamp DATETIME
    )
""")
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
    is_completed: str

@app.get("/to-do")
async def get_certain_to_do(id: Optional[str] | None=None, category: Optional[str] | None=None, title: Optional[str] | None=None, is_completed: Optional[str] | None=None):
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
    
    if not new_list:
        raise HTTPException(status_code=404, detail="Query could not be populated")

    return new_list


@app.post("/to-do")
async def post_entry(new_entry: To_Do):
    sql_query = ("INSERT INTO things_to_do (id, category, title, message, is_completed, created_timestamp) VALUES (%s, %s, %s, %s, %s, %s)")
    mycursor.execute(
        sql_query,
        (
            gen_rando_id(), 
            new_entry.category, 
            new_entry.title,
            new_entry.message,
            new_entry.is_completed,
            calc_timestamp()
        )
    )
    mydb.commit()
    return new_entry

@app.delete("/to-do")
async def delete_to_do(id: Optional[str] | None=None, category: Optional[str] | None=None, title: Optional[str] | None=None, is_completed: Optional[str] | None=None):
    sql_query = "DELETE FROM things_to_do WHERE id = %s OR category = %s or is_completed = %s OR title = %s"
    mycursor.execute(sql_query, (id, category, is_completed, title))
    mydb.commit()

    if not any ((id, category, title, is_completed)):
        raise HTTPException(status_code=404, detail="Item cannot be found")

    return "Deletion Completed."


@app.get("/to-do/{id}")
async def get_single_to_to(id: str):
    mycursor.execute("SELECT * FROM things_to_do WHERE id = %s", (id,))
    thing = mycursor.fetchone()

    if thing:
        return {
            "id": thing[0], 
            "category": thing[1], 
            "title": thing[2], 
            "message": thing[3], 
            "is_completed": thing[4], 
            "created_timestamp": thing[5], 
            "completed_timestamp": thing[6]
            }
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    
            
@app.put("/to-do/{id}")
async def update_to_do(id: str, updated_entry: To_Do):
    sql_query = "UPDATE things_to_do SET category = %s, title = %s, message = %s, is_completed = %s, completed_timestamp = %s WHERE id = %s"
    mycursor.execute(
        sql_query, 
        (
            updated_entry.category, 
            updated_entry.title, 
            updated_entry.message, 
            updated_entry.is_completed, 
            calc_timestamp(), 
            id
        )
    )
    mydb.commit()

    if not id:
        raise HTTPException(status_code=404, detail="Item could not be found")

    return updated_entry