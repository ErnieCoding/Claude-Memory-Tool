from anthropic.lib.tools import BetaAbstractMemoryTool
from anthropic.types.beta import (
    BetaMemoryTool20250818ViewCommand,
    BetaMemoryTool20250818CreateCommand,
    BetaMemoryTool20250818DeleteCommand,
    BetaMemoryTool20250818InsertCommand,
    BetaMemoryTool20250818RenameCommand,
    BetaMemoryTool20250818StrReplaceCommand,
)
from typing_extensions import override
from pathlib import Path
from services.file_processor import FileProcessor


SYSTEM_PROMPT = """Правила работы с memory tool:

У тебя есть доступ к двум директориям:
1. /user_files/ - для чтения файлов, загруженных пользователем (ТОЛЬКО ДЛЯ ЧТЕНИЯ)
2. /responses/ - для сохранения сгенерированных ответов (можно создавать, редактировать, удалять файлы)

- В /user_files/ ты можешь ТОЛЬКО просматривать файлы через view
- В /responses/ ты можешь использовать все операции: view, create, delete, insert, rename, str_replace
- Ты можешь создавать файлы для отслеживания прогресса ТОЛЬКО с названием progress.txt. По окончанию ответа на запрос пользователя ты ОБЯЗАТЕЛЬНО ДОЛЖЕН удалить файл с прогрессом
- Конечный ответ всегда должен быть записан в /responses/
- Ответ должен содержаться ТОЛЬКО в одном файле. ЗАПРЕЩЕНО создание нескольких файлов с ответом на один запрос

## 📝 ПРАВИЛА ИСПОЛЬЗОВАНИЯ КОМАНД:

### view(path)
Просматривает содержимое файла или директории.
✅ Используй для чтения файлов из /user_files/ и /responses/

### create(path, file_text)
Создаёт новый файл с содержимым.
✅ Используй только в /responses/
❌ НЕ используй если файл уже существует

### delete(path)
Удаляет файл.
✅ Используй только в /responses/

### insert(path, insert_line, insert_text)
Вставляет текст на конкретную строку.
✅ Используй только в /responses/

### rename(old_path, new_path)
Переименовывает файл.
✅ Используй только в /responses/

### str_replace(path, old_str, new_str)
Заменяет УНИКАЛЬНЫЙ фрагмент текста.
✅ Используй только в /responses/
❌ old_str должен быть УНИКАЛЬНЫМ (встречается РОВНО 1 РАЗ)
❌ ЗАПРЕЩЕНО: old_str="" (пустая строка)

## ⚠️ ВАЖНО:
- Всегда отвечай на русском языке
- Сохраняй конечный результат в /responses/
- Используй понятные имена файлов с расширением .txt
- Во время ответа на запросы используй ТОЛЬКО информацию из контекста, предоставленный пользователем. Если вопрос общий и предполагает использование внешних реесурсов и контекста - ты можешь использовать другие источники.
"""


