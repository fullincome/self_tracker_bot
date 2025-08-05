# Self-Tracker Telegram Bot (Todoist/Yougile)

Telegram-бот для создания задач в **Todoist** или **Yougile** с поддержкой голосовых сообщений и распознавания речи через Yandex SpeechKit и LLM (YandexGPT).

## 🚀 Основные возможности

- **Создание задач из текста**: Отправьте текстовое сообщение боту, и он автоматически создаст задачу в выбранном сервисе (Todoist или Yougile)
- **Голосовые сообщения**: Отправьте голосовое сообщение, бот распознает речь и создаст задачу
- **LLM-парсинг**: Используется YandexGPT для извлечения параметров задачи из естественного языка
- **Гибкий выбор сервиса**: Сервис выбирается при запуске бота через переменную окружения `SERVICE` (`todoist` или `yougile`)
- **Приватность**: Доступ только для указанного пользователя по Telegram ID
- **Логирование**: Ведение подробных логов работы бота
- **Системный сервис**: Возможность запуска как systemd сервис
- **Гибкая конфигурация**: Все параметры задаются через .env-файл
- **Командная строка**: Утилита для создания задач без Telegram (поддерживает оба сервиса)

> **Примечание:** Self-Tracker — это название бота, а не отдельный сервис. Бот поддерживает только Todoist и Yougile.

## 📋 Требования

