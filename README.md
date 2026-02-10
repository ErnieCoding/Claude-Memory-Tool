# Claude Memory Tool 

# Быстрый запуск

### 1. Клонируйте репозиторий
```bash
git clone <repo-url>
cd Claude-Memory-Tool
```

### 2. Настройте API ключ
```bash
# Отредактируйте .env и вставьте ваш API ключ от Anthropic
# CLAUDE_API=your-api-key-here
```

### 3. Создайте папки для данных
```bash
mkdir -p storage/user_files storage/responses
```

### 4. Запуск
```bash
docker-compose up -d --build
```

## Где хранятся данные?

- **Загруженные файлы**: `storage/user_files/`
- **Ответы Claude**: `storage/responses/`

---

## Структура проекта

```
├── backend/                  
│   ├── api/
│   │   └── routes.py         
│   ├── services/
│   │   ├── memory_tool.py    # Anthropic Memory Tool
│   │   ├── claude_client.py  # Claude API клиент
│   │   └── file_processor.py # Обработка различных форматов
│   ├── config.py             # Конфигурация
│   ├── app.py                
│   └── requirements.txt
│
├── frontend/                 
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUploader.vue    
│   │   │   ├── QueryInput.vue      
│   │   │   └── ResponseViewer.vue  
│   │   ├── services/
│   │   │   └── api.js        # API клиент
│   │   └── App.vue
│   └── package.json
│
├── storage/                  
│   ├── user_files/           # Загруженные файлы (read-only для Claude)
│   └── responses/            # Ответы Claude (read-write)
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf            # Nginx reverse proxy
│
├── docker-compose.yml        # Docker Compose конфигурация
└── README.md
```

---

## API Endpoints

### Файлы
- `POST /api/upload` - Загрузка файлов
- `GET /api/files` - Список загруженных файлов
- `DELETE /api/files/<path>` - Удаление файла
- `POST /api/files/clear` - Очистка всех файлов

### Запросы
- `POST /api/query` - Отправка запроса Claude
  ```json
  {
    "query": "Ваш вопрос",
    "max_tokens": 8000
  }
  ```

### Ответы
- `GET /api/responses` - Список сохранённых ответов
- `GET /api/responses/<path>` - Получение конкретного ответа
- `DELETE /api/responses/<path>` - Удаление ответа

### Системные
- `GET /api/health` - Проверка состояния API

---

## Использование

### 1. Загрузка файлов

**Через веб-интерфейс:**
- Перетащите файлы/папки в область загрузки
- Или нажмите на область для выбора файлов

**Вручную:**
- Скопируйте файлы в `storage/user_files/`
- Файлы сразу будут доступны Claude

**Поддерживаемые форматы:**
- JSON, TXT, XML (текстовые)
- PDF (с извлечением текста)
- CSV, XLSX, XLS (таблицы)

### 2. Работа с Claude

**Memory Tool:**
Claude имеет доступ к двум директориям:
- `/user_files/` - загруженные файлы (только чтение)
- `/responses/` - результаты (чтение и запись)

---

## Конфигурация

### Переменные окружения

В файле `.env`:

```bash
# Обязательно
CLAUDE_API=...

# значения по умолчанию
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

### Модель и лимиты

В `backend/config.py`:

```python
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_BETAS = [
    "context-1m-2025-08-07",           # Расширенный контекст 1 миллион токенов
    "context-management-2025-06-27"    # Управление контекстом
]
ALLOWED_EXTENSIONS = {'.json', '.txt', '.xml', '.pdf', '.csv', '.xlsx', '.xls'}
```
