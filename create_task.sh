#!/bin/bash

# Функция для отображения справки
show_usage() {
    echo "Usage: $0 [OPTIONS] 'Task text'"
    echo ""
    echo "Options:"
    echo "  -s, --service SERVICE    Service to use: todoist or yougile (default: todoist)"
    echo "  -e, --env PATH           Path to .env file (default: ./env or ./.env)"
    echo "  -v, --venv-path PATH     Path to Python virtual environment (default: ./myenv)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 'Buy groceries'"
    echo "  $0 -s yougile 'Позвонить клиенту'"
    echo "  $0 --service todoist -e /etc/mybot/.env 'Meeting at 3pm'"
}

# Значения по умолчанию
SERVICE="todoist"
ENV_PATH=".env"
VENV_PATH="./myenv"
TASK_TEXT=""

# Требуемые переменные для каждого сервиса
TODOIST_VARS=(TELEGRAM_TOKEN TODOIST_TOKEN YANDEX_SPEECHKIT_TOKEN YANDEX_GPT_APIKEY YANDEX_FOLDER_ID TELEGRAM_USER_ID SERVICE)
YOUGILE_VARS=(TELEGRAM_TOKEN YOUGILE_TOKEN YOUGILE_LOCATION YANDEX_SPEECHKIT_TOKEN YANDEX_GPT_APIKEY YANDEX_FOLDER_ID TELEGRAM_USER_ID SERVICE)

# Парсинг аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
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
            TASK_TEXT="$1"
            shift
            ;;
    esac
done

# Проверяем, передан ли текст задачи
if [ -z "$TASK_TEXT" ]; then
    echo "Error: Task text is required"
    echo ""
    show_usage
    exit 1
fi

# Если .env не найден — выводим подсказку и выходим
if [ ! -f "$ENV_PATH" ]; then
    echo "Error: $ENV_PATH not found."
    echo "Создайте этот файл и заполните переменные. Пример можно посмотреть в .env_template."
    exit 1
fi

# Загружаем переменные из .env
set -o allexport
source "$ENV_PATH"
set +o allexport

# Проверяем нужные переменные для выбранного сервиса
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
    echo "Error: Unknown service '$SERVICE'. Use 'todoist' or 'yougile'."
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

if [ "$SERVICE" = "todoist" ]; then
    echo "Creating task in Todoist: $TASK_TEXT"
    python3 todoist_api.py "$TASK_TEXT"
    EXIT_CODE=$?
elif [ "$SERVICE" = "yougile" ]; then
    echo "Creating task in Yougile: $TASK_TEXT"
    python3 yougile_api.py "$TASK_TEXT"
    EXIT_CODE=$?
fi

deactivate
exit $EXIT_CODE 
