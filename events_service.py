import pandas as pd
from fastapi import FastAPI


# Класс-хранилище онлайн-событий 
class EventStore:
    """
    Класс для сохранения и получения последних онлайн-событий,
    необходимых для генерации персональных онлайн-рекомендаций.
    """

    def __init__(self, max_events_per_user=10):

        self.events = {}
        self.max_events_per_user = max_events_per_user

    def put(self, user_id, track_id):
        """
        Сохраняет событие
        """
        user_events = self.events.get(user_id, [])
        self.events[user_id] = [track_id] + user_events[: self.max_events_per_user]

    def get(self, user_id, k):
        """
        Возвращает последние онлайн-события пользователя
        """
        user_events = self.events.get(user_id, [])[: min(k, self.max_events_per_user)]

        return user_events


# Создаем хранилище событий
events_store = EventStore()

# Создаём приложение FastAPI
app = FastAPI(title="events")


# Обращение к корневому url для проверки работоспособности сервиса
@app.get("/")
def read_root():
    return {"message": "Events service is working"}


# Сохранение одного события
@app.post("/put")
async def put(user_id: int, track_id: int):
    """
    Сохраняет событие для user_id, track_id
    """
    events_store.put(user_id, track_id)
    return {"result": "ok"}


# Получение онлайн-событий, начиная с самого последнего
@app.post("/get")
async def get(user_id: int, k: int = 10):
    """
    Возвращает список последних k событий для пользователя user_id
    """
    events = events_store.get(user_id, k)
    return {"events": events}