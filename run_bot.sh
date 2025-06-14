#!/bin/bash

# Функция для отображения справки
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --env PATH           Path to .env file (default: ./.env)"
    echo "  -v, --venv-path PATH     Path to Python virtual environment (default: ./myenv)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 -e /etc/mybot/.env"
}

# Значения по умолчанию
ENV_PATH=".env"
VENV_PATH="./myenv"

# Требуемые переменные для каждого сервиса
TODOIST_VARS=(TELEGRAM_TOKEN TODOIST_TOKEN YANDEX_SPEECHKIT_TOKEN YANDEX_GPT_APIKEY YANDEX_FOLDER_ID TELEGRAM_USER_ID SERVICE)
YOUGILE_VARS=(TELEGRAM_TOKEN YOUGILE_TOKEN YOUGILE_LOCATION YANDEX_SPEECHKIT_TOKEN YANDEX_GPT_APIKEY YANDEX_FOLDER_ID TELEGRAM_USER_ID SERVICE)

# Парсинг аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENV_PATH="$2"
            shift 2
            ;;
        -v|--venv-path)
            VENV_PATH="$2"
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

if [ ! -f "$ENV_PATH" ]; then
    echo "Error: $ENV_PATH not found."
    echo "Создайте этот файл и заполните переменные. Пример можно посмотреть в .env_template."
    exit 1
fi

# Загружаем переменные из .env
set -o allexport
source "$ENV_PATH"
set +o allexport

if [ -z "$SERVICE" ]; then
    echo "Error: SERVICE is not set in $ENV_PATH (must be 'todoist' or 'yougile')"
    exit 1
fi

if [ "$SERVICE" = "todoist" ]; then
    for var in "${TODOIST_VARS[@]}"; do
        if [ -z "${!var}" ] || [[ "${!var}" == "your_"* ]]; then
            echo "Error: $var is not set in $ENV_PATH (required for todoist)"
            exit 1
        fi
    done
elif [ "$SERVICE" = "yougile" ]; then
    for var in "${YOUGILE_VARS[@]}"; do
        if [ -z "${!var}" ] || [[ "${!var}" == "your_"* ]]; then
            echo "Error: $var is not set in $ENV_PATH (required for yougile)"
            exit 1
        fi
    done
else
    echo "Error: Unknown SERVICE value '$SERVICE' in $ENV_PATH. Use 'todoist' or 'yougile'."
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
source "$VENV_ACTIVATE"

# Обновляем зависимости
pip install --upgrade pip
pip install -r requirements.txt

export SERVICE

echo "Starting Telegram Bot with service: $SERVICE"
echo "Allowed Telegram User ID: $TELEGRAM_USER_ID"

python3 self_tracker_bot.py

EXIT_CODE=$?

echo "Bot stopped with exit code: $EXIT_CODE"

deactivate

exit $EXIT_CODE
