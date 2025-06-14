import requests
from typing import Dict, Any
import json
import re

class YandexGPT:
    def __init__(self, apikey: str, folder_id: str):
        self.apikey = apikey
        self.folder_id = folder_id
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def ask(self, prompt: str, max_tokens: int = 300) -> str:
        headers = {
            "Authorization": f"Api-Key {self.apikey}",
            "Content-Type": "application/json"
        }
        data = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": str(max_tokens)
            },
            "messages": [
                {"role": "user", "text": prompt}
            ]
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["result"]["alternatives"][0]["message"]["text"]

    def extract_todoist_task_params(self, text: str) -> Dict[str, Any]:
        prompt = f"""
Ты — помощник, который извлекает параметры для создания задачи в Todoist из пользовательского текста. 
Верни результат в формате JSON с ключами: content (текст задачи), due_string (срок, если есть), priority (1-4, если есть), labels (список, если есть). Если параметр не найден — не включай его в JSON.

Пример:
Вход: Завтра купить молоко, важно
Выход: {{"content": "Купить молоко", "due_string": "завтра", "priority": 4}}

Вход: Позвонить маме
Выход: {{"content": "Позвонить маме"}}

Вход: {text}
Выход:
"""
        answer = self.ask(prompt)
        match = re.search(r'\{.*\}', answer, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {"content": text.strip()} 