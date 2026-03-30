import psycopg2
import json 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
import os
import bcrypt

# noinspection SpellCheckingInspection
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST")
)

cur = conn.cursor()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[#потом поменять на домен
        "http://localhost:5173",
        "http://127.18.0.1:5173",
        "http://130.49.148.168:5173",
        ],  
    allow_credentials=True,
    allow_methods=["*"],  # POST, GET, PUT и т.д.
    allow_headers=["*"],
)

SECRET_KEY = str(os.getenv("SECRET_KEY"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic-модель для валидации входящих данных
class User(BaseModel):
    user_name: str
    password: str
    email: str
    photo: str | None = "default.png"

class Board(BaseModel):
    board_name: str
    address: str
    about: str | None
    contents: dict | None

class Link(BaseModel):
    user_id: int
    board_id: int


#модели объектов с доски, пожалуйста спид мне это нужно
class Task(BaseModel):
    id: str
    text: str
    done: bool

class Card(BaseModel):
    id: str
    title: str
    tasks: list[Task]

class Column(BaseModel):
    id: str
    title: str
    cards: list[Card]

class BoardContents(BaseModel):
    columns: list[Column]

#модель для логина
class Login(BaseModel):
    login: str
    password: str


#хеширование и проверка пароля
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


# 1. CREATE: Регистрация нового пользователя
@app.post("/register")
def register_user(user:User):
    cur = conn.cursor()
    new_user = user.model_dump()  # Превращаем Pydantic-модель в словарь
    user_name = new_user["user_name"]
    password = new_user["password"]
    email = new_user["email"]
    photo = new_user["photo"]
    
    hashed = hash_password(password)

    try:
        cur.execute("INSERT INTO users (name,password,email,photo)"
            "VALUES (%s, %s, %s, %s) RETURNING user_id;",
            (user_name, hashed, email, photo))
        result = cur.fetchone()
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        raise HTTPException(status_code=400, detail="User already exists")

    return result

# 2. READ: Проверка данных пользователя (логин)
@app.post("/login")
def login(data: User):
    cur = conn.cursor()
    login = data.user_name
    password = data.password

    cur.execute(
        "SELECT password FROM users WHERE name = %s",
        (login,)
    )
    result = cur.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    stored_hash = result[0]

    if not verify_password(password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": login}, SECRET_KEY, algorithm="HS256") #sha256 с ключом

    return {"access_token": token}

# 1. READ: Получить всех пользователей
@app.get("/users")
def get_users():
    cur.execute("SELECT * FROM users;")
    result = cur.fetchall()
    return result

# 2. CREATE: Создать нового пользователя
@app.post("/users")
def create_user(user: User):
    new_user = user.model_dump()  # Превращаем Pydantic-модель в словарь
    user_name = new_user["user_name"]
    pword = new_user["pword"]
    email = new_user["email"]
    photo = new_user["photo"]

    # Сохраняем в базу
    cur.execute("INSERT INTO users (user_name,pword,email,photo) VALUES"
                "(%s,%s,%s,%s) RETURNING user_id;",
                (user_name,pword,email,photo))
    result = cur.fetchone()
    conn.commit()
    return result

# 4. DELETE: Удалить пользователя по ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    cur.execute("DELETE FROM users WHERE user_id = %s RETURNING user_name;",str(user_id))
    result = cur.fetchone()
    conn.commit()
    return {"Deleted user name": result}

# 1. READ: Получить все доски
@app.get("/boards")
def get_boards():
    cur.execute("SELECT * FROM boards;")
    result = cur.fetchall()
    return result

# 2. CREATE: Создать новую доску
@app.post("/boards")
def create_board(board: Board, user_id: int):
    new_board = board.model_dump()  # Превращаем Pydantic-модель в словарь
    board_name = new_board["board_name"]
    address = new_board["address"]
    about = new_board["about"]

    # Сохраняем в базу
    cur.execute("INSERT INTO boards (board_name,address,about) VALUES"
                "(%s,%s,%s) RETURNING board_id;",
                (board_name,address,about))
    board_id = cur.fetchone()[0]
    conn.commit()

    cur.execute("INSERT INTO link (user_id,board_id) VALUES"
                "(%s,%s) RETURNING user_id;",
                (user_id,board_id))
    u_id = cur.fetchone()[0]
    conn.commit()

    result = {"board_id": board_id, "owner_user_id":u_id}
    return result

# 4. DELETE: Удалить доску по ID
@app.delete("/boards/{board_id}")
def delete_board(board_id: int):
    b_id = str(board_id)

    cur.execute("DELETE FROM link WHERE board_id = %s;", b_id)

    cur.execute("DELETE FROM boards WHERE board_id = %s RETURNING address;",b_id)
    result = cur.fetchone()
    conn.commit()
    return {"Deleted board address": result}

# 1. READ: Получить все связи
@app.get("/links")
def get_links():
    cur.execute("SELECT * FROM link;")
    result = cur.fetchall()
    return result

# 2. CREATE: Создать новую связь
@app.post("/links")
def create_link(link: Link):
    new_link = link.model_dump()  # Превращаем Pydantic-модель в словарь
    user_id = new_link["user_id"]
    board_id = new_link["board_id"]

    # Сохраняем в базу
    cur.execute("INSERT INTO link (user_id,board_id) VALUES"
                "(%s,%s) RETURNING user_id,board_id;",
                (user_id,board_id))
    result = cur.fetchone()
    conn.commit()
    return result

# 1. READ: Проверить доступ пользователя к доске
@app.get("/boards/{board_id}/{user_id}")
def check_access(board_id : int, user_id : int):
    b_id = str(board_id)
    u_id = str(user_id)
    cur.execute("SELECT * FROM link WHERE board_id = %s AND user_id = %s;", (b_id,u_id))
    result = cur.fetchone()
    return bool(result)

# 1. READ: Получить все доски пользователя
@app.get("/userboards/{user_name}")
def get_user_boards(user_name : str):
    cur.execute("SELECT user_id FROM users WHERE name = %s;",(user_name,))
    user_id = cur.fetchone()[0]
    cur.execute("SELECT board_id FROM link WHERE user_id = %s;", (user_id,))
    result = cur.fetchall()
    return result


security = HTTPBearer()
# 2. READ: Вернуть пользователя из токена
@app.get("/token")
def get_user_by_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("sub")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 2. READ: Получить содержимое доски
@app.get("/boards/{board_id}")
def get_board_data(board_id : int):
    cur.execute("SELECT contents FROM boards WHERE board_id = %s;", (board_id,))
    result = cur.fetchone()[0]
    return result

# 3. UPDATE: изменение на доске
@app.put("/boards/{board_id}")
def update_board(board_id: int, board_contents: BoardContents):
    contents_json = json.dumps(board_contents.model_dump())
    # Ищем задачу по ID
    
    cur.execute("UPDATE boards SET contents = %s WHERE board_id = %s RETURNING address,contents;",
                (contents_json,str(board_id)))
    result = cur.fetchone()
    conn.commit()
    return result
