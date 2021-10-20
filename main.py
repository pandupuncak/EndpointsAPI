import json
from typing import Optional
from fastapi import FastAPI,HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

users_db = {
    "asdf": {
        "username": "asdf",
        "hashed_password": "$2b$12$CFaTR5wERJgwMuqb/SRSSeO/rt/m3A01InBG3rZ8EsKFk7jPjJTSO",
        "disabled": False,
    },
}
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class TokenData(BaseModel):
    username: Optional[str] = None

SECRET_KEY = "8119b3629d21ec5602f2d68cc8f7533d44d94b6add9cff6f1b070ad1c5e3fe58"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

with open("menu.json", "r") as read_file:
    data = json.load(read_file)

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    # Untuk menambah time limit pada token:
    # if expires_delta:
    #     expire = datetime.utcnow() + expires_delta
    # else:
    #     expire = datetime.utcnow() + timedelta(minutes=15)
    # to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/")
async def root(current_user: User = Depends(get_current_user)):
    return "You are accessing root node, Hello."

#Get Menu based on ID
@app.get("/menu/{item_id}")
async def read_menu(item_id: int, current_user: User = Depends(get_current_user)):

    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item

    raise HTTPException(
        status_code=404, detail=f'Index not found'
    )

@app.get("/menu/")
async def get_all(current_user: User = Depends(get_current_user)):

    return data['menu']

#Post Menu (Add New Menu Item)
@app.post("/menu/{item}")
async def add_menu(item : str, current_user: User = Depends(get_current_user)):
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
async def update_item(item_id: int, item_name: str, current_user: User = Depends(get_current_user)):
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
async def delete_item(item_id: int, current_user: User = Depends(get_current_user)):
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