- Python 3.7+
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- Todoist API Token (если используете Todoist)
- Yougile API Token и ID колонки (если используете Yougile)
- Yandex SpeechKit API Token (получить в [Yandex Cloud](https://cloud.yandex.ru/))
- YandexGPT API Key и Folder ID (получить в [Yandex Cloud](https://cloud.yandex.ru/))

## 🛠 Установка и настройка

### Быстрый старт (локальная разработка)

1. **Клонирование и настройка окружения**:
   ```bash
   git clone <repository-url>
   cd self_tracker_bot
   ./setup_env.sh
   ```

2. **Создайте .env-файл** (или используйте `.env_template`):
   ```bash
   cp .env_template .env
   # Заполните все переменные своими значениями
   ```

3. **Создайте виртуальное окружение и установите зависимости**:
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   pip install -r requirements.txt
   ```

### Запуск бота

Запуск осуществляется через скрипт:

```bash
./run_bot.sh -e .env
```

- Для выбора сервиса укажите в .env: `SERVICE=todoist` или `SERVICE=yougile`
- Для смены пути к виртуальному окружению используйте `-v <venv_path>`

### Создание задач из командной строки

```bash
./create_task.sh -s todoist -e .env "Купить хлеб"
./create_task.sh -s yougile -e .env "Позвонить клиенту"
```

## ⚙️ Конфигурация

### Пример .env

```bash
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_USER_ID=your_telegram_user_id
YANDEX_FOLDER_ID=your_yandex_folder_id
YANDEX_SPEECHKIT_TOKEN=your_yandex_token
YANDEX_GPT_APIKEY=your_yandex_gpt_apikey
SERVICE=todoist   # или yougile

TODOIST_TOKEN=your_todoist_token   # (только если используете Todoist)
YOUGILE_TOKEN=your_yougile_token   # (только если используете Yougile)
YOUGILE_LOCATION=your_yougile_column_id   # (только если используете Yougile)
```

**Важно:** Все переменные должны быть заданы для выбранного сервиса. Без них бот не запустится.

## 🛠 Смена tracker-а

Tracker выбирается через переменную окружения `SERVICE` в .env (`todoist` или `yougile`).

## 📁 Работа с проектами Todoist

### Просмотр доступных проектов

Для просмотра всех проектов в вашем Todoist аккаунте:

```bash
python3 list_todoist_projects.py
```

### Установка проекта и секции по умолчанию

#### Быстрый способ (автоматическое получение ID):

```bash
# Получить ID проекта
python3 get_todoist_ids.py "Название проекта"

# Получить ID проекта и секции
python3 get_todoist_ids.py "Название проекта" "Название секции"
```

#### Ручной способ:

Добавьте в `.env` файл:
```
TODOIST_DEFAULT_PROJECT_ID=123456789
TODOIST_DEFAULT_SECTION_ID=987654321
```

### Создание задач в конкретном проекте

Можно указать проект прямо в тексте задачи:
```
"Сделать отчёт в проекте Работа"
"Купить продукты в проекте Личное"
```

Бот автоматически найдет проект по названию и создаст в нем задачу.

### Приоритеты при создании задач:

1. **Проект и секция из текста** (если указаны)
2. **Проект из текста + секция по умолчанию** (если проект указан в тексте, а секция нет)
3. **Проект и секция по умолчанию** (если ничего не указано в тексте)
4. **Inbox** (если проект по умолчанию не настроен)

### Создание задач в конкретной колонке

Можно указать и проект, и колонку:
```
"Добавить задачу в колонку В работе проекта Разработка"
"Создать задачу в колонке Готово проекта Маркетинг"
```

**Важно:** Колонки доступны только в проектах с включенным Kanban-видом. В обычных проектах задачи создаются в первой колонке.

### Просмотр колонок в проектах

```bash
python3 list_todoist_sections.py
```

## 🐛 Устранение неполадок

- Проверьте, что все необходимые токены и ID колонки (для yougile) заданы в .env.
- Для yougile обязательно наличие `YOUGILE_TOKEN` и `YOUGILE_LOCATION`.
- Для todoist обязательно наличие `TODOIST_TOKEN`.
- Для работы LLM нужны `YANDEX_GPT_APIKEY` и `YANDEX_FOLDER_ID`.
- Логи ошибок выводятся в консоль.

## 📚 Примеры

**Через Telegram:**
```
Пользователь: "Купить молоко завтра в 18:00"
Бот: "✅ Задача создана: Купить молоко завтра в 18:00"

Пользователь: "Сделать отчёт в проекте Работа"
Бот: "✅ Задача создана в проекте 'Работа': Сделать отчёт"

Пользователь: "Добавить задачу в колонку В работе проекта Разработка"
Бот: "✅ Задача создана в проекте 'Разработка' в колонке 'В работе': Новая задача"
```

**Через командную строку:**
```bash
./create_task.sh -s yougile -e .env "Позвонить клиенту"
# Создана задача: Позвонить клиенту
```

## 📦 Зависимости проекта

Основные Python пакеты:
- `python-telegram-bot==22.1` — Telegram Bot API
- `requests==2.31.0` — HTTP запросы и интеграции
- `pydantic==1.10.14` — Для поддержки yougile_api

## 🗂️ Структура проекта

- `self_tracker_bot.py` — основной Telegram-бот
- `todoist_api.py` — API-клиент и обработка задач Todoist
- `yougile_api.py` — API-клиент и обработка задач Yougile
- `yandex_gpt.py` — интеграция с YandexGPT для парсинга задач
- `list_todoist_projects.py` — утилита для просмотра проектов Todoist
- `list_todoist_sections.py` — утилита для просмотра колонок в проектах Todoist
- `get_todoist_ids.py` — утилита для получения ID проекта и секции по названию
- `run_bot.sh` — запуск Telegram-бота
- `create_task.sh` — создание задач из командной строки
- `setup_env.sh` — быстрая настройка окружения
- `.env_template` — шаблон для .env
- `requirements.txt` — зависимости

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 📞 Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории проекта.

## 📦 Установка через deb-пакет

Бот можно собрать и установить как deb-пакет для Linux (Ubuntu/Debian).

### Сборка deb-пакета

Для сборки требуется установленный [podman](https://podman.io/):

```bash
./build_deb.sh
# Или с произвольным именем:
./build_deb.sh mybot
```

В результате появится файл `mybot_1.0.0_all.deb` в корне проекта.

### Установка пакета

```bash
sudo dpkg -i mybot_1.0.0_all.deb
```

### Первичная настройка

После установки:
- Все файлы бота будут размещены в `/usr/local/bin/mybot/`
- Логи работы: `/var/log/mybot/bot.log` и `/var/log/mybot/bot.error.log`
- Конфигурация: `/usr/local/bin/mybot/.env` (создаётся автоматически, заполните своими токенами)

**Пример содержимого .env:**
```
TELEGRAM_TOKEN=your_telegram_token
TODOIST_TOKEN=your_todoist_token   # (только если используете Todoist)
TODOIST_DEFAULT_PROJECT_ID=123456789   # (опционально, ID проекта по умолчанию)
TODOIST_DEFAULT_SECTION_ID=987654321   # (опционально, ID секции по умолчанию)
YOUGILE_TOKEN=your_yougile_token   # (только если используете Yougile)
YOUGILE_LOCATION=your_yougile_column_id   # (только если используете Yougile)
YANDEX_SPEECHKIT_TOKEN=your_yandex_token
YANDEX_GPT_APIKEY=your_yandex_gpt_apikey
YANDEX_FOLDER_ID=your_yandex_folder_id
TELEGRAM_USER_ID=your_telegram_user_id
SERVICE=todoist   # или yougile
```

После изменения `.env` перезапустите сервис:
```bash
sudo systemctl restart mybot.service
```

### Управление сервисом

- Проверить статус:
  ```bash
  sudo systemctl status mybot.service
  ```
- Перезапустить:
  ```bash
  sudo systemctl restart mybot.service
  ```
- Остановить:
  ```bash
  sudo systemctl stop mybot.service
  ```
- Удалить:
  ```bash
  sudo dpkg -r mybot
  ```
