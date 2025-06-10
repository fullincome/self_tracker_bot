#!/bin/bash

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 не установлен. Пожалуйста, установите Python3."
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 не установлен. Пожалуйста, установите pip3."
    exit 1
fi

# Создаем виртуальное окружение, если оно еще не существует
if [ ! -d "myenv" ]; then
    echo "Создаем виртуальное окружение myenv..."
    python3 -m venv myenv
fi

# Активируем виртуальное окружение
echo "Активируем виртуальное окружение..."
source myenv/bin/activate

# Обновляем pip
echo "Обновляем pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "Устанавливаем зависимости из requirements.txt..."
pip install -r requirements.txt

echo "Окружение успешно настроено!"
echo "Для активации окружения выполните: source myenv/bin/activate" 