import json
from typing import Optional
from fastapi import FastAPI,HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

class UserInDB(User):
    hashed_password: str

with open("menu.json", "r") as read_file:
    data = json.load(read_file)

app = FastAPI()

def fake_hash_password(password: str):
    return "fakehashed" + password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/")
async def root():
    return "You are accessing root node, Hello."

#Get Menu based on ID
@app.get("/menu/{item_id}")
async def read_menu(item_id: int):

    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item

    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )

@app.get("/menu/")
async def get_all():

    return data['menu']

#Post Menu (Add New Menu Item)
@app.post("/menu/{item}")
async def add_menu(item : str):
    menu_item = {}
    item_id = data['menu'][len(data['menu']) - 1]["id"] + 1
    menu_item["id"] = item_id
    menu_item["name"] = item
    data['menu'].append(menu_item)

    #read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4, sort_keys=False)
        return menu_item

    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

#Update Menu Item
@app.put("/menu/")
async def update_item(item_id: int, item_name: str):
    found = False
    i = 0
    while (not found) and (i < len(data['menu'])):
        if(data['menu'][i]["id"] == item_id):
            found = True
        i = i + 1
    
    if found:
        data['menu'][item_id-1]["name"] = item_name
        with open("menu.json", "w") as write_file:
            json.dump(data, write_file, indent=4, sort_keys=False)
        return data['menu']

    # else:
    #     return "not found"
    
    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )

#Delete
@app.delete("/menu/")
async def delete_item(item_id: int):
    new_data = {}
    new_menu = []
    found = False
    for menu_item in data['menu']:
        if menu_item['id'] != item_id:
            new_menu.append(menu_item)
        else:
            found = True
    
    new_data["menu"] = new_menu
    if found:
        with open("menu.json", "w") as write_file:
            json.dump(new_data, write_file, indent=4, sort_keys=False)
        return new_menu
    
    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )