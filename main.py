from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    """Модель задачи"""
    id: str
    title: str
    completed: bool = False


class TaskCreate(BaseModel):
    title: str

class Book(BaseModel):
    book: str

class TaskUpdate(BaseModel):
    title: str


tasks: list[Task] = []
book: str = ""

@app.get("/tasks", response_model=list[Task])
def get_tasks():
    """Получить список задач"""
    return tasks


@app.post("/tasks", response_model=Task)
def create_task(payload: TaskCreate):
    """Создать новую задачу"""
    task = Task(id=str(uuid4()), title=payload.title, completed=False)
    tasks.append(task)
    return task

@app.get("/booklike")
def get_book():
    global book
    return f'Любимая книга: {book}'


@app.post("/booklike")
def name_book(payload: Book):
    global book
    book = payload.book
    return book