class MemoryTool(BetaAbstractMemoryTool):
    def __init__(self, user_files_dir: Path, responses_dir: Path):
        super().__init__()
        self.user_files_dir = user_files_dir
        self.responses_dir = responses_dir
        self.file_processor = FileProcessor()

        self.user_files_dir.mkdir(parents=True, exist_ok=True)
        self.responses_dir.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, path: str) -> tuple[Path, bool]:
        """
        Валидирует путь и возвращает (full_path, read_only)
        """
        if path.startswith("/user_files"):
            relative_path = path[len("/user_files"):].lstrip("/")
            full_path = self.user_files_dir / relative_path if relative_path else self.user_files_dir
            read_only = True
        elif path.startswith("/responses"):
            relative_path = path[len("/responses"):].lstrip("/")
            full_path = self.responses_dir / relative_path if relative_path else self.responses_dir
            read_only = False
        else:
            raise ValueError(f"Путь должен начинаться с /user_files или /responses, получено: {path}")

        try:
            if read_only:
                full_path.resolve().relative_to(self.user_files_dir.resolve())
            else:
                full_path.resolve().relative_to(self.responses_dir.resolve())
        except ValueError as e:
            raise ValueError(f"Путь {path} выходит за пределы разрешенной директории") from e

        return full_path, read_only

    @override
    def view(self, command: BetaMemoryTool20250818ViewCommand) -> str:
        full_path, _ = self._validate_path(command.path)

        if full_path.is_dir():
            items = []
            try:
                for item in sorted(full_path.iterdir()):
                    if item.name.startswith("."):
                        continue
                    items.append(f"{item.name}/" if item.is_dir() else item.name)

                if not items:
                    return f"Директория: {command.path}\n(пустая)"

                return f"Директория: {command.path}\n" + "\n".join([f"- {item}" for item in items])
            except Exception as e:
                raise RuntimeError(f"Не удалось прочитать директорию {command.path}: {e}") from e

        elif full_path.is_file():
            try:
                content = self.file_processor.process_file(full_path)

                lines = content.splitlines()
                view_range = command.view_range

                if view_range:
                    start_line = max(1, view_range[0]) - 1
                    end_line = len(lines) if view_range[1] == -1 else view_range[1]
                    lines = lines[start_line:end_line]
                    start_num = start_line + 1
                else:
                    start_num = 1

                numbered_lines = [f"{i + start_num:4d}: {line}" for i, line in enumerate(lines)]
                return "\n".join(numbered_lines)
            except Exception as e:
                raise RuntimeError(f"Не удалось прочитать файл {command.path}: {e}") from e
        else:
            raise RuntimeError(f"Путь не найден: {command.path}")

    @override
    def create(self, command: BetaMemoryTool20250818CreateCommand) -> str:
        full_path, read_only = self._validate_path(command.path)

        if read_only:
            raise PermissionError(f"Нельзя создавать файлы в /user_files: {command.path}")

        if command.file_text is None:
            command.file_text = ""

        if full_path.exists():
            raise FileExistsError(f"Файл уже существует: {command.path}")

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(command.file_text, encoding="utf-8")
        return f"Файл успешно создан: {command.path}"

    @override
    def delete(self, command: BetaMemoryTool20250818DeleteCommand) -> str:
        full_path, read_only = self._validate_path(command.path)

        if read_only:
            raise PermissionError(f"Нельзя удалять файлы в /user_files: {command.path}")

        if not full_path.exists():
            raise FileNotFoundError(f"Файл не найден: {command.path}")

        full_path.unlink()
        return f"Файл успешно удален: {command.path}"

    @override
    def insert(self, command: BetaMemoryTool20250818InsertCommand) -> str:
        full_path, read_only = self._validate_path(command.path)

        if read_only:
            raise PermissionError(f"Нельзя изменять файлы в /user_files: {command.path}")

        if not full_path.is_file():
            raise FileNotFoundError(f"Файл не найден: {command.path}")

        if command.insert_text is None:
            command.insert_text = ""

        content = full_path.read_text(encoding="utf-8")
        lines = content.splitlines(keepends=True)

        insert_line = command.insert_line
        if insert_line < 0 or insert_line > len(lines):
            raise ValueError(f"Неверный номер строки: {insert_line}")

        lines.insert(insert_line, command.insert_text + "\n")
        full_path.write_text("".join(lines), encoding="utf-8")
        return f"Текст вставлен на строку {insert_line} в {command.path}"

    @override
    def rename(self, command: BetaMemoryTool20250818RenameCommand) -> str:
        old_path, read_only = self._validate_path(command.old_path)

        if read_only:
            raise PermissionError(f"Нельзя переименовывать файлы в /user_files: {command.old_path}")

        if not old_path.exists():
            raise FileNotFoundError(f"Файл не найден: {command.old_path}")

        new_path, _ = self._validate_path(command.new_path)

        if new_path.exists():
            raise FileExistsError(f"Файл с таким именем уже существует: {command.new_path}")

        old_path.rename(new_path)
        return f"Файл переименован: {command.old_path} → {command.new_path}"

    @override
    def str_replace(self, command: BetaMemoryTool20250818StrReplaceCommand) -> str:
        full_path, read_only = self._validate_path(command.path)

        if read_only:
            raise PermissionError(f"Нельзя изменять файлы в /user_files: {command.path}")

        if not full_path.is_file():
            raise FileNotFoundError(f"Файл не найден: {command.path}")

        if command.old_str is None or command.new_str is None:
            if command.old_str is None:
                raise ValueError(f"old_str не может быть None")
            if command.new_str is None:
                raise ValueError(f"new_str не может быть None")

        if command.old_str == "":
            raise ValueError("old_str не может быть пустой строкой! Используй insert()")

        content = full_path.read_text(encoding="utf-8")
        count = content.count(command.old_str)

        if count == 0:
            raise ValueError(f"Текст не найден в {command.path}")
        elif count > 1:
            raise ValueError(f"Текст встречается {count} раз в {command.path}. old_str должен быть уникальным")

        new_content = content.replace(command.old_str, command.new_str)
        full_path.write_text(new_content, encoding="utf-8")

        return f"Файл {command.path} успешно изменен"
