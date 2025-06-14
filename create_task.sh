#!/bin/bash

# Функция для отображения справки
show_usage() {
    echo "Usage: $0 [OPTIONS] 'Task text'"
    echo ""
    echo "Options:"
    echo "  -s, --service SERVICE    Service to use: todoist or yougile (default: todoist)"
    echo "  -t, --token-path PATH    Path to the directory containing .todoist_token и .yougile_token"
    echo "                          (default: $HOME)"
    echo "  -v, --venv-path PATH     Path to Python virtual environment"
    echo "                          (default: ./myenv)"
    echo "  -l, --location LOCATION  Yougile column id (YOUGILE_DEFAULT_LOCATION) для yougile"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  TODOIST_TOKEN_PATH      Alternative way to specify token directory path"
    echo "  VENV_PATH              Alternative way to specify virtual environment path"
    echo "  YOUGILE_DEFAULT_LOCATION  Default Yougile column id (обязателен для yougile, можно через -l)"
    echo ""
    echo "Examples:"
    echo "  $0 'Buy groceries'"
    echo "  $0 -s yougile -l <column_id> 'Call mom'"
    echo "  $0 --service todoist -t /path/to/tokens 'Meeting at 3pm'"
}

# Значения по умолчанию
SERVICE="todoist"
TOKEN_PATH="${TODOIST_TOKEN_PATH:-$HOME}"
VENV_PATH="${VENV_PATH:-./myenv}"
YOUGILE_LOCATION=""
TASK_TEXT=""

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

if [ "$SERVICE" = "todoist" ]; then
    # Формируем полный путь к файлу токена
    TOKEN_FILE="$TOKEN_PATH/todoist_token"
    if [ ! -f "$TOKEN_FILE" ]; then
        echo "Error: Token file not found at $TOKEN_FILE"
        echo "Please make sure the .todoist_token file exists in the specified directory"
        deactivate
        exit 1
    fi
    # Читаем токен из файла
    echo "Reading token from: $TOKEN_FILE"
    TODOIST_TOKEN=$(cat "$TOKEN_FILE")
    if [ -z "$TODOIST_TOKEN" ]; then
        echo "Error: Token file is empty"
        deactivate
        exit 1
    fi
    export TODOIST_TOKEN
    # Читаем токены YandexGPT
    YANDEX_GPT_APIKEY_FILE="$TOKEN_PATH/yandex_gpt_apikey"
    YANDEX_GPT_FOLDER_ID_FILE="$TOKEN_PATH/yandex_gpt_folder_id"
    if [ ! -f "$YANDEX_GPT_APIKEY_FILE" ]; then
        echo "Error: YandexGPT IAM token file not found at $YANDEX_GPT_APIKEY_FILE"
        deactivate
        exit 1
    fi
    if [ ! -f "$YANDEX_GPT_FOLDER_ID_FILE" ]; then
        echo "Error: YandexGPT folder_id file not found at $YANDEX_GPT_FOLDER_ID_FILE"
        deactivate
        exit 1
    fi
    YANDEX_GPT_APIKEY=$(cat "$YANDEX_GPT_APIKEY_FILE")
    YANDEX_GPT_FOLDER_ID=$(cat "$YANDEX_GPT_FOLDER_ID_FILE")
    if [ -z "$YANDEX_GPT_APIKEY" ]; then
        echo "Error: YandexGPT IAM token file is empty"
        deactivate
        exit 1
    fi
    if [ -z "$YANDEX_GPT_FOLDER_ID" ]; then
        echo "Error: YandexGPT folder_id file is empty"
        deactivate
        exit 1
    fi
    export YANDEX_GPT_APIKEY
    export YANDEX_GPT_FOLDER_ID
    echo "Creating task in Todoist: $TASK_TEXT"
    python3 todoist_api.py "$TASK_TEXT"
    EXIT_CODE=$?
elif [ "$SERVICE" = "yougile" ]; then
    # Формируем путь к файлу токена
    YOUGILE_TOKEN_FILE="$TOKEN_PATH/yougile_token"
    if [ ! -f "$YOUGILE_TOKEN_FILE" ]; then
        echo "Error: Yougile token file not found at $YOUGILE_TOKEN_FILE"
        echo "Please make sure the yougile_token file exists in the specified directory"
        deactivate
        exit 1
    fi
    # Читаем токен из файла
    echo "Reading token from: $YOUGILE_TOKEN_FILE"
    YOUGILE_TOKEN=$(cat "$YOUGILE_TOKEN_FILE")
    if [ -z "$YOUGILE_TOKEN" ]; then
        echo "Error: Yougile token file is empty"
        deactivate
        exit 1
    fi
    export YOUGILE_TOKEN
    # Устанавливаем YOUGILE_LOCATION из аргумента, переменной или файла
    if [ -n "$YOUGILE_LOCATION" ]; then
        export YOUGILE_LOCATION="$YOUGILE_LOCATION"
    elif [ -z "$YOUGILE_LOCATION" ] && [ -f "$TOKEN_PATH/yougile_location" ]; then
        YOUGILE_LOCATION=$(cat "$TOKEN_PATH/yougile_location")
        export YOUGILE_LOCATION
    fi
    if [ -z "$YOUGILE_LOCATION" ]; then
        echo "Error: YOUGILE_LOCATION environment variable is not set (и не передан через -l, и нет файла yougile_location)"
        deactivate
        exit 1
    fi
    echo "Creating task in Yougile: $TASK_TEXT"
    python3 yougile_api.py "$TASK_TEXT"
    EXIT_CODE=$?
else
    echo "Error: Unknown service '$SERVICE'. Use 'todoist' or 'yougile'."
    deactivate
    exit 1
fi

# Деактивируем виртуальное окружение
deactivate

# Выходим с тем же кодом, что и Python скрипт
exit $EXIT_CODE 
