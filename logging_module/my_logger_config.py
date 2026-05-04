import logging
import logging.config  # Нужен для dictConfig
import yaml  # Нужен для работы с YAML
import os
from pathlib import Path  # Нужен для создания директорий

YamlPathType = str


def setup_logging(
        task_name: str = "general",
        default_path: YamlPathType = 'my_logging_config.yaml') -> None:
    """
     Настраивает систему логирования приложения.
     Пытается загрузить конфигурацию из YAML-файла, указанного в default_path или через переменную окружения env_key.
     При возникновении ошибки загрузки или если файл не найден,
     используется базовая конфигурация логирования (вывод в stderr, уровень DEBUG).
     :param task_name: str: Имя папки для файлов с логами.
     :param default_path: YamlPathType: Путь к файлу конфигурации YAML по умолчанию.
     :return: None: Конфигурация логирования применяется глобально.
    """
    # 1. Определяем базовые пути
    # Получаем абсолютный путь к папке, где лежит текущий файл (my_logger_config.py)
    current_dir = Path(__file__).resolve().parent
    # Корень проекта (WorkWithAPI)
    project_root = current_dir.parent

    # 2. Определяем путь к конфигурации
    # Склеиваем путь к папке модуля и имя файла конфига
    config_path: Path = current_dir / default_path

    # 3. Проверяем существование файла через объект Path
    if config_path.exists():
        try:
            # Открываем и читаем YAML
            with open(config_path, 'rt', encoding='utf-8') as f:
                # Парсим YAML
                config: dict = yaml.safe_load(f)

            # 4. Создаем директорию для логов (если ее нет) конкретной задачи: logs/task_2
            log_dir: Path = project_root / 'logs' / task_name
            # отключаем возникновение ошибки в случае, если директория уже существует
            log_dir.mkdir(parents=True, exist_ok=True)

            # 5. Перезаписываем пути в хендлерах конфига
            # Проходимся по всем хендлерам в YAML (file, error_file и тд.)
            # и подставляем им правильный абсолютный путь
            for handler_name, handler_conf in config.get('handlers', {}).items():
                if 'filename' in handler_conf:
                    # Извлекаем только имя файла (например 'app.log') из старого пути
                    filename = Path(handler_conf['filename']).name
                    # Собираем новый абсолютный путь: корень/logs/task_name/app.log
                    new_log_path = log_dir / filename
                    handler_conf['filename'] = str(new_log_path)

            # 6. Применяем конфигурацию
            logging.config.dictConfig(config)
            print(f'Конфигурация логирования загружена из файла: {config_path}')
            print(f'Логирование для {task_name} настроено. Файлы в {log_dir}')
        except Exception as e:
            # 7. Если файл найден, но произошла ошибка при его чтении/парсинге
            print(f'Ошибка при чтении или парсинге файла конфигурации "{config_path}": {e}.'
                  f' Используются базовые настройки (уровень DEGUG).')
            logging.basicConfig(level=logging.DEBUG)  # Fallback на DEBUG
    else:
        # 8. Если файл не найден, используем базовую программную настройку
        print(f'Файл конфигурации логирования "{config_path}" не найден. Используются базовые настройки (уровень DEGUG).')
        logging.basicConfig(level=logging.DEBUG)  # Fallback на DEBUG