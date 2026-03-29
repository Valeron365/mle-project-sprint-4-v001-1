# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/Valeron365/mle-project-sprint-4-v001
```

## Активируйте виртуальное окружение


Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

Код вспомогательных сервисов содержится в файлах:

`features_service.py` - вспомогательный сервис для поиска похожих треков;
`events_service.py` - вспомогательный сервис для сохранения и получения последних прослушанных треков пользователя.

# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

Для корректной работы должны быть запущены три микросервиса:

feature_service.py (порт 8010)
events_service.py (порт 8020)
recommendations_service.py (порт 8000)
```
uvicorn recommendations_service:app
uvicorn events_service:app --port 8020
uvicorn features_service:app --port 8010
```
Тестирование:
Запуск тестов осуществляется скриптом test_service.py:
```
python test_service.py
```

Скрипт автоматически:
Проверяет доступность (Health Check) всех трех сервисов.
Тестирует сценарий «Холодного старта» (новый пользователь).
Тестирует сценарий «Только офлайн» (постоянный пользователь без текущей сессии).
Тестирует сценарий «Blending» (активный пользователь с новыми кликами).
Сохраняет подробный лог выполнения в файл test_service.log.

# Стратегия смешивания (Blending Strategy)
Для формирования итогового списка используется стратегия Interleaving (чередование).
Логика смешивания:
Нечетные позиции (1, 3, 5...): заполняются рекомендациями из офлайн-истории (персональные подборки из feature_service).
Четные позиции (2, 4, 6...): заполняются рекомендациями на основе онлайн-активности (данные из events_service).
Обработка исключений (Fallback):
Если у пользователя нет онлайн-истории, вакантные «четные» места заполняются офлайн-рекомендациями.
Если у пользователя нет ни офлайн, ни онлайн данных (новый пользователь), сервис возвращает Default-рекомендации (топ популярных треков).
Дубликаты при смешивании исключаются.

