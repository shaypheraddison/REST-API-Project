from fastapi import FastAPI, Body, HTTPException
from typing import Optional
import json
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import random 

path = Path("./to-do-list.json")
app = FastAPI()

if not path.is_file():
    with open(path, "w") as writer:
        writer.write("[\n\t\n]")

class To_Do(BaseModel):
    id: Optional[str] | None = None
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
async def get_to_do():
    with open(path, "r") as reader:
       return json.loads(reader.read())
    

@app.post("/to-do")
async def post_entry(new_entry: To_Do):

    # create new entry for to-do list
    to_do_entry_dict = new_entry.model_dump()
    to_do_entry_dict.update({"id": gen_rando_id()})
    to_do_entry_dict.update({"Created": calc_timestamp()})

    # read the file to obatin the needed data
    # loads is used to go from JSON to Python
    with open(path, "r") as reader:
        data = json.loads(reader.read())

    # reference data retrieved from read method above and have it stored in data variable
    # append the list, data var, with the new post entry 
    data.append(to_do_entry_dict)
    
    # open the file as a writer to re-write all of the data to the file
    # dumps is used to go from Python to JSON
    with open(path, "w") as writer:
        writer.write(json.dumps(data, indent=4))
    return to_do_entry_dict
    

@app.get("/to-do/{id}")
async def get_single_to_to(id: str):
    with open(path, "r") as reader:
        to_do_items = json.loads(reader.read())

        for item in to_do_items:
            if item["id"] == id:
                return item
            
        raise HTTPException(status_code=404, detail="Item not found")
                
        
@app.put("/to-do/{id}")
async def update_to_do(id: str, updated_entry: To_Do):
    # getting data entered in from endpoint, adding in the ID of the endpoint to data and adding completed timestamp
    to_do_entry_dict = updated_entry.model_dump()
    to_do_entry_dict["id"] = id
    to_do_entry_dict.update({"Completed": calc_timestamp()})

    # loading the JSON file as a python document and reading the data into a reference-able variable
    with open(path, "r") as reader:
        to_do_items = json.loads(reader.read())

    # iterating through all of the items to find specific ID entered in endpoint and updating the data with entered info
    # break is used to stop the loop immediately after the item is found and updated 
    for item in to_do_items:
        if item["id"] == id:
            item.update(to_do_entry_dict)
            break
    # raise a 404 error in case ID is entered in url and cannot be found
    else:
        raise HTTPException (status_code=404, detail="Item not found")

    # opening file as a writer to truncate all of the data with the updated information
    # dumps python data back into the JSON file and the .dumps converts everything 
    with open(path, "w") as writer:
        writer.write(json.dumps(to_do_items, indent=4))
    
    # returns this message when item has been updated successfully
    return {"message": "Item has been successfully updated"}


@app.delete("/to-do/{id}")
async def delete_to_do(id: str):
    # view data as read only
    with open(path, "r") as reader:
        to_do_items = json.loads(reader.read())

    # iterate through each object and search for ID entered in URL.
    # once ID is found it removes it from the list and immediately stops the loop with the break
    for item in to_do_items:
        if item["id"] == id:
            to_do_items.remove(item)
            break
    # status code 404 raised if ID cannot be found from file
    else:
        raise HTTPException (status_code=404, detail="Item not found")

    # opens file as a writer to truncate the data removed and dumps in the JSON data back to the file
    with open(path, "w") as writer:
        writer.write(json.dumps(to_do_items, indent=4))

    # returns the message when item has been successfully deleted
    return {"message": "Item has been successfully deleted."}
