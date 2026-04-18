import os
import json
from session import FemapSession
from builders import ConeModelBuilder
from director import ModelDirector

def run_automation(config_path):
    """Точка входа: инициализация сессии, строителей и запуск задач."""
    
    if not os.path.exists(config_path):
        print(f"Ошибка: Файл конфигурации {config_path} не найден.")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 1. Инициализируем соединение с Femap (Singleton)
    session = FemapSession()
    if not session.is_connected():
        print("Ошибка: Не удалось подключиться к Femap. Убедитесь, что программа запущена.")
        return

    # 2. Выбираем строителя (в будущем можно выбирать на основе типа в JSON)
    builder = ConeModelBuilder()
    
    # 3. Создаем Директора
    director = ModelDirector(builder)

    # 4. Обрабатываем список задач
    tasks = config.get("tasks", [])
    if not tasks:
        print("Задачи для выполнения не найдены в конфигурации.")
        return

    models_dir = os.path.join(os.getcwd(), "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    for i, t_data in enumerate(tasks):
        print(f"\n>>> Выполнение задачи {i+1}: {t_data.get('file_name', 'Unnamed')} <<<")
        
        output_path = os.path.join(models_dir, t_data["file_name"])
        
        # Директор собирает модель на основе текущего конфига (глобальный + специфичный для задачи)
        # В данном примере мы передаем общий конфиг, но логика расширяема
        success = director.construct_and_solve(config, output_path)
        
        if not success:
            print(f"ОШИБКА: Задача {i+1} завершилась неудачно.")

if __name__ == "__main__":
    run_automation("config.json")
