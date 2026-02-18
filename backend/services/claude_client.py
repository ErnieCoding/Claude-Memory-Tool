from anthropic import Anthropic
from anthropic.types.beta import BetaMessageParam
from typing import List, Dict, Any
from pathlib import Path
from services.memory_tool import MemoryTool, SYSTEM_PROMPT
from config import Config


class ClaudeClient:
    def __init__(self, user_files_dir: Path, responses_dir: Path):
        self.client = Anthropic(api_key=Config.CLAUDE_API_KEY)
        self.memory_tool = MemoryTool(user_files_dir, responses_dir)
        self.model = Config.CLAUDE_MODEL
        self.betas = Config.CLAUDE_BETAS

    def process_query_sync(self, query: str, max_tokens: int = 8000) -> Dict[str, Any]:
        """
        Синхронная версия обработки запроса с поддержкой MemoryTool

        Args:
            query: Запрос пользователя
            max_tokens: Максимальное количество токенов для ответа

        Returns:
            Словарь с результатом обработки
        """
        # Запоминаем файлы ДО выполнения запроса
        files_before = self._get_response_file_paths()

        messages: List[BetaMessageParam] = [
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            tool_runner = self.client.beta.messages.tool_runner(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                system=SYSTEM_PROMPT,
                betas=self.betas,
                tools=[self.memory_tool]
            )

            final_text = ""
            last_usage = None

            for message in tool_runner:
                for block in message.content:
                    if hasattr(block, 'text'):
                        final_text += block.text

                if hasattr(message, 'usage'):
                    last_usage = message.usage

            # Определяем новые файлы ПОСЛЕ выполнения запроса
            files_after = self._get_response_file_paths()
            created_files = [f for f in files_after if f not in files_before]

            # Фильтруем progress.txt из списка созданных файлов
            created_files = [f for f in created_files if not f['name'].lower() == 'progress.txt']

            return {
                "success": True,
                "text": final_text,
                "usage": {
                    "input_tokens": last_usage.input_tokens if last_usage else 0,
                    "output_tokens": last_usage.output_tokens if last_usage else 0
                },
                "created_files": created_files
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_response_file_paths(self) -> List[Dict[str, Any]]:
        """Вспомогательный метод для получения списка файлов в responses"""
        files = []
        for file_path in self.memory_tool.responses_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                rel_path = file_path.relative_to(self.memory_tool.responses_dir)
                files.append({
                    "name": file_path.name,
                    "path": str(rel_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        return files

    def get_available_files(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных файлов в user_files"""
        files = []
        for file_path in self.memory_tool.user_files_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                rel_path = file_path.relative_to(self.memory_tool.user_files_dir)
                files.append({
                    "name": file_path.name,
                    "path": str(rel_path),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix
                })
        return files

    def get_response_files(self) -> List[Dict[str, Any]]:
        """Возвращает список сгенерированных ответов"""
        files = []
        for file_path in self.memory_tool.responses_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                rel_path = file_path.relative_to(self.memory_tool.responses_dir)
                files.append({
                    "name": file_path.name,
                    "path": str(rel_path),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        return sorted(files, key=lambda x: x['modified'], reverse=True)
