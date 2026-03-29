import logging
from contextlib import asynccontextmanager
import pandas as pd
from fastapi import FastAPI


logger = logging.getLogger("uvicorn.error")


class SimilarItems:
    """
    Класс для поиска похожих айтемов, необходимых для генерации онлайн-рекомендаций
    """

    def __init__(self):

        self._similar_items = None

    def load(self, path, **kwargs):
        """
        Загружаем данные из файла
        """
        logger.info(f"Loading data, type: {type}")
        self._similar_items = pd.read_parquet(path, **kwargs) 
        logger.info(f"Loaded")

    def get(self, track_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items.query('track_id == @track_id')
            i2i = i2i[["similar_track_id", "similarity_score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"similar_track_id": [], "similarity_score": []}

        return i2i


sim_items_store = SimilarItems()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    sim_items_store.load(
        'similar.parquet', 
        columns=["track_id", "similar_track_id", "similarity_score"],
    )
    logger.info("Ready!")
    # код ниже выполнится только один раз при остановке сервиса
    yield


# Создаём приложение FastAPI
app = FastAPI(title="features", lifespan=lifespan)


# Обращение к корневому url для проверки работоспособности сервиса
@app.get("/")
def read_root():
    return {"message": "Features service is working"}


@app.post("/similar_items")
async def recommendations(track_id: int, k: int = 10):
    """
    Возвращает список похожих объектов длиной k для track_id
    """
    i2i = sim_items_store.get(track_id, k)
    return i2i