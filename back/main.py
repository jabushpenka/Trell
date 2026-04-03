import psycopg2
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from dotenv import load_dotenv
import os

# переменные окружения
load_dotenv()

# noinspection SpellCheckingInspection
# подключение к базе
conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("DBUSER"),
    password=os.getenv("DBPWORD"),
    host=os.getenv("DBHOST")
)

cur = conn.cursor()

# само приложение
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[  # потом поменять на домен
        "http://localhost:5173",
        "http://127.18.0.1:5173",
        "http://130.49.148.168:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # POST, GET, PUT и т.д.
    allow_headers=["*"],
)

# настройки шифрования
SECRET_KEY = str(os.getenv("SECRET_KEY"))
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Pydantic-модели для валидации входящих данных
class User(BaseModel):
    user_name: str
    pword: str
    email: str
    photo: str | None = "default.png"


class Board(BaseModel):
    board_name: str
    address: str
    about: str | None
    contents: dict | None


class Link(BaseModel):
    user_name: str
    address: str
    role_name: str = "Worker"

# модели объектов с доски, пожалуйста спид мне это нужно
class Task(BaseModel):
    id: str
    text: str
    done: bool = False


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


# модель для логина
class Login(BaseModel):
    login: str
    pword: str


# хеширование пароля
def hash_password(password: str):
    return pwd_context.hash(password)

# проверка пароля
def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

# отмена изменений для undocumented случаев
def cancel(error: Exception):
    conn.rollback()
    print(error)
    raise HTTPException(status_code=400, detail=str(error))

# Регистрация нового пользователя
@app.post("/register")
def register_user(user: User):
    new_user = user.model_dump()  # Превращаем Pydantic-модель в словарь
    user_name = new_user["user_name"]
    pword = new_user["pword"]
    email = new_user["email"]
    photo = new_user["photo"]

    hashed = hash_password(pword)

    try:
        cur.execute("INSERT INTO users (user_name,pword,email,photo)"
                    "VALUES (%s, %s, %s, %s) RETURNING user_id;",
                    (user_name, hashed, email, photo))
        result = cur.fetchone()
        conn.commit()
        return result
    except Exception as e:
        cancel(e)

# Проверка данных пользователя (логин)
@app.post("/login")
def login_user(login_info: Login):
    data = login_info.model_dump()
    user_name = data["login"]
    pword = data["pword"]

    cur.execute(
        "SELECT pword FROM users WHERE user_name = %s",
        (user_name,)
    )
    result = cur.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    stored_hash = result[0]

    if not verify_password(pword, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": user_name}, SECRET_KEY, algorithm="HS256")  # sha256 с ключом

    return {"access_token": token}


# Получить пользователей (для дебага)
@app.get("/users")
def get_users(skip: int = 0, limit: int = 10):
    cur.execute("SELECT * FROM users OFFSET %s LIMIT %s;",(skip,limit))
    result = cur.fetchall()
    return result

# Удалить пользователя по имени
@app.delete("/users/{user_name}")
def delete_user(user_name: str):
    try:
        cur.execute("DELETE FROM users WHERE user_name = %s RETURNING user_id;", (user_name,))
        result = cur.fetchone()
        if not bool(result):
            raise HTTPException(status_code=400, detail="User does not exist")
        conn.commit()
        return {"Deleted user ID": result}
    except Exception as e:
        cancel(e)


# Получить доски (для дебага)
@app.get("/boards")
def get_boards(skip: int = 0, limit: int = 10):
    cur.execute("SELECT * FROM boards OFFSET %s LIMIT %s;",(skip,limit))
    result = cur.fetchall()
    return result


# Создать новую доску
@app.post("/boards")
def create_board(board: Board, owner_name: str):
    cur.execute("SELECT user_id FROM users WHERE user_name = %s",(owner_name,))
    res = cur.fetchone()
    if not bool(res):
        raise HTTPException(status_code=400, detail="Owner does not exist")
    owner_id = res[0]

    new_board = board.model_dump()  # Превращаем Pydantic-модель в словарь
    board_name = new_board["board_name"]
    address = new_board["address"]
    about = new_board["about"]

    cur.execute("SELECT board_id FROM boards WHERE address = %s", (address,))
    res = cur.fetchone()
    if bool(res):
        raise HTTPException(status_code=400, detail="Board address taken")

    # Сохраняем в базу
    try:
        cur.execute("INSERT INTO boards (board_name,address,about) VALUES"
                    "(%s,%s,%s) RETURNING board_id;",
                    (board_name, address, about))
        board_id = cur.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        raise HTTPException(status_code=400, detail=str(e))

    try:
        cur.execute("INSERT INTO links (user_id,board_id,role_id) VALUES"
                    "(%s,%s,1) RETURNING user_id;",
                    (owner_id, board_id))
        conn.commit()
    except Exception as e:
        cancel(e)

    result = {"board_id": board_id, "owner_id": owner_id}
    return result


# Удалить доску по адресу
@app.delete("/boards/{address}")
def delete_board(address: str):
    try:
        cur.execute("DELETE FROM boards WHERE address = %s RETURNING board_id;",
                    (address,))
        result = cur.fetchone()
        if not bool(result):
            raise HTTPException(status_code=400, detail="Board does not exist")
        conn.commit()
        return {"Deleted board ID": result}
    except Exception as e:
        cancel(e)



# Получить все связи (для дебага)
@app.get("/links")
def get_links(skip: int = 0, limit: int = 10):
    cur.execute("SELECT users.user_name, boards.address, roles.role_name FROM "
                "( links INNER JOIN users ON links.user_id = users.user_id "
                "INNER JOIN "
                "boards ON links.board_id = boards.board_id "
                "INNER JOIN "
                "roles ON links.role_id = roles.role_id ) "
                "OFFSET %s LIMIT %s;",
                (skip,limit))
    result = cur.fetchall()
    return result


# Выдать пользователю роль на доске
@app.post("/links")
def give_role(link: Link):
    new_link = link.model_dump()  # Превращаем Pydantic-модель в словарь

    user_name = new_link["user_name"]
    cur.execute("SELECT user_id FROM users WHERE user_name = %s",
                (user_name,))
    res = cur.fetchone()
    if not bool(res):
        raise HTTPException(status_code=400, detail="User does not exist")
    user_id = res[0]

    address = new_link["address"]
    cur.execute("SELECT board_id FROM boards WHERE address = %s",
                (address,))
    res = cur.fetchone()
    if not bool(res):
        raise HTTPException(status_code=400, detail="Board does not exist")
    board_id = res[0]

    role_name = new_link["role_name"]
    cur.execute("SELECT role_id FROM roles WHERE role_name = %s",
                (role_name,))
    res = cur.fetchone()
    if not bool(res):
        raise HTTPException(status_code=400, detail="Role does not exist")
    role_id = res[0]


    # Сохраняем в базу
    try:
        cur.execute("SELECT * FROM links WHERE user_id = %s AND board_id = %s",
                    (user_id, board_id))
        res = cur.fetchone()
        if not bool(res):
            cur.execute("INSERT INTO links (user_id,board_id,role_id) VALUES"
                        "(%s,%s,%s) RETURNING user_id,board_id,role_id;",
                        (user_id, board_id, role_id))
        else:
            cur.execute("UPDATE links SET role_id = %s WHERE user_id = %s AND board_id = %s RETURNING user_id, board_id, role_id;",
                        (role_id, user_id, board_id))


        result = cur.fetchone()
        conn.commit()
        return result
    except Exception as e:
        cancel(e)


# Проверить роль пользователя на доске
@app.get("/boards/{address}/{user_name}")
def check_access(address: str, user_name: str):
    cur.execute("SELECT board_id FROM boards WHERE address = %s",
                (address,))
    res = cur.fetchone()
    if not bool(res):
        raise HTTPException(status_code=400, detail="Board does not exist")
    board_id = res[0]

    cur.execute("SELECT user_id FROM users WHERE user_name = %s",
                (user_name,))
    res = cur.fetchone()
    if not bool(res):
        raise HTTPException(status_code=400, detail="User does not exist")
    user_id = res[0]

    cur.execute("SELECT role_id FROM links WHERE board_id = %s AND user_id = %s;",
                (board_id, user_id))
    res = cur.fetchone()
    if not bool(res):
        return {"User has no access"}
    role_id = res[0]

    cur.execute("SELECT role_name FROM roles WHERE role_id = %s;",
                (role_id,))
    res = cur.fetchone()
    if not bool(res):
        return {"Role does not exist/unknown role"}
    role_name = res[0]

    result = {"Access level": role_name}
    return result

# Получить все доски пользователя по имени
@app.get("/user-boards/{user_name}")
def get_user_boards(user_name: str):
    try:
        cur.execute("SELECT user_id FROM users WHERE user_name = %s;", (user_name,))
        res = cur.fetchone()
        if not bool(res):
            return {"User does not exist"}
        user_id = res[0]

        cur.execute("SELECT * FROM boards WHERE board_id IN"
                    "(SELECT board_id FROM links WHERE user_id=%s);",
                    (user_id,))
        result = cur.fetchall()
        return result
    except Exception as e:
        cancel(e)

security = HTTPBearer()


# Вернуть пользователя из токена
@app.get("/token")
def get_user_by_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = payload.get("sub")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Получить содержимое доски по адресу
@app.get("/boards/{address}")
def get_board_data(address: str):
    cur.execute("SELECT contents FROM boards WHERE address = %s;",
                (address,))
    result = cur.fetchone()
    if not bool(result):
        return {"Board does not exist"}

    return result

# изменение на доске по адресу
@app.put("/boards/{address}")
def update_board(address: str, board_contents: BoardContents):
    contents_json = json.dumps(board_contents.model_dump())

    cur.execute("SELECT board_id FROM boards WHERE address = %s;",
                (address,))
    res = cur.fetchone()
    if not bool(res):
        return {"Board does not exist"}

    try:
        cur.execute("UPDATE boards SET contents = %s WHERE address = %s RETURNING address,contents;",
                    (contents_json, address))
        result = cur.fetchone()
        conn.commit()
        return result
    except Exception as e:
        cancel(e)

# Получить все роли (для дебага)
@app.get("/roles")
def get_roles(skip: int = 0, limit: int = 10):
    cur.execute("SELECT * FROM roles OFFSET %s LIMIT %s;",(skip,limit))
    result = cur.fetchall()
    return result
