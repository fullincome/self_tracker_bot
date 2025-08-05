# Memory Bank: Self-Tracker Telegram Bot

## 🎯 Обзор проекта

**Self-Tracker** — это Telegram-бот для автоматического создания задач в системах управления проектами (Todoist/Yougile) с поддержкой голосовых сообщений и AI-парсинга через YandexGPT.

### Ключевые возможности:
- 📝 Создание задач из текстовых сообщений
- 🎤 Создание задач из голосовых сообщений (распознавание речи через Yandex SpeechKit)
- 🤖 AI-парсинг параметров задач через YandexGPT
- 🔄 Поддержка двух сервисов: Todoist и Yougile
- 🔒 Приватность: доступ только для указанного пользователя
- 🖥️ Командная строка: создание задач без Telegram
- 📦 Системный сервис: установка как deb-пакет

## 🏗️ Архитектура проекта

### Основные компоненты:

```
self_tracker_bot/
├── self_tracker_bot.py      # Основной Telegram-бот
├── todoist_api.py           # API-клиент для Todoist
├── yougile_api.py           # API-клиент для Yougile
├── yandex_gpt.py            # Интеграция с YandexGPT
├── run_bot.sh               # Скрипт запуска бота
├── create_task.sh           # CLI для создания задач
├── setup_env.sh             # Настройка окружения
├── build_deb.sh             # Сборка deb-пакета
├── requirements.txt         # Python зависимости
└── debian/                  # Структура deb-пакета
```

## 🔧 Технические детали

### 1. Основной бот (`self_tracker_bot.py`)

**Назначение**: Telegram-бот с обработкой текстовых и голосовых сообщений

**Ключевые функции**:
- `start()` - приветствие и информация о сервисе
- `handle_text()` - обработка текстовых сообщений
- `handle_voice()` - обработка голосовых сообщений
- `recognize_speech_yandex()` - распознавание речи через Yandex SpeechKit
- `check_user()` - проверка доступа пользователя

**Поток обработки**:
1. Получение сообщения от пользователя
2. Проверка авторизации (`TELEGRAM_USER_ID`)
3. Для голосовых: распознавание речи → текст
4. Парсинг параметров через YandexGPT
5. Создание задачи в выбранном сервисе
6. Отправка подтверждения

### 2. Todoist API (`todoist_api.py`)

**Назначение**: Клиент для работы с Todoist REST API v2

**Ключевые возможности**:
- Создание задач с полным набором параметров
- Retry-логика при ошибках с `due_string`
- Интеграция с YandexGPT для парсинга параметров
- CLI-интерфейс для создания задач

**Поддерживаемые параметры**:
- `content` - текст задачи
- `description` - описание
- `project_id`, `section_id`, `parent_id` - структура
- `priority` (1-4) - приоритет
- `due_string`, `due_date`, `due_datetime` - сроки
- `labels` - метки

### 3. Yougile API (`yougile_api.py`)

**Назначение**: Клиент для работы с Yougile API v2

**Ключевые возможности**:
- Создание задач в указанной колонке
- Поддержка заголовка и описания
- CLI-интерфейс для создания задач

**Параметры**:
- `title` - заголовок задачи
- `description` - описание (HTML)
- `columnId` - ID колонки (из `YOUGILE_LOCATION`)

### 4. YandexGPT интеграция (`yandex_gpt.py`)

**Назначение**: AI-парсинг параметров задач из естественного языка

**Ключевые функции**:
- `ask()` - базовый запрос к YandexGPT
- `extract_todoist_task_params()` - парсинг для Todoist
- `extract_yougile_task_params()` - парсинг для Yougile

**Промпты для Todoist**:
```json
{
  "content": "текст задачи",
  "due_string": "завтра/сегодня/2025-06-30",
  "priority": 1-4,
  "labels": ["список", "меток"]
}
```

**Промпты для Yougile**:
```json
{
  "title": "Заголовок [срок]"
}
```

### 5. Скрипты управления

#### `run_bot.sh`
- Запуск Telegram-бота
- Валидация переменных окружения
- Активация виртуального окружения
- Проверка зависимостей для выбранного сервиса

#### `create_task.sh`
- CLI для создания задач без Telegram
- Поддержка обоих сервисов
- Валидация конфигурации

