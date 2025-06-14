#!/bin/bash

# Функция для отображения справки
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --service SERVICE    Service to use: todoist or yougile (обязательный)"
    echo "  -t, --token-path PATH    Path to the directory containing token files"
    echo "                          (default: $HOME)"
    echo "  -v, --venv-path PATH     Path to Python virtual environment"
    echo "                          (default: ./myenv)"
    echo "  -u, --user-id ID         Telegram User ID (overrides file-based ID)"
    echo "  -l, --location LOCATION  Yougile column id (YOUGILE_LOCATION) для yougile"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  TODOIST_TOKEN_PATH       Alternative way to specify token directory path"
    echo "  VENV_PATH               Alternative way to specify virtual environment path"
    echo "  TELEGRAM_USER_ID        Alternative way to specify Telegram User ID"
    echo "  YOUGILE_LOCATION  Yougile column id (можно через -l или файл yougile_location)"
    echo ""
    echo "Required token files in token directory:"
    echo "  todoist:  todoist_token, telegram_token, yandex_speech_kit_recognizer_token, telegram_id"
    echo "  yougile:  yougile_token, telegram_token, yandex_speech_kit_recognizer_token, telegram_id"
    echo ""
    echo "Examples:"
    echo "  $0 -s todoist"
    echo "  $0 -s yougile -l <column_id>"
    echo "  $0 -s yougile -t /path/to/tokens -l <column_id>"
}

# Значения по умолчанию
SERVICE=""
TOKEN_PATH="${TODOIST_TOKEN_PATH:-$HOME}"
VENV_PATH="${VENV_PATH:-./myenv}"
USER_ID_OVERRIDE=""
YOUGILE_LOCATION=""

# Парсинг аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -t|--token-path)
            TOKEN_PATH="$2"
            shift 2
            ;;
        -v|--venv-path)
            VENV_PATH="$2"
            shift 2
            ;;
        -u|--user-id)
            USER_ID_OVERRIDE="$2"
            shift 2
            ;;
        -l|--location)
            YOUGILE_LOCATION="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -* )
            echo "Unknown option $1"
            show_usage
            exit 1
            ;;
        * )
            echo "Unexpected argument: $1"
            show_usage
            exit 1
            ;;
    esac
done

if [ -z "$SERVICE" ]; then
    echo "Error: --service (todoist или yougile) обязателен"
    show_usage
    exit 1
fi

# Формируем пути к файлам токенов
TODOIST_TOKEN_FILE="$TOKEN_PATH/todoist_token"
YOUGILE_TOKEN_FILE="$TOKEN_PATH/yougile_token"
TELEGRAM_TOKEN_FILE="$TOKEN_PATH/telegram_token"
YANDEX_TOKEN_FILE="$TOKEN_PATH/yandex_speech_kit_recognizer_token"
TELEGRAM_ID_FILE="$TOKEN_PATH/telegram_id"
YOUGILE_LOCATION_FILE="$TOKEN_PATH/yougile_location"

# Проверяем существование виртуального окружения
VENV_ACTIVATE="$VENV_PATH/bin/activate"
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please create virtual environment or specify correct path with -v option"
    exit 1
fi

# Активируем виртуальное окружение Python
echo "Activating virtual environment: $VENV_PATH"
source "$VENV_ACTIVATE"

# Обновляем зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Проверяем и экспортируем токены по выбранному сервису
if [ "$SERVICE" = "todoist" ]; then
    if [ ! -f "$TODOIST_TOKEN_FILE" ]; then
        echo "Error: Todoist token file not found at $TODOIST_TOKEN_FILE"
        deactivate
        exit 1
    fi
    TODOIST_TOKEN=$(cat "$TODOIST_TOKEN_FILE")
    if [ -z "$TODOIST_TOKEN" ]; then
        echo "Error: Todoist token file is empty"
        deactivate
        exit 1
    fi
    export TODOIST_TOKEN
elif [ "$SERVICE" = "yougile" ]; then
    if [ ! -f "$YOUGILE_TOKEN_FILE" ]; then
        echo "Error: Yougile token file not found at $YOUGILE_TOKEN_FILE"
        deactivate
        exit 1
    fi
    YOUGILE_TOKEN=$(cat "$YOUGILE_TOKEN_FILE")
    if [ -z "$YOUGILE_TOKEN" ]; then
        echo "Error: Yougile token file is empty"
        deactivate
        exit 1
    fi
    export YOUGILE_TOKEN
    if [ -n "$YOUGILE_LOCATION" ]; then
        export YOUGILE_LOCATION="$YOUGILE_LOCATION"
    elif [ -z "$YOUGILE_LOCATION" ] && [ -f "$YOUGILE_LOCATION_FILE" ]; then
        YOUGILE_LOCATION=$(cat "$YOUGILE_LOCATION_FILE")
        export YOUGILE_LOCATION
    fi
    if [ -z "$YOUGILE_LOCATION" ]; then
        echo "Error: YOUGILE_LOCATION environment variable is not set (и не передан через -l, и нет файла yougile_location)"
        deactivate
        exit 1
    fi
else
    echo "Error: Unknown service '$SERVICE'. Use 'todoist' or 'yougile'."
    deactivate
    exit 1
fi

# Проверяем остальные обязательные токены (общие для обоих сервисов)
if [ ! -f "$TELEGRAM_TOKEN_FILE" ]; then
    echo "Error: Telegram token file not found at $TELEGRAM_TOKEN_FILE"
    deactivate
    exit 1
fi
TELEGRAM_TOKEN=$(cat "$TELEGRAM_TOKEN_FILE")
if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "Error: Telegram token file is empty"
    deactivate
    exit 1
fi
export TELEGRAM_TOKEN

if [ ! -f "$YANDEX_TOKEN_FILE" ]; then
    echo "Error: Yandex SpeechKit token file not found at $YANDEX_TOKEN_FILE"
    deactivate
    exit 1
fi
YANDEX_SPEECHKIT_TOKEN=$(cat "$YANDEX_TOKEN_FILE")
if [ -z "$YANDEX_SPEECHKIT_TOKEN" ]; then
    echo "Error: Yandex SpeechKit token file is empty"
    deactivate
    exit 1
fi
export YANDEX_SPEECHKIT_TOKEN

# Проверяем User ID (из параметра или из файла)
if [ -n "$USER_ID_OVERRIDE" ]; then
    TELEGRAM_USER_ID="$USER_ID_OVERRIDE"
    echo "Using Telegram User ID from parameter: $TELEGRAM_USER_ID"
elif [ -f "$TELEGRAM_ID_FILE" ]; then
    TELEGRAM_USER_ID=$(cat "$TELEGRAM_ID_FILE")
    echo "Using Telegram User ID from file: $TELEGRAM_USER_ID"
else
    echo "Error: Telegram User ID not specified and file not found at $TELEGRAM_ID_FILE"
    echo "Use -u option to specify User ID or create telegram_id file"
    deactivate
    exit 1
fi
if [ -z "$TELEGRAM_USER_ID" ]; then
    echo "Error: Telegram User ID is empty"
    deactivate
    exit 1
fi
export TELEGRAM_USER_ID
export SERVICE

echo "Starting Telegram Bot with service: $SERVICE"
echo "Allowed Telegram User ID: $TELEGRAM_USER_ID"

python3 self_tracker_bot.py

EXIT_CODE=$?

echo "Bot stopped with exit code: $EXIT_CODE"

deactivate

exit $EXIT_CODE 