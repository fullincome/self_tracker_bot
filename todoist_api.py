import requests
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
# Импортируем YandexGPT
from yandex_gpt import YandexGPT

class TodoistAPI:
    def __init__(self, api_token: str, default_project_id: Optional[int] = None, default_section_id: Optional[int] = None):
        """
        Initialize Todoist API client
        
        Args:
            api_token (str): Your Todoist API token
            default_project_id (int, optional): Default project ID for new tasks
            default_section_id (int, optional): Default section ID for new tasks
        """
        self.api_token = api_token
        self.default_project_id = default_project_id
        self.default_section_id = default_section_id
        self.base_url = "https://api.todoist.com/api/v1"
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
        
        # Use provided project_id, then default_project_id, then None (Inbox)
        final_project_id = project_id if project_id is not None else self.default_project_id
        if final_project_id is not None:
            task_data["project_id"] = final_project_id
            
        # Use provided section_id, then default_section_id (only if project is specified)
        final_section_id = section_id if section_id is not None else self.default_section_id
        if final_section_id is not None and final_project_id is not None:
            task_data["section_id"] = final_section_id
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
            print(response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            # Retry logic: if due_string was present, try again without it
            if due_string is not None:
                logging.warning(f"Retrying Todoist task creation without due_string due to error: {e}")
                task_data.pop("due_string", None)
                try:
                    response = requests.post(endpoint, headers=self.headers, json=task_data)
                    response.raise_for_status()
                    result = response.json()
                    result["_due_string_failed"] = True
                    return result
                except requests.exceptions.RequestException as e2:
                    raise Exception(f"Failed to create task (even without due_string): {str(e2)}. Original error: {str(e)}")
            raise Exception(f"Failed to create task: {str(e)}")

    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects from Todoist
        
        Returns:
            List[Dict[str, Any]]: List of projects
        """
        endpoint = f"{self.base_url}/projects"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()['results']

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find project by name
        
        Args:
            name (str): Project name to search for
            
        Returns:
            Optional[Dict[str, Any]]: Project data if found, None otherwise
        """
        projects = self.get_projects()
        for project in projects:
            if project.get("name", "").lower() == name.lower():
                return project
        return None

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Find project by ID
        
        Args:
            project_id (int): Project ID to search for
            
        Returns:
            Optional[Dict[str, Any]]: Project data if found, None otherwise
        """
        projects = self.get_projects()
        for project in projects:
            if project.get("id") == project_id:
                return project
        return None

    def get_sections(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get sections (columns) from Todoist
        
        Args:
            project_id (int, optional): Project ID to get sections for. If None, returns all sections.
            
        Returns:
            List[Dict[str, Any]]: List of sections
        """
        endpoint = f"{self.base_url}/sections"
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()['results']

    def get_section_by_name(self, name: str, project_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Find section by name
        
        Args:
            name (str): Section name to search for
            project_id (int, optional): Project ID to search within
            
        Returns:
            Optional[Dict[str, Any]]: Section data if found, None otherwise
        """
        sections = self.get_sections(project_id)
        for section in sections:
            if section.get("name", "").lower() == name.lower():
                return section
        return None

    def get_section_by_id(self, section_id: int, project_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Find section by ID
        
        Args:
            section_id (int): Section ID to search for
            project_id (int, optional): Project ID to search within
            
        Returns:
            Optional[Dict[str, Any]]: Section data if found, None otherwise
        """
        sections = self.get_sections(project_id)
        for section in sections:
            if section.get("id") == section_id:
                return section
        return None

    def get_default_section(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the first section (default column) of a project
        
        Args:
            project_id (int): Project ID
            
        Returns:
            Optional[Dict[str, Any]]: First section data if found, None otherwise
        """
        sections = self.get_sections(project_id)
        if sections:
            return sections[0]  # Первая колонка обычно является дефолтной
        return None

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

    # Create API client
    todoist = TodoistAPI(api_token, os.getenv('TODOIST_DEFAULT_PROJECT_ID'), os.getenv('TODOIST_DEFAULT_SECTION_ID'))
    
    # Инициализируем LLM с клиентом
    gpt = YandexGPT(yandex_gpt_apikey, yandex_folder_id, todoist_client=todoist)

    # Извлекаем параметры задачи через LLM
    params = gpt.extract_todoist_task_params(task_text)
    
    # Create a task
    try:
        task = todoist.create_task(**params)
        print(f"Created task: {task['content']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 