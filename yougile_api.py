import requests
from typing import Optional, Dict, Any

class YougileAPI:
    def __init__(self, api_key: str, default_location: str):
        """
        Инициализация клиента Yougile API
        Args:
            api_key (str): API-ключ Yougile
            default_location (str): ID колонки по умолчанию (обязательный)
        """
        self.api_key = api_key
        self.base_url = "https://yougile.com/data/api-v1"
        self.headers = {
            "Authorization": f"YOUGILE-KEY {self.api_key}",
            "Content-Type": "application/json"
        }
        self.default_location = default_location

    def create_task(
        self,
        title: str,
        location: Optional[str] = None,
        description: Optional[str] = None,
        assigned: Optional[str] = None,
        deadline: Optional[str] = None,
        start_date: Optional[str] = None,
        string_stickers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать задачу в Yougile
        Args:
            title (str): Название задачи
            location (str, optional): ID колонки. Если не указано, используется default_location
            description (str, optional): Описание задачи (html)
            assigned (str, optional): ID пользователей через запятую
            deadline (str, optional): Дедлайн (YYYY-MM-DD или YYYY-MM-DD hh:mm:ss)
            start_date (str, optional): Дата начала (YYYY-MM-DD или YYYY-MM-DD hh:mm:ss)
            string_stickers (dict, optional): Стикеры
        Returns:
            dict: Данные созданной задачи (id и result)
        Raises:
            Exception: Если API вернул ошибку
        """
        if location is None:
            location = self.default_location
        endpoint = f"{self.base_url}/tasks"
        task_data = {
            "title": title,
            "location": location
        }
        if description is not None:
            task_data["description"] = description
        if assigned is not None:
            task_data["assigned"] = assigned
        if deadline is not None:
            task_data["deadline"] = deadline
        if start_date is not None:
            task_data["startDate"] = start_date
        if string_stickers is not None:
            task_data["stringStickers"] = string_stickers

        response = requests.post(endpoint, headers=self.headers, json=task_data)
        data = response.json()
        if data.get("result") != "ok":
            raise Exception(f"Yougile API error: {data.get('error', 'Unknown error')}")
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
    yougile = YougileAPI(api_token, default_location=default_location)
    try:
        task = yougile.create_task(title=task_text)
        print(f"Created task in Yougile: {task_text}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 