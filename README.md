# HTTP Proxy Service

Простой прозрачный HTTP/SOAP-прокси на **FastAPI + httpx**.  
Принимает любые HTTP-запросы (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)  
и пересылает их на целевой сервер **в точно таком же виде** — метод, заголовки, тело, query-параметры.
SOAP-запросы через `/soap` отправляются на отдельный сервер.

---

## Быстрый старт

### 1. Прямой запуск (Python)

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить (переменные можно задать через .env или CLI)
TARGET_HOST=http://my-backend:9000 PROXY_PORT=8080 python proxy.py
```

### 2. Docker

```bash
docker build -t proxy-service .
docker run -p 8080:8080 \
  -e TARGET_HOST=http://my-backend:9000 \
  proxy-service
```

### 3. Docker Compose

```bash
# Скопировать пример конфига
cp .env.example .env
# Отредактировать TARGET_HOST
docker-compose up -d
```

---

## Переменные окружения

| Переменная    | По умолчанию            | Описание                        |
|---------------|-------------------------|---------------------------------|
| `PROXY_HOST`  | `0.0.0.0`               | Адрес прослушивания             |
| `PROXY_PORT`  | `8080`                  | Порт прокси                     |
| `TARGET_HOST` | `http://localhost:9000` | Целевой сервер (без слеша в конце) |
| `SOAP_TARGET_HOST` | `http://localhost:9001` | Отдельный сервер для SOAP-запросов |

---

## SOAP-запросы

Отправьте SOAP envelope методом `POST` на `/soap` либо `/soap/{путь}`.
Прокси сохранит XML-тело, query-параметры, `Content-Type`, `SOAPAction` и другие
заголовки. Префикс `/soap` не добавляется к адресу целевого сервера.

Например, запрос:

```bash
curl http://localhost:8080/soap/CustomerService \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H 'SOAPAction: "GetCustomer"' \
  --data-binary @request.xml
```

будет отправлен на:

```text
${SOAP_TARGET_HOST}/CustomerService
```

Для SOAP 1.2 используйте `Content-Type: application/soap+xml`.

---

## Как работает

```
Клиент  →  POST /api/data?foo=bar   →  Прокси (8080)
                                            ↓
                                   TARGET_HOST/api/data?foo=bar
                                            ↓
                                   Ответ передаётся обратно клиенту

Клиент  →  POST /soap/Service       →  Прокси (8080)
                                            ↓
                                   SOAP_TARGET_HOST/Service
```

- Все заголовки запроса пробрасываются (кроме `host`, `content-length`)
- Тело запроса передаётся без изменений
- Статус-код и заголовки ответа сохраняются
- Hop-by-hop заголовки (`transfer-encoding`, `connection` и др.) удаляются из ответа

---

## Структура файлов

```
proxy-service/
├── proxy.py           # Основной код прокси
├── requirements.txt   # Зависимости Python
├── Dockerfile         # Docker-образ
├── docker-compose.yml # Compose-конфигурация
├── .env.example       # Пример переменных окружения
└── README.md          # Документация
```
