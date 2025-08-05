#!/usr/bin/env python3
"""
Утилита для получения ID проекта и секции Todoist по названию
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

    # Проверяем аргументы
    if len(sys.argv) < 2:
        print("Usage: python3 get_todoist_ids.py <project_name> [section_name]")
        print("Examples:")
        print("  python3 get_todoist_ids.py 'Работа'")
        print("  python3 get_todoist_ids.py 'Разработка' 'В работе'")
        sys.exit(1)

    project_name = sys.argv[1]
    section_name = sys.argv[2] if len(sys.argv) > 2 else None

    # Создаем клиент
    client = TodoistAPI(api_token)
    
    try:
        # Ищем проект
        project = client.get_project_by_name(project_name)
        if not project:
            print(f"❌ Проект '{project_name}' не найден")
            print("\nДоступные проекты:")
            projects = client.get_projects()
            for p in projects:
                print(f"  - {p.get('name', 'Без названия')} (ID: {p.get('id', 'N/A')})")
            sys.exit(1)
        
        project_id = project.get('id')
        project_name_actual = project.get('name', 'Без названия')
        
        print(f"✅ Проект найден: '{project_name_actual}' (ID: {project_id})")
        
        # Если указана секция, ищем её
        if section_name:
            section = client.get_section_by_name(section_name, project_id)
            if not section:
                print(f"❌ Секция '{section_name}' в проекте '{project_name_actual}' не найдена")
                print(f"\nДоступные секции в проекте '{project_name_actual}':")
                sections = client.get_sections(project_id)
                if not sections:
                    print("  (Нет секций - используется стандартный вид)")
                else:
                    for s in sections:
                        print(f"  - {s.get('name', 'Без названия')} (ID: {s.get('id', 'N/A')})")
                sys.exit(1)
            
            section_id = section.get('id')
            section_name_actual = section.get('name', 'Без названия')
            
            print(f"✅ Секция найдена: '{section_name_actual}' (ID: {section_id})")
            
            print(f"\n📋 Для .env файла:")
            print(f"TODOIST_DEFAULT_PROJECT_ID={project_id}")
            print(f"TODOIST_DEFAULT_SECTION_ID={section_id}")
            
        else:
            print(f"\n📋 Для .env файла:")
            print(f"TODOIST_DEFAULT_PROJECT_ID={project_id}")
            
            # Показываем доступные секции
            sections = client.get_sections(project_id)
            if sections:
                print(f"\nДоступные секции в проекте '{project_name_actual}':")
                for s in sections:
                    print(f"  - {s.get('name', 'Без названия')} (ID: {s.get('id', 'N/A')})")
                print(f"\nДля установки секции по умолчанию добавьте:")
                print(f"TODOIST_DEFAULT_SECTION_ID=<ID_секции>")
            else:
                print("(В этом проекте нет секций - используется стандартный вид)")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 