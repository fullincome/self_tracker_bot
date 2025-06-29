import requests
from typing import Dict, Any
import json
import re
import logging

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
Верни результат в формате JSON с ключами:
content (текст задачи),
due_string (срок, если есть; может быть в формате "завтра", "сегодня", "послезавтра" и или в формате даты, например, "2025-06-30"),
priority (1-4, если есть),
labels (список, если есть).

Если параметр не найден — не включай его в JSON. Но content заполняй всегда! Даже если понять смысловую часть задачи не просто, небольшой текст всегда лучше, чем ничего.

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
                params = json.loads(match.group(0))
                params['description'] = text.strip()
                # Проверяем, что есть ключ 'content'
                if 'content' not in params:
                    params['content'] = "Новая задача"
                return params
            except Exception:
                pass
        # Если не удалось распарсить JSON или нет ключа content, возвращаем дефолт
        return {"content": "Новая задача", "description": text.strip()}

    def extract_yougile_task_params(self, text: str) -> Dict[str, Any]:
        prompt = f"""
Ты — помощник, который извлекает параметры для создания задачи в Yougile из пользовательского текста.
Верни результат в формате JSON с ключами:
title (текст задачи; если срок указан, то добавь его в квадратные скобки, например, "Сделать отчёт [завтра]")

Даже если понять смысловую часть задачи и выделить title не просто, небольшой текст в нем вернуть всегда лучше, чем ничего.

Пример:
Вход: Срочно сделать отчёт до 14.06.2025
Выход: {{"title": "Сделать отчёт [завтра]"}}

Вход: Позвонить клиенту завтра
Выход: {{"title": "Позвонить клиенту [завтра]"}}

Вход: Купить хлеб
Выход: {{"title": "Купить хлеб"}}

По аналогии разбери следующий вход.

Вход: {text}
Выход:
"""
        answer = self.ask(prompt)
        match = re.search(r'\{.*\}', answer, re.DOTALL)
        if match:
            try:
                params = json.loads(match.group(0))
                params['description'] = text.strip()
                if 'title' not in params:
                    params['title'] = "Новая задача"
                return params
            except Exception:
                pass
        return {"title": "Новая задача", "description": text.strip()} 