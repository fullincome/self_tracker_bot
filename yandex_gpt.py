import requests
from typing import Dict, Any, Optional
import json
import re
import logging

class YandexGPT:
    def __init__(self, apikey: str, folder_id: str, todoist_client=None):
        self.apikey = apikey
        self.folder_id = folder_id
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.todoist_client = todoist_client

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
        """
        Извлекает параметры для создания задачи в Todoist и преобразует их в формат API
        
        Args:
            text (str): Пользовательский текст
            
        Returns:
            Dict[str, Any]: Параметры для API Todoist (с project_id, section_id вместо project_name, section_name)
        """
        prompt = f"""
Ты — помощник, который извлекает параметры для создания задачи в Todoist из пользовательского текста. 
Верни результат в формате JSON с ключами:
content (текст задачи),
due_string (срок, если есть; может быть в формате "завтра", "сегодня", "послезавтра" и или в формате даты, например, "2025-06-30"),
priority (1-4, если есть),
labels (список, если есть),
project_name (название проекта в котором нужно создать задачу, если упоминается в тексте; не перепутай с названием задачи или проекта, по которому создаем задачу),
section_name (название колонки в проекте, если упоминается в тексте; например "В работе", "Готово", "Бэклог").

Если параметр не найден — не включай его в JSON. Но content заполняй всегда! Даже если понять смысловую часть задачи не просто, небольшой текст всегда лучше, чем ничего.

Пример:
Вход: Завтра купить молоко, важно
Выход: {{"content": "Купить молоко", "due_string": "завтра", "priority": 4}}

Вход: Позвонить маме
Выход: {{"content": "Позвонить маме"}}

Вход: Сделать отчёт в проекте "Работа"
Выход: {{"content": "Сделать отчёт", "project_name": "Работа"}}

Вход: Добавить задачу в колонку "В работе" проекта "Разработка"
Выход: {{"content": "Новая задача", "project_name": "Разработка", "section_name": "В работе"}}

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
                
                # Преобразуем project_name и section_name в project_id и section_id
                params = self._resolve_project_and_section_ids(params)
                
                return params
            except Exception:
                pass
        # Если не удалось распарсить JSON или нет ключа content, возвращаем дефолт
        default_params = {"content": "Новая задача", "description": text.strip()}
        return self._resolve_project_and_section_ids(default_params)

    def _resolve_project_and_section_ids(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразует project_name и section_name в project_id и section_id
        
        Args:
            params (Dict[str, Any]): Параметры с project_name/section_name
            
        Returns:
            Dict[str, Any]: Параметры с project_id/section_id
        """
        if not self.todoist_client:
            # Если клиент не передан, возвращаем как есть
            return params
        
        # Обрабатываем project_name
        if 'project_name' in params:
            project_name = params.pop('project_name')
            project = self.todoist_client.get_project_by_name(project_name)
            if project:
                params['project_id'] = project['id']
                
                # Обрабатываем section_name, если есть
                if 'section_name' in params:
                    section_name = params.pop('section_name')
                    section = self.todoist_client.get_section_by_name(section_name, project['id'])
                    if section:
                        params['section_id'] = section['id']
        
        # Удаляем section_name, если он остался (проект не найден или секция не найдена)
        if 'section_name' in params:
            params.pop('section_name')

        return params

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