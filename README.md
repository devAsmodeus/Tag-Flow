# Tag-Flow

Система автоматического тегирования и ответов на отзывы и вопросы покупателей с маркетплейсов Wildberries, Ozon и Яндекс Маркет.

## Что делает

1. **Собирает** неотвеченные отзывы и вопросы через API маркетплейсов
2. **Тегирует** каждый отзыв с помощью локальной LLM (тональность, тема, срочность)
3. **Генерирует** персонализированный ответ на основе тегов
4. **Отправляет** ответ обратно на маркетплейс

Весь пайплайн работает автоматически по расписанию, без ручного вмешательства.

## Архитектура

Clean Architecture с разделением на слои:

```
src/
├── domain/          # Сущности, интерфейсы, enum-ы, исключения (без зависимостей)
├── services/        # Бизнес-логика (зависит только от domain)
├── adapters/        # Реализации интерфейсов: collectors, senders, llm
├── repositories/    # Работа с PostgreSQL
└── infrastructure/  # Config, DB, миграции, scheduler, logging, DI-контейнер
```

### Паттерны

- **Circuit Breaker** (pybreaker) — защита от каскадных отказов API маркетплейсов и LLM
- **Structured Logging** (structlog) — JSON-логи с контекстом для фильтрации и анализа
- **Retry с exponential backoff** (tenacity) — повторные попытки при сетевых ошибках
- **Bulkhead** — ограничение batch_size на каждый маркетплейс для изоляции нагрузки
- **Версионированные миграции** — SQL-файлы в `migrations/versions/` с трекингом в БД

## Стек

- **Python 3.13** + **uv** для управления зависимостями
- **PostgreSQL** — хранение отзывов, тегов, ответов, лога отправки, метрик
- **Ollama** + **Qwen3 8B** — локальная LLM для тегирования и генерации ответов (CPU)
- **Pydantic v2** — валидация данных и настроек
- **httpx** — HTTP-клиент
- **APScheduler** — запуск по расписанию
- **Docker Compose** — оркестрация app + PostgreSQL + Ollama

## Быстрый старт

### Локально

```bash
# Клонировать и установить зависимости
git clone https://github.com/devAsmodeus/Tag-Flow.git
cd Tag-Flow
uv sync

# Настроить переменные окружения
cp .env.example .env
# Заполнить .env реальными API-ключами

# Установить и запустить Ollama
ollama pull qwen3:8b

# Один прогон пайплайна
uv run python main.py --once

# Запуск по расписанию (каждые 30 мин)
uv run python main.py
```

### Docker Compose

```bash
cp .env.example .env
# Заполнить .env

docker compose up -d
# Скачать модель в Ollama-контейнер:
docker compose exec ollama ollama pull qwen3:8b
```

## Конфигурация

| Переменная | Описание | По умолчанию |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `WB_API_TOKEN` | Токен Wildberries Feedbacks API | — |
| `OZON_CLIENT_ID` | Client-Id Ozon Seller API | — |
| `OZON_API_KEY` | Api-Key Ozon Seller API | — |
| `YM_API_TOKEN` | Api-Key Яндекс Маркет Partner API | — |
| `YM_BUSINESS_ID` | Business ID Яндекс Маркет | — |
| `OLLAMA_URL` | URL Ollama API | `http://localhost:11434` |
| `TAGGER_MODEL` | Модель для тегирования | `qwen3:8b` |
| `RESPONDER_MODEL` | Модель для генерации ответов | `qwen3:8b` |
| `POLL_INTERVAL_MINUTES` | Интервал запуска пайплайна | `30` |
| `MAX_RETRIES` | Макс. попыток отправки ответа | `3` |
| `BATCH_SIZE` | Макс. отзывов за прогон с одного МП | `100` |
| `MODE` | Режим: LOCAL / TEST / PROD | `LOCAL` |
| `LOG_LEVEL` | Уровень логирования | `INFO` |

## Разработка

```bash
# Линтер
uv run ruff check src/ tests/

# Форматирование
uv run ruff format src/ tests/

# Тесты
uv run pytest tests/ -v

# Только миграции
uv run python main.py --migrate
```

## Лицензия

MIT
