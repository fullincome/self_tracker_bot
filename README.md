# Todoist Telegram Bot

Telegram бот для создания задач в Todoist с поддержкой голосовых сообщений и распознавания речи через Yandex SpeechKit.

## 🚀 Основные возможности

- **Создание задач из текста**: Отправьте текстовое сообщение боту, и он автоматически создаст задачу в Todoist
- **Голосовые сообщения**: Отправьте голосовое сообщение, бот распознает речь и создаст задачу
- **Приватность**: Доступ только для указанного пользователя по Telegram ID
- **Логирование**: Ведение подробных логов работы бота
- **Системный сервис**: Возможность запуска как systemd сервис
- **Гибкая конфигурация**: Поддержка файлов токенов и переменных окружения
- **Командная строка**: Утилита для создания задач без Telegram
- **Deb-пакет**: Автоматизированная сборка и установка

## 📋 Требования

- Python 3.7+
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))
- Todoist API Token (получить в [настройках Todoist](https://todoist.com/app/settings/integrations))
- Yandex SpeechKit API Token (получить в [Yandex Cloud](https://cloud.yandex.ru/))

## 🛠 Установка и настройка

### Быстрый старт (локальная разработка)

1. **Клонирование и настройка окружения**:
   ```bash
   git clone <repository-url>
   cd tgbot_todoist
   ./setup_env.sh
   ```

2. **Настройка токенов** (выберите один из способов):

   **Способ 1: Файл .env (рекомендуется для разработки)**
   ```bash
   # Создайте файл .env в корне проекта
   cat > .env << EOF
   TELEGRAM_TOKEN=your_telegram_bot_token
   TODOIST_TOKEN=your_todoist_api_token
   YANDEX_SPEECHKIT_TOKEN=your_yandex_speechkit_token
   TELEGRAM_USER_ID=your_telegram_user_id
   EOF
   ```

   **Способ 2: Отдельные файлы токенов (для продакшена)**
   ```bash
   # В домашней директории или указанной папке
   echo "your_todoist_token" > ~/.todoist_token
   echo "your_telegram_bot_token" > ~/.telegram_todoisttask_token
   echo "your_yandex_speechkit_token" > ~/.yandex_speech_kit_recognizer_token
   echo "your_telegram_user_id" > ~/.telegram_id
   ```

3. **Запуск бота**:

   **Прямой запуск (с .env файлом)**:
   ```bash
   source myenv/bin/activate
   python3 todoist_bot.py
   ```

   **Через скрипт (с файлами токенов)**:
   ```bash
   # Токены в домашней директории ($HOME)
   ./run_bot.sh
   
   # Токены в другой директории
   ./run_bot.sh -t /path/to/token/directory
   
   # Переопределение User ID
   ./run_bot.sh -u 123456789
   
   # Полная конфигурация
   ./run_bot.sh --token-path /home/user --venv-path ./myenv --user-id 123456789
   ```

### Создание задач из командной строки

Для быстрого создания задач без запуска бота используйте утилиту `create_task.sh`:

```bash
# Базовое использование (токен в $HOME/.todoist_token)
./create_task.sh "Купить продукты"

# Указание пути к токенам
./create_task.sh -t /path/to/tokens "Важная встреча завтра"

# Указание виртуального окружения
./create_task.sh -v /opt/myenv "Задача для работы"

# Полная конфигурация
./create_task.sh --token-path /home/user --venv-path /opt/venv "Комплексная задача"

# Справка по использованию
./create_task.sh --help
```

### Установка через deb-пакет (Linux)

#### Сборка deb-пакета (на macOS/Linux)

1. **Подготовка Docker** (для macOS):
   ```bash
   # Убедитесь, что Docker Desktop установлен и запущен
   ./build_deb.sh
   ```

2. **Результат**: Будет создан файл `todoist-bot_1.0.0_all.deb`

#### Установка на сервере

1. **Копирование пакета на сервер**:
   ```bash
   scp todoist-bot_1.0.0_all.deb username@server:/tmp/
   ```

2. **Установка зависимостей**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-venv
   ```

3. **Установка пакета**:
   ```bash
   sudo dpkg -i todoist-bot_1.0.0_all.deb
   ```

4. **Настройка конфигурации**:
   Отредактируйте файл `/usr/local/bin/todoist-bot/.env`:
   ```bash
   sudo nano /usr/local/bin/todoist-bot/.env
   ```
   
   Заполните своими токенами:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   TODOIST_TOKEN=your_todoist_api_token
   YANDEX_SPEECHKIT_TOKEN=your_yandex_speechkit_token
   TELEGRAM_USER_ID=your_telegram_user_id
   ```

5. **Запуск сервиса**:
   ```bash
   sudo systemctl enable todoist-bot.service
   sudo systemctl start todoist-bot.service
   ```

## 🎯 Использование

### Команды бота

- `/start` - Приветствие и инструкции
- `/help` - Справка по использованию

### Создание задач

1. **Текстовые сообщения**: Просто отправьте текст боту
2. **Голосовые сообщения**: Запишите голосовое сообщение, бот распознает речь и создаст задачу
3. **Командная строка**: Используйте `create_task.sh` для создания задач без Telegram

### Примеры

**Через Telegram:**
```
Пользователь: "Купить молоко завтра в 18:00"
Бот: "✅ Задача создана: Купить молоко завтра в 18:00"
```

**Через командную строку:**
```bash
./create_task.sh "Позвонить клиенту в понедельник"
# Создана задача: Позвонить клиенту в понедельник
```

## ⚙️ Конфигурация

### Переменные окружения

Скрипты поддерживают следующие переменные окружения:

```bash
# Пути к токенам и окружению
export TODOIST_TOKEN_PATH=/path/to/tokens
export VENV_PATH=/path/to/venv
export TELEGRAM_USER_ID=123456789

# Прямые токены (для .env файла)
export TELEGRAM_TOKEN=your_telegram_bot_token
export TODOIST_TOKEN=your_todoist_api_token
export YANDEX_SPEECHKIT_TOKEN=your_yandex_speechkit_token
```

### Файлы токенов

Требуемые файлы в директории токенов:
- `.todoist_token` - Todoist API токен
- `.telegram_todoisttask_token` - Telegram Bot токен
- `.yandex_speech_kit_recognizer_token` - Yandex SpeechKit токен
- `.telegram_id` - Telegram User ID

## 🔧 Управление сервисом

### Команды systemd

```bash
# Запуск сервиса
sudo systemctl start todoist-bot.service

# Остановка сервиса
sudo systemctl stop todoist-bot.service

# Перезапуск сервиса
sudo systemctl restart todoist-bot.service

# Статус сервиса
sudo systemctl status todoist-bot.service

# Автозапуск при загрузке системы
sudo systemctl enable todoist-bot.service

# Отключение автозапуска
sudo systemctl disable todoist-bot.service
```

### Логи

- **Основные логи**: `/var/log/todoist-bot/bot.log`
- **Логи ошибок**: `/var/log/todoist-bot/bot.error.log`
- **Системные логи**: `journalctl -u todoist-bot.service -f`

## 📁 Структура проекта

```
tgbot_todoist/
├── todoist_bot.py          # Основной модуль Telegram бота
├── todoist_api.py          # API клиент для работы с Todoist
├── requirements.txt        # Python зависимости
├── setup_env.sh           # Скрипт настройки виртуального окружения
├── run_bot.sh             # Гибкий скрипт запуска бота
├── create_task.sh         # Утилита создания задач из командной строки
├── build_deb.sh           # Скрипт сборки deb-пакета
├── Dockerfile.build       # Docker конфигурация для сборки
├── debian/                # Структура deb-пакета
│   ├── DEBIAN/
│   ├── etc/systemd/system/
│   ├── usr/local/bin/
│   └── var/log/
├── myenv/                 # Виртуальное окружение Python (создается автоматически)
├── logs/                  # Директория для логов (локальная разработка)
└── __pycache__/          # Кеш Python модулей
```

## 🔐 Безопасность

- **Токены**: Никогда не коммитьте токены в репозиторий
- **Доступ**: Бот работает только с указанным Telegram User ID
- **Файл .env**: Добавлен в `.gitignore` для предотвращения случайного коммита
- **Файлы токенов**: Рекомендуется устанавливать права доступа 600 (`chmod 600 ~/.todoist_token`)
- **Логирование**: Токены не записываются в логи

## 🐛 Устранение неполадок

### Проблемы с зависимостями

```bash
# Переустановка зависимостей
source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Проверка импортов
python3 -c "import telegram, speechkit, pydub, requests; print('All modules OK')"
```

### Проблемы с голосовыми сообщениями

1. Проверьте корректность Yandex SpeechKit токена
2. Убедитесь, что голосовое сообщение записано на русском языке
3. Проверьте наличие временных файлов в директории
4. Убедитесь в наличии всех аудио-зависимостей

### Проблемы с созданием задач

1. Проверьте Todoist API токен
2. Убедитесь в доступности API Todoist
3. Проверьте логи для детальной информации об ошибках

### Проблемы с сервисом

```bash
# Проверка статуса
sudo systemctl status todoist-bot.service

# Просмотр логов
journalctl -u todoist-bot.service --no-pager -l

# Проверка конфигурации
sudo cat /usr/local/bin/todoist-bot/.env
```

### Проблемы с конфигурацией

```bash
# Проверка файлов токенов
ls -la ~/.todoist_token ~/.telegram_todoisttask_token ~/.yandex_speech_kit_recognizer_token ~/.telegram_id

# Проверка содержимого (без отображения токена)
[ -s ~/.todoist_token ] && echo "Todoist token: OK" || echo "Todoist token: MISSING/EMPTY"

# Тест скриптов с отладкой
./run_bot.sh --help
./create_task.sh --help
```

## 📦 Зависимости проекта

Основные Python пакеты:
- `python-telegram-bot==22.1` - Telegram Bot API
- `yandex-speechkit==1.5.0` - Распознавание речи
- `pydub==0.25.1` - Обработка аудио
- `SpeechRecognition==3.10.1` - Дополнительные возможности распознавания
- `requests==2.31.0` - HTTP запросы

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 📞 Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории проекта.
