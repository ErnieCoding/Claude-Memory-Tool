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
        messages: List[BetaMessageParam] = [
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            # Используем beta.messages.tool_runner для работы с MemoryTool
            tool_runner = self.client.beta.messages.tool_runner(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                system=SYSTEM_PROMPT,
                betas=self.betas,
                tools=[self.memory_tool]
            )

            # Итерируемся по tool_runner для получения всех ответов
            final_text = ""
            last_usage = None

            for message in tool_runner:
                for block in message.content:
                    if hasattr(block, 'text'):
                        final_text += block.text

                # Сохраняем usage из последнего сообщения
                if hasattr(message, 'usage'):
                    last_usage = message.usage

            return {
                "success": True,
                "text": final_text,
                "usage": {
                    "input_tokens": last_usage.input_tokens if last_usage else 0,
                    "output_tokens": last_usage.output_tokens if last_usage else 0
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

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

    def process_query_stream(self, query: str, max_tokens: int = 8000):
        """
        Streaming версия обработки запроса с поддержкой MemoryTool

        Args:
            query: Запрос пользователя
            max_tokens: Максимальное количество токенов для ответа

        Yields:
            Словари с частями ответа или ошибками
        """
        messages: List[BetaMessageParam] = [
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            # Используем stream с MemoryTool
            with self.client.beta.messages.stream(
                model=self.model,
                max_tokens=max_tokens,
                messages=messages,
                system=SYSTEM_PROMPT,
                betas=self.betas,
                tools=[self.memory_tool]
            ) as stream:
                for event in stream:
                    # Обрабатываем различные типы событий
                    if hasattr(event, 'type'):
                        if event.type == 'content_block_delta':
                            if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                                yield {
                                    "type": "text_delta",
                                    "text": event.delta.text
                                }
                        elif event.type == 'message_start':
                            yield {
                                "type": "message_start"
                            }
                        elif event.type == 'message_stop':
                            yield {
                                "type": "message_stop"
                            }

                # Отправляем финальное использование токенов
                final_message = stream.get_final_message()
                if hasattr(final_message, 'usage'):
                    yield {
                        "type": "usage",
                        "input_tokens": final_message.usage.input_tokens,
                        "output_tokens": final_message.usage.output_tokens
                    }

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }
