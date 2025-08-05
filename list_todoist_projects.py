#!/usr/bin/env python3
"""
Утилита для просмотра проектов в Todoist
"""

import os
import sys
from todoist_api import TodoistAPI

def main():
    # Проверяем наличие токена в переменных окружения
    api_token = os.getenv('TODOIST_TOKEN')
    if not api_token:
        print("Error: TODOIST_TOKEN environment variable is not set")
        sys.exit(1)

    # Создаем клиент
    client = TodoistAPI(api_token)
    
    try:
        # Получаем список проектов
        projects = client.get_projects()
        
        if not projects:
            print("Проекты не найдены")
            return
        
        print("Доступные проекты в Todoist:")
        print("-" * 50)
        
        for project in projects:
            project_id = project.get('id', 'N/A')
            name = project.get('name', 'Без названия')
            color = project.get('color', 'default')
            parent_id = project.get('parent_id')
            
            # Определяем уровень вложенности
            indent = ""
            if parent_id:
                indent = "  "  # Дочерний проект
            
            print(f"{indent}ID: {project_id} | Название: {name} | Цвет: {color}")
        
        print("-" * 50)
        print(f"Всего проектов: {len(projects)}")
        print("\nДля использования проекта по умолчанию добавьте в .env:")
        print("TODOIST_DEFAULT_PROJECT_ID=<ID_проекта>")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 