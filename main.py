#ВСЕ ИМПОРТЫ
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Depends , status , HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from sqlalchemy import create_engine , select
from sqlalchemy.orm import (
    sessionmaker,
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
)


# НАСТРОЙКА ПОДКЛЮЧЕНИЯ К БАЗЕ ПОСТГРЕСКЛ
DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost:15432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,      # ← ГЛАВНОЕ
)

#КЛАСС ОТ КОТОРОГО
class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))

class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)

class CategoryORM(Base):
    __tablename__ = 'categories'

    name: Mapped[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

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
    name: str

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: str

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

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def task_to_model(task: TaskORM) -> Task:
    """Конвертация объекта ORM в Pydantic"""
    return Task(id=task.id, title=task.title, completed=task.completed)

def category_to_model(category: CategoryORM) -> Category:
    return Category(id=category.id, name=category.name)


@app.get("/tasks", response_model=list[Task])
def get_tasks(db: Session = Depends(get_db)) -> list[Task]:
    """Получить список задач"""
    tasks = db.scalars(select(TaskORM)).all()
    return [task_to_model(task) for task in tasks]

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """Создать новую задачу"""
    new_task = TaskORM(title=payload.title, completed=False)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return task_to_model(new_task)

@app.patch("/tasks/{task_id}",response_model=Task)
def tasks_update(task_id: str, payload: UpdateTasks ,db : Session = Depends(get_db) ):
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    task.title = payload.title if payload.title is not None else task.title
    task.completed = payload.completed if payload.completed is not None else task.completed
    db.commit()
    db.refresh(task)
    return task_to_model(task)

@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.get(TaskORM, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    db.delete(task)
    db.commit()

@app.get("/bookdike")
def get_book():
    global book
    return f'Любимая книга: {book}'


@app.post("/booklike")
def name_book(payload: Book):
    global book
    book = payload.book
    return book

@app.get("/categories", response_model=list[Category])
def get_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(CategoryORM)).all()
    return [category_to_model(c) for c in categories]

@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    category = CategoryORM(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)                # ← фикс
    return category_to_model(category)

@app.patch("/categories/{category_id}", response_model=Category)   # ← не list
def update_category(category_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)):
    category = db.get(CategoryORM, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category.name = payload.name if payload.name is not None else category.name
    db.commit()
    db.refresh(category)                # ← фикс
    return category_to_model(category)


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, db: Session = Depends(get_db)):
    category = db.get(CategoryORM, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")  # ← фикс
    db.delete(category)
    db.commit()

