from fastapi import FastAPI, Body
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from datetime import datetime, date, time, timezone
import json

def calc_time():
    dt = datetime.now()
    time_stamp = dt.timestamp()
    date_time = datetime.fromtimestamp(time_stamp)
    real_time = date_time.strftime('%m/%d/%y at %H:%M')
    return real_time

app = FastAPI()

class Entry(BaseModel):
    title: str
    message: str
    is_completed: bool

to_do_list = []

@app.get("/")
async def get_root():
    return {"message": "This is a to-do list"}


@app.get("/whole-list")
async def return_whole_list():
    with open("/Users/shaypherashe/stuff/blarg/rest_api_project.txt", "r") as reader:
        return str(reader.read())
    

@app.get("/list-entry/{title}")
async def return_single_entry(title: str):
    for entry in to_do_list:
        if entry["title"] == title:
            return entry
        
        
@app.post("/add-to-do")
async def add_list_item(new_item: Entry):
    to_do_entry_dict = new_item.model_dump()
    to_do_entry_dict.update({"Created": calc_time()})
    to_do_list.append(to_do_entry_dict)
    with open("/Users/shaypherashe/stuff/blarg/rest_api_project.txt", "a") as writer:
        writer.write(str(to_do_entry_dict) + "\n")
            

@app.delete("/remove-to-do/{title}")
async def remove_list_item(title: str, remove_entry = Body()):
    with open("/Users/shaypherashe/stuff/blarg/rest_api_project.txt", "r") as reader:
        entries = reader.readlines()
    with open("/Users/shaypherashe/stuff/blarg/rest_api_project.txt", "w") as remover:
        for entry in entries:
            if entry.find("COMPLETED") == -1:
                remover.write(entry)
    

@app.put("/list-entry/update/{title}")
async def update_list_item(title: str, updated_entry: Entry):
    to_do_entry_dict = updated_entry.model_dump()
    to_do_entry_dict.update({"Completed": calc_time()})
    to_do_list.append(to_do_entry_dict)
    print(to_do_entry_dict)
    with open("/Users/shaypherashe/stuff/blarg/rest_api_project.txt", "a") as updater:
        updater.write(str(to_do_entry_dict) + "\n")