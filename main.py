import psycopg2

conn = psycopg2.connect(
    dbname="trelldb",
    user="trell",
    password="troll",
    host="localhost"
)

cur = conn.cursor()

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Разрешаем CORS
origins = [
    #"*",  # разрешить все источники
     "http://localhost:5173",  # можно указать конкретно фронт
     "http://130.49.148.168:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # кто может обращаться
    allow_credentials=True,
    allow_methods=["GET","POST","DELETE"],        # какие методы разрешены (GET, POST и т.д.)
    allow_headers=["*"],        # какие заголовки разрешены
)

# Pydantic-модель для валидации входящих данных
class User(BaseModel):
    name: str
    password: str
    email: str
    photo: str | None = "default.png"

# 1. READ: Получить всех пользователей
@app.get("/users")
def get_users():
    cur.execute("SELECT * FROM public.user;")
    result = cur.fetchall()
    return result

# 2. CREATE: Создать нового пользователя
@app.post("/users")
def create_user(user: User):
    # Генерируем ID для новой задачи (просто длина списка + 1)
    new_user = user.model_dump()  # Превращаем Pydantic-модель в словарь
    name = new_user["name"]
    password = new_user["password"]
    email = new_user["email"]
    photo = new_user["photo"]

    # Сохраняем в базу
    cur.execute("INSERT INTO public.user (name,password,email,photo) VALUES"
                "(%s,%s,%s,%s) RETURNING user_id;",
                (name,password,email,photo))
    result = cur.fetchone()
    conn.commit()
    return result


# 3. UPDATE: что-нибудь обновить у пользователя хз???
"""
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    # Ищем задачу по ID
    cur.execute("SELECT * FROM public.user WHERE user_id = %s;", user_id)
    # Обновляем данные, сохраняя оригинальный ID
    updated_task = task.dict()
    updated_task["id"] = task_id
    fake_database[idx] = updated_task
    return updated_task

    # Если цикл завершился и мы ничего не вернули — задачи нет
    raise HTTPException(status_code=404, detail="Пользователь не найден")
"""


# 4. DELETE: Удалить задачу по ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    cur.execute("DELETE FROM public.user WHERE user_id = %s;",str(user_id))
    conn.commit()
    return {"Success": True}
