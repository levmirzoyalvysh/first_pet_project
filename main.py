from uuid import uuid4
from fastapi.middleware.cors import (
    CORSMiddleware,   # ← возможно, эта строка отсутствует или сломана
)
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Category(BaseModel):
    id: str
    title: str

class CategoryCreate(BaseModel):
    title: str

class CategoryUpdate(BaseModel):
    title: str

class Task(BaseModel):
    """Модель задачи"""
    id: str
    title: str
    completed: bool = False

class UpdateTasks(BaseModel):
    title: str | None = None
    completed: bool | None = None


class TaskCreate(BaseModel):
    title: str

class Book(BaseModel):
    book: str




tasks: list[Task] = []
categories: list[Category] = []
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

@app.patch("/tasks/{task_id}")
def tasks_update(task_id: str, payload: UpdateTasks):
    for task in tasks:
        if task.id == task_id:
            if payload.title:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed

            return task

@app.delete('/tasks/{task_id}')
def delete_task(task_id):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)

@app.get("/categories" , response_model=list[Category])
def get_categories():
    return categories

@app.post("/categories", response_model=list[Category])
def create_category(payload: CategoryCreate):
    categoria = Category(id=str(uuid4()), title=payload.title)
    categories.append(categoria)
    return categories

@app.patch("/categories/{category_id}", response_model=list[Category])
def update_category(category_id: str, payload: CategoryUpdate):
    for categoria in categories:
        if categoria.id == category_id:
            categoria.title = payload.title
            return categoria

@app.delete("/categories/{category_id}", response_model=list[Category])
def delete_category(category_id: str, payload: Category):
    for categoria in categories:
        if categoria.id == category_id:
            categories.remove(categoria)

