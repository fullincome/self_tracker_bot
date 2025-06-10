#!/bin/bash

# Функция для отображения справки
show_usage() {
    echo "Usage: $0 [OPTIONS] 'Task text'"
    echo ""
    echo "Options:"
    echo "  -t, --token-path PATH    Path to the directory containing .todoist_token file"
    echo "                          (default: \$HOME)"
    echo "  -v, --venv-path PATH     Path to Python virtual environment"
    echo "                          (default: ./myenv)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  TODOIST_TOKEN_PATH      Alternative way to specify token directory path"
    echo "  VENV_PATH              Alternative way to specify virtual environment path"
    echo ""
    echo "Examples:"
    echo "  $0 'Buy groceries'"
    echo "  $0 -t /path/to/tokens 'Call mom'"
    echo "  $0 --token-path /home/user --venv-path /opt/myenv 'Meeting at 3pm'"
}

# Значения по умолчанию
TOKEN_PATH="${TODOIST_TOKEN_PATH:-$HOME}"
VENV_PATH="${VENV_PATH:-./myenv}"
TASK_TEXT=""

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

# Формируем полный путь к файлу токена
TOKEN_FILE="$TOKEN_PATH/.todoist_token"

# Проверяем существование файла с токеном
if [ ! -f "$TOKEN_FILE" ]; then
    echo "Error: Token file not found at $TOKEN_FILE"
    echo "Please make sure the .todoist_token file exists in the specified directory"
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

# Читаем токен из файла
echo "Reading token from: $TOKEN_FILE"
TODOIST_TOKEN=$(cat "$TOKEN_FILE")

# Проверяем, что токен не пустой
if [ -z "$TODOIST_TOKEN" ]; then
    echo "Error: Token file is empty"
    exit 1
fi

# Экспортируем токен в переменную окружения
export TODOIST_TOKEN

# Запускаем Python скрипт с параметром
echo "Creating task: $TASK_TEXT"
python3 todoist_api.py "$TASK_TEXT"

# Сохраняем код выхода Python скрипта
EXIT_CODE=$?

# Деактивируем виртуальное окружение
deactivate

# Выходим с тем же кодом, что и Python скрипт
exit $EXIT_CODE 