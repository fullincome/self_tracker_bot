#!/usr/bin/env python3
"""
Утилита для просмотра колонок (sections) в проектах Todoist
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
        
        print("Колонки в проектах Todoist:")
        print("=" * 60)
        
        for project in projects:
            project_id = project.get('id', 'N/A')
            project_name = project.get('name', 'Без названия')
            
            print(f"\n📁 Проект: {project_name} (ID: {project_id})")
            print("-" * 40)
            
            # Получаем колонки для этого проекта
            sections = client.get_sections(project_id)
            
            if not sections:
                print("  (Нет колонок - используется стандартный вид)")
            else:
                for i, section in enumerate(sections, 1):
                    section_id = section.get('id', 'N/A')
                    section_name = section.get('name', 'Без названия')
                    order = section.get('order', 0)
                    
                    # Определяем дефолтную колонку
                    default_marker = " (по умолчанию)" if i == 1 else ""
                    
                    print(f"  {i}. ID: {section_id} | Название: {section_name} | Порядок: {order}{default_marker}")
        
        print("\n" + "=" * 60)
        print("💡 Использование:")
        print("- Задачи без указания колонки создаются в первой колонке проекта")
        print("- Можно указать колонку в тексте: 'задача в колонке В работе проекта Разработка'")
        print("- Колонки доступны только в проектах с включенным Kanban-видом")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 