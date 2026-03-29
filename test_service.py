import requests
import logging
import sys

# Настройки адресов сервисов
recommendations_url = "http://127.0.0.1:8000"
features_url = "http://127.0.0.1:8010"  # Адрес сервиса признаков
events_store_url = "http://127.0.0.1:8020" # Адрес стора событий
headers = {'Content-type': 'application/json'}

# Настройка логирования
logger = logging.getLogger("full_test_logger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('test_service.log', mode='w', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# --- Блок проверки состояния сервисов (Health Check) ---

def check_services_health():
    """Проверяет доступность всех микросервисов системы"""
    logger.info("--- ПРОВЕРКА СОСТОЯНИЯ СИСТЕМЫ ---")
    services = {
        "Recommendations Service": recommendations_url,
        "Feature Service": features_url,
        "Events Service": events_store_url
    }
    
    all_ok = True
    for name, url in services.items():
        try:
            # Пробуем достучаться до корня или эндпоинта /health
            resp = requests.get(url, timeout=2)
            logger.info(f"[OK] {name} доступен (Статус {resp.status_code})")
        except Exception as e:
            logger.error(f"[ERROR] {name} НЕДОСТУПЕН по адресу {url}!")
            all_ok = False
    
    if not all_ok:
        logger.warning("Внимание: Некоторые сервисы не отвечают. Тесты могут упасть.")
    return all_ok

# --- Проверка сервиса рекоммендаций ---

def top_recs(k: int = 10):
    params = {'k': k}
    resp = requests.post(recommendations_url + "/recommendations_default", headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"Top-{k} popular tracks: {data.get('recs')}")
    else:
        logger.error(f"Top recs error, status: {resp.status_code}")

def offline_recs(user_id: int, k: int = 10):
    params = {'user_id': user_id, 'k': k}
    resp = requests.post(recommendations_url + "/recommendations_offline", headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"Offline recs for user {user_id}: {data.get('recs')}")
    else:
        logger.error(f"Offline error for user {user_id}, status: {resp.status_code}")

def add_online(user_id: int, track_id: int):
    params = {"user_id": user_id, "track_id": track_id}
    # Обращаемся напрямую в Events Service
    resp = requests.post(events_store_url + "/put", headers=headers, params=params)
    if resp.status_code == 200:
        logger.info(f"Added item {track_id} to online history of user {user_id}")
    else:
        logger.error(f"Events Service error, status: {resp.status_code}")

def blended_recs(user_id: int, k: int = 10):
    params = {"user_id": user_id, 'k': k}
    resp = requests.post(recommendations_url + "/recommendations", headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        logger.info(f"Blended recs for user {user_id}: {data.get('recs')}")
    else:
        logger.error(f"Blended error for user {user_id}, status: {resp.status_code}")

# --- Основной цикл тестирования ---

if __name__ == "__main__":
    logger.info("=== ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ ===")
    
    # Сначала проверяем, живы ли сервисы
    if check_services_health():
        
        # Сценарий 1: Пользователь без истории 
        logger.info("--- Сценарий 1: Проверка Default (ID 999) ---")
        top_recs(k=3)

        # Сценарий 2: Только офлайн 
        user_id = 617032
        logger.info(f"--- Сценарий 2: Офлайн-рекомендации (ID {user_id}) ---")
        offline_recs(user_id)

        # Сценарий 3: Смешивание 
        active_user = 505050
        logger.info(f"--- Сценарий 3: Blending (ID {active_user}) ---")
        add_online(active_user, track_id=777) # Эмулируем активность в Events Service
        blended_recs(active_user, k=4) # Запрашиваем результат смешивания в Recs Service

        logger.info("=== ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ. РЕЗУЛЬТАТ В test_service.log ===")
    else:
        logger.critical("ТЕСТИРОВАНИЕ ПРЕРВАНО: Не все сервисы запущены.")

