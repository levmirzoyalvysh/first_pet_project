from DataBase import engine, Base
from models import Task   # обязательно импортируем модель!

Base.metadata.create_all(bind=engine)
print("Tables created")