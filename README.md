# Self-Tracker Telegram Bot (Todoist/Yougile)

Telegram-бот для создания задач в **Todoist** или **Yougile** с поддержкой голосовых сообщений и распознавания речи через Yandex SpeechKit.

## 🚀 Основные возможности

- **Создание задач из текста**: Отправьте текстовое сообщение боту, и он автоматически создаст задачу в выбранном сервисе (Todoist или Yougile)
- **Голосовые сообщения**: Отправьте голосовое сообщение, бот распознает речь и создаст задачу
- **Гибкий выбор сервиса**: Сервис выбирается при запуске бота через переменную окружения `SERVICE` (`todoist` или `yougile`)
- **Приватность**: Доступ только для указанного пользователя по Telegram ID
- **Логирование**: Ведение подробных логов работы бота
- **Системный сервис**: Возможность запуска как systemd сервис
- **Гибкая конфигурация**: Поддержка файлов токенов и переменных окружения
- **Командная строка**: Утилита для создания задач без Telegram (поддерживает оба сервиса)

> **Примечание:** Self-Tracker — это название бота, а не отдельный сервис. Бот поддерживает только Todoist и Yougile.

## 📋 Требования

- Python 3.7+
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- Todoist API Token (если используете Todoist)
- Yougile API Token и ID колонки (если используете Yougile)
- Yandex SpeechKit API Token (получить в [Yandex Cloud](https://cloud.yandex.ru/))

## 🛠 Установка и настройка

### Быстрый старт (локальная разработка)

1. **Клонирование и настройка окружения**:
   ```bash
   git clone <repository-url>
   cd tgbot_todoist
   ./setup_env.sh
   ```

2. **Создайте файлы токенов** в директории (например, `~/.tokens`):
   - `todoist_token` — Todoist API токен (если используете Todoist)
   - `yougile_token` — Yougile API токен (если используете Yougile)
   - `yougile_location` — ID колонки Yougile (обязателен для yougile)
   - `telegram_token` — Telegram Bot токен
   - `yandex_speech_kit_recognizer_token` — Yandex SpeechKit токен
   - `telegram_id` — Telegram User ID

3. **Установите зависимости**:
   ```bash
   source myenv/bin/activate
   pip install -r requirements.txt
   ```

### Запуск бота

#### Через run_bot.sh

```bash
# Для Todoist:
./run_bot.sh -s todoist -t ~/.tokens

# Для Yougile:
./run_bot.sh -s yougile -t ~/.tokens
# (файл yougile_location должен быть в ~/.tokens или используйте -l <column_id>)
```

#### Через переменные окружения

```bash
export SERVICE=yougile
export YOUGILE_LOCATION=<column_id>
./run_bot.sh -s yougile -t ~/.tokens
```

### Создание задач из командной строки

```bash
# Для Todoist:
./create_task.sh -s todoist -t ~/.tokens "Купить хлеб"

# Для Yougile:
./create_task.sh -s yougile -t ~/.tokens -l <column_id> "Позвонить клиенту"
```

## ⚙️ Конфигурация

### Переменные окружения

```bash
# Пути к токенам и окружению
export TODOIST_TOKEN_PATH=/path/to/tokens
export VENV_PATH=/path/to/venv
export TELEGRAM_USER_ID=123456789

# Прямые токены (для .env файла)
export TELEGRAM_TOKEN=your_telegram_bot_token
export TODOIST_TOKEN=your_todoist_api_token
export YOUGILE_TOKEN=your_yougile_api_token
export YOUGILE_LOCATION=your_yougile_column_id
export YANDEX_SPEECHKIT_TOKEN=your_yandex_speechkit_token
```

### Файлы токенов

В директории токенов должны быть файлы:
- `todoist_token` — Todoist API токен
- `yougile_token` — Yougile API токен
- `yougile_location` — ID колонки Yougile
- `telegram_token` — Telegram Bot токен
- `yandex_speech_kit_recognizer_token` — Yandex SpeechKit токен
- `telegram_id` — Telegram User ID

## 🛠 Смена сервиса

Сервис выбирается при запуске через аргумент `-s` или переменную окружения `SERVICE` (`todoist` или `yougile`).

## 🐛 Устранение неполадок

- Проверьте, что все необходимые токены и ID колонки (для yougile) заданы.
- Для yougile обязательно наличие файла `yougile_location` или переменной окружения `YOUGILE_LOCATION`.
- Для todoist обязательно наличие файла `todoist_token` или переменной окружения `TODOIST_TOKEN`.
- Логи ошибок выводятся в консоль.

## 📚 Примеры

**Через Telegram:**
```
Пользователь: "Купить молоко завтра в 18:00"
Бот: "✅ Задача создана: Купить молоко завтра в 18:00"
```

**Через командную строку:**
```bash
./create_task.sh -s yougile -t ~/.tokens -l <column_id> "Позвонить клиенту"
# Создана задача: Позвонить клиенту
```

## 📦 Зависимости проекта

Основные Python пакеты:
- `python-telegram-bot==22.1` — Telegram Bot API
- `requests==2.31.0` — HTTP запросы
- `yandex-speechkit==1.5.0` — Распознавание речи
- `pydub==0.25.1` — Обработка аудио
- `SpeechRecognition==3.10.1` — Дополнительные возможности распознавания
- `pydantic==1.10.14` — Для поддержки yougile_api

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

### Сборка deb-пакета с произвольным именем

Для сборки требуется установленный [podman](https://podman.io/):

```bash
# По умолчанию имя пакета self-tracker-bot:
./build_deb.sh

# Или с произвольным именем (например, mybot):
./build_deb.sh mybot
```

В результате появится файл `mybot_1.0.0_all.deb` в корне проекта (или с другим именем).

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
YOUGILE_TOKEN=your_yougile_token   # (только если используете Yougile)
YOUGILE_LOCATION=your_yougile_column_id   # (только если используете Yougile)
YANDEX_SPEECHKIT_TOKEN=your_yandex_token
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
