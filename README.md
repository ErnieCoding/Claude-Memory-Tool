# Claude Memory Tool

Веб-приложение для работы с Claude AI с поддержкой расширенного контекста (1M токенов) и Memory Tool для чтения файлов и создания ответов.

## Быстрый запуск

### 1. Клонируйте репозиторий
```bash
git clone <repo-url>
cd Claude-Memory-Tool
cd Claude-Memory-Tool
```

### 2. Настройте API ключ
```bash
# Создайте файл .env и вставьте ваш API ключ от Anthropic
echo "CLAUDE_API=your-api-key-here" > .env
```

### 3. Создайте папки для данных
```bash
mkdir -p storage/user_files storage/responses
```

### 4. Запуск

```bash
docker-compose up -d --build
```

**Development**
```bash
docker-compose -f docker-compose.dev.yml up --build
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
    "query": "",
    "max_tokens": 8000
  }
  ```

- `POST /api/query/stream` - Отправка запроса Claude (streaming)
  - Возвращает Server-Sent Events (SSE)
  - Тот же формат body что и `/api/query`

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