#### `setup_env.sh`
- Создание виртуального окружения
- Установка зависимостей
- Настройка Python окружения

## 🔐 Конфигурация и безопасность

### Переменные окружения (`.env`)

**Обязательные для всех сервисов**:
- `TELEGRAM_TOKEN` - токен Telegram-бота
- `TELEGRAM_USER_ID` - ID разрешенного пользователя
- `YANDEX_SPEECHKIT_TOKEN` - токен для распознавания речи
- `YANDEX_GPT_APIKEY` - API-ключ YandexGPT
- `YANDEX_FOLDER_ID` - Folder ID в Yandex Cloud
- `SERVICE` - выбранный сервис (`todoist` или `yougile`)

**Для Todoist**:
- `TODOIST_TOKEN` - API-токен Todoist

**Для Yougile**:
- `YOUGILE_TOKEN` - API-токен Yougile
- `YOUGILE_LOCATION` - ID колонки по умолчанию

### Безопасность
- Доступ только для указанного `TELEGRAM_USER_ID`
- Все токены хранятся в переменных окружения
- Валидация всех обязательных параметров при запуске

## 📦 Упаковка и развертывание

### Deb-пакет

**Структура пакета**:
```
/usr/local/bin/{package_name}/
├── self_tracker_bot.py
├── todoist_api.py
├── yougile_api.py
├── yandex_gpt.py
└── requirements.txt

/var/log/{package_name}/
├── bot.log
└── bot.error.log

/etc/systemd/system/
└── {package_name}.service
```

**Сборка**:
```bash
./build_deb.sh [package_name]
```

**Установка**:
```bash
sudo dpkg -i {package_name}_1.0.0_all.deb
```

### Systemd сервис

**Управление**:
```bash
sudo systemctl start/stop/restart/status {package_name}.service
```

**Логи**:
```bash
sudo journalctl -u {package_name}.service
```

## 🔄 Потоки данных

### 1. Текстовое сообщение
```
Пользователь → Telegram → self_tracker_bot.py → YandexGPT → Todoist/Yougile API
```

### 2. Голосовое сообщение
```
Пользователь → Telegram → self_tracker_bot.py → Yandex SpeechKit → YandexGPT → Todoist/Yougile API
```

### 3. CLI команда
```
Команда → create_task.sh → todoist_api.py/yougile_api.py → YandexGPT → Todoist/Yougile API
```

## 🛠️ Зависимости

### Python пакеты (`requirements.txt`):
- `python-telegram-bot==22.1` - Telegram Bot API
- `requests==2.31.0` - HTTP клиент
- `pydantic==1.10.14` - валидация данных

### Системные зависимости:
- Python 3.7+
- ffmpeg (для deb-пакета)
- podman (для сборки deb-пакета)

## 🐛 Обработка ошибок

### Retry-логика в Todoist
- При ошибке с `due_string` - повторная попытка без этого параметра
- Логирование всех ошибок API

### Валидация конфигурации
- Проверка всех обязательных переменных окружения
- Валидация выбранного сервиса
- Проверка существования виртуального окружения

### Логирование
- Подробные логи работы бота
- Отдельные файлы для ошибок
- Systemd journal integration

## 🚀 Использование

### Запуск бота
```bash
./run_bot.sh -e .env
```

### Создание задачи через CLI
```bash
./create_task.sh -s todoist -e .env "Купить хлеб завтра"
./create_task.sh -s yougile -e .env "Позвонить клиенту"
```

### Управление сервисом
```bash
sudo systemctl start/stop/restart self-tracker-bot.service
```

## 📈 Масштабирование и расширение

### Возможные улучшения:
1. **Поддержка других сервисов**: Jira, Asana, Trello
2. **База данных**: сохранение истории задач
3. **Многопользовательский режим**: поддержка нескольких пользователей
4. **Веб-интерфейс**: управление через браузер
5. **Аналитика**: статистика по созданным задачам
6. **Шаблоны**: предустановленные шаблоны задач
7. **Интеграции**: webhooks, календари

### Архитектурные решения:
- Модульная архитектура с четким разделением ответственности
- Единый интерфейс для разных сервисов
- Конфигурация через переменные окружения
- Поддержка как Telegram, так и CLI интерфейсов 