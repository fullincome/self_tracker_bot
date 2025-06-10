#!/bin/bash

# Функция для отображения справки
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --token-path PATH    Path to the directory containing token files"
    echo "                          (default: \$HOME)"
    echo "  -v, --venv-path PATH     Path to Python virtual environment"
    echo "                          (default: ./myenv)"
    echo "  -u, --user-id ID         Telegram User ID (overrides file-based ID)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  TODOIST_TOKEN_PATH       Alternative way to specify token directory path"
    echo "  VENV_PATH               Alternative way to specify virtual environment path"
    echo "  TELEGRAM_USER_ID        Alternative way to specify Telegram User ID"
    echo ""
    echo "Required token files in token directory:"
    echo "  .todoist_token                        - Todoist API token"
    echo "  .telegram_todoisttask_token          - Telegram Bot token"
    echo "  .yandex_speech_kit_recognizer_token  - Yandex SpeechKit token"
    echo "  .telegram_id                         - Telegram User ID (optional if -u is used)"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 -t /path/to/tokens"
    echo "  $0 --token-path /home/user --venv-path /opt/myenv"
    echo "  $0 -t /path/to/tokens -u 123456789"
}

# Значения по умолчанию
TOKEN_PATH="${TODOIST_TOKEN_PATH:-$HOME}"
VENV_PATH="${VENV_PATH:-./myenv}"
USER_ID_OVERRIDE=""

# Парсинг аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
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
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option $1"
            show_usage
            exit 1
            ;;
        *)
            echo "Unexpected argument: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Формируем пути к файлам токенов
TODOIST_TOKEN_FILE="$TOKEN_PATH/.todoist_token"
TELEGRAM_TOKEN_FILE="$TOKEN_PATH/.telegram_todoisttask_token"
YANDEX_TOKEN_FILE="$TOKEN_PATH/.yandex_speech_kit_recognizer_token"
TELEGRAM_ID_FILE="$TOKEN_PATH/.telegram_id"

# Проверяем существование файлов с токенами
echo "Checking token files in: $TOKEN_PATH"

if [ ! -f "$TODOIST_TOKEN_FILE" ]; then
    echo "Error: Todoist token file not found at $TODOIST_TOKEN_FILE"
    exit 1
fi

if [ ! -f "$TELEGRAM_TOKEN_FILE" ]; then
    echo "Error: Telegram token file not found at $TELEGRAM_TOKEN_FILE"
    exit 1
fi

if [ ! -f "$YANDEX_TOKEN_FILE" ]; then
    echo "Error: Yandex SpeechKit token file not found at $YANDEX_TOKEN_FILE"
    exit 1
fi

# Проверяем User ID (из параметра или из файла)
if [ -n "$USER_ID_OVERRIDE" ]; then
    TELEGRAM_USER_ID="$USER_ID_OVERRIDE"
    echo "Using Telegram User ID from parameter: $TELEGRAM_USER_ID"
elif [ -f "$TELEGRAM_ID_FILE" ]; then
    TELEGRAM_USER_ID=$(cat "$TELEGRAM_ID_FILE")
    echo "Using Telegram User ID from file: $TELEGRAM_USER_ID"
else
    echo "Error: Telegram User ID not specified and file not found at $TELEGRAM_ID_FILE"
    echo "Use -u option to specify User ID or create .telegram_id file"
    exit 1
fi

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

# Читаем токены из файлов
echo "Reading tokens from files..."
TODOIST_TOKEN=$(cat "$TODOIST_TOKEN_FILE")
TELEGRAM_TOKEN=$(cat "$TELEGRAM_TOKEN_FILE")
YANDEX_SPEECHKIT_TOKEN=$(cat "$YANDEX_TOKEN_FILE")

# Проверяем, что токены не пустые
if [ -z "$TODOIST_TOKEN" ]; then
    echo "Error: Todoist token file is empty"
    exit 1
fi

if [ -z "$TELEGRAM_TOKEN" ]; then
    echo "Error: Telegram token file is empty"
    exit 1
fi

if [ -z "$YANDEX_SPEECHKIT_TOKEN" ]; then
    echo "Error: Yandex SpeechKit token file is empty"
    exit 1
fi

if [ -z "$TELEGRAM_USER_ID" ]; then
    echo "Error: Telegram User ID is empty"
    exit 1
fi

# Экспортируем токены и пользователя в переменные окружения
export TODOIST_TOKEN
export TELEGRAM_TOKEN
export YANDEX_SPEECHKIT_TOKEN
export TELEGRAM_USER_ID

echo "Starting Todoist Telegram Bot..."
echo "Allowed Telegram User ID: $TELEGRAM_USER_ID"

# Запускаем Python скрипт бота
python3 todoist_bot.py

# Сохраняем код выхода Python скрипта
EXIT_CODE=$?

echo "Bot stopped with exit code: $EXIT_CODE"

# Деактивируем виртуальное окружение
deactivate

# Выходим с тем же кодом, что и Python скрипт
exit $EXIT_CODE 