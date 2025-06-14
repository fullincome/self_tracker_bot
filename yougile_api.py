import requests
from typing import Optional, Dict, Any
import logging, json

class YougileAPI:
    def __init__(self, api_key: str, location: str):
        """
        Инициализация клиента Yougile API
        Args:
            api_key (str): API-ключ Yougile
            location (str): ID колонки по умолчанию (обязательный)
        """
        self.api_key = api_key
        self.base_url = "https://yougile.com/api-v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.location = location

    def create_task(
        self,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создать задачу в Yougile (api-v2)
        Args:
            title (str): Название задачи
            description (str, optional): Описание задачи (html)
        Returns:
            dict: Данные созданной задачи (id и result)
        Raises:
            Exception: Если API вернул ошибку
        """
        endpoint = f"{self.base_url}/tasks"
        task_data = {
            "title": title,
            "columnId": self.location
        }
        if description is not None:
            task_data["description"] = description

        response = requests.post(endpoint, headers=self.headers, json=task_data)
        data = response.json()
        if not data.get("id"):
            raise Exception(f"Yougile API error: {data.get('message', 'Unknown error')}")
        return data

if __name__ == "__main__":
    import os
    import sys
    api_token = os.getenv('YOUGILE_TOKEN')
    default_location = os.getenv('YOUGILE_LOCATION')
    if not api_token:
        print("Error: YOUGILE_TOKEN environment variable is not set")
        sys.exit(1)
    if not default_location:
        print("Error: YOUGILE_LOCATION environment variable is not set")
        sys.exit(1)
    if len(sys.argv) < 2:
        print("Error: Task text is required")
        print("Usage: python3 yougile_api.py 'Task text'")
        sys.exit(1)
    task_text = sys.argv[1]
    yougile = YougileAPI(api_token, location=default_location)
    try:
        task = yougile.create_task(title=task_text)
        print(f"Created task in Yougile: {task_text}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
