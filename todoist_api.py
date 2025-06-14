import requests
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
# Импортируем YandexGPT
from yandex_gpt import YandexGPT

class TodoistAPI:
    def __init__(self, api_token: str):
        """
        Initialize Todoist API client
        
        Args:
            api_token (str): Your Todoist API token
        """
        self.api_token = api_token
        self.base_url = "https://api.todoist.com/rest/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def create_task(
        self,
        content: str,
        description: Optional[str] = None,
        project_id: Optional[int] = None,
        section_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        order: Optional[int] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[int] = None,
        due_string: Optional[str] = None,
        due_date: Optional[str] = None,
        due_datetime: Optional[str] = None,
        due_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new task in Todoist
        
        Args:
            content (str): The text of the task
            description (str, optional): A description for the task
            project_id (int, optional): The project ID to add the task to
            section_id (int, optional): The section ID to add the task to
            parent_id (int, optional): The parent task ID
            order (int, optional): The order of the task
            labels (List[str], optional): The labels to add to the task
            priority (int, optional): The priority of the task (1-4)
            due_string (str, optional): The due date in natural language
            due_date (str, optional): The due date in YYYY-MM-DD format
            due_datetime (str, optional): The due date and time in ISO 8601 format
            due_lang (str, optional): The language of the due string
            
        Returns:
            Dict[str, Any]: The created task data
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        endpoint = f"{self.base_url}/tasks"
        
        # Prepare the task data
        task_data = {
            "content": content
        }
        
        # Add optional parameters if they are provided
        if description is not None:
            task_data["description"] = description
        if project_id is not None:
            task_data["project_id"] = project_id
        if section_id is not None:
            task_data["section_id"] = section_id
        if parent_id is not None:
            task_data["parent_id"] = parent_id
        if order is not None:
            task_data["order"] = order
        if labels is not None:
            task_data["labels"] = labels
        if priority is not None:
            task_data["priority"] = priority
        if due_string is not None:
            task_data["due_string"] = due_string
        if due_date is not None:
            task_data["due_date"] = due_date
        if due_datetime is not None:
            task_data["due_datetime"] = due_datetime
        if due_lang is not None:
            task_data["due_lang"] = due_lang
            
        try:
            response = requests.post(endpoint, headers=self.headers, json=task_data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create task: {str(e)}")

def main():
    # Проверяем наличие токена в переменных окружения
    api_token = os.getenv('TODOIST_TOKEN')
    if not api_token:
        print("Error: TODOIST_TOKEN environment variable is not set")
        sys.exit(1)

    # Проверяем наличие аргумента с текстом задачи
    if len(sys.argv) < 2:
        print("Error: Task text is required")
        print("Usage: python3 todoist_api.py 'Task text'")
        sys.exit(1)

    # Получаем текст задачи из аргументов командной строки
    task_text = sys.argv[1]

    # Читаем токены YandexGPT
    yandex_gpt_apikey = os.getenv('YANDEX_GPT_APIKEY')
    yandex_folder_id = os.getenv('YANDEX_FOLDER_ID')
    if not yandex_gpt_apikey or not yandex_folder_id:
        print("Error: YANDEX_GPT_APIKEY and YANDEX_FOLDER_ID must be set in environment variables")
        sys.exit(1)

    # Инициализируем LLM
    gpt = YandexGPT(yandex_gpt_apikey, yandex_folder_id)

    # Извлекаем параметры задачи через LLM
    params = gpt.extract_todoist_task_params(task_text)

    # Create API client
    todoist = TodoistAPI(api_token)
    
    # Create a task
    try:
        task = todoist.create_task(**params)
        print(f"Created task: {task['content']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 