# README для проекта по созданию пользователей счетов и эмуляции выполнения транзакции в стороннем приложении с записью в БД

---

## Технологии и зависимости

Для работы приложения используются следующие технологии и зависимости:

| Компонент            | Версия   | Назначение                     |
|----------------------|----------|--------------------------------|
| **Python**           | 3.12`    | Основной язык программирования |
| **SQLAlchemy**       | 2.0.40   | ORM для работы с БД            |            
| **FastAPI**          | 0.115.12 | веб-фреймворк                  |                  
| **Pydantic**         | 2.11.4   | валидация данных               |               
| **Uvicorn**          | 0.34.2   | ASGI-сервер                    |                    
| **AsyncPG**          | 0.30.0   | асинхронный драйвер PostgreSQL | 
| **Alembic**          | 1.15.2   | миграции БД                    |                    
| **PyJWT**            | 2.10.1   | JWT-токены                     |                     
| **Passlib**          | 1.7.4    | хэширование паролей            |            
| **Bcrypt**           | 4.0.1    | криптография паролей           |           
| **Email-Validator**  | 2.2.0    | проверка email                 |                 
| **Python-Dotenv**    | 0.9.9    | загрузка `.env`                |                
| **Python-Multipart** | 0.0.20   | обработка форм                 |                 
| **Greenlet**         | 3.2.1    | легковесные корутины           |


---

## Структура базы данных

### Таблицы:

- `users` - пользователи
- `accounts` - счета
- `transactions` - платежи

---

## Для запуска:

### 1. Клонирование репозитория

   ```bash
   git clone https://github.com/GromovAS21/trading_results_parser.git
   cd trading_results_parser
   ```

### 2. Установка зависимостей

- Установите зависимости с помощью Poetry и активируйте виртуальное окружение:
    ```bash
    poetry shell
    poetry install
    ```

### 3. Настройка переменных окружения

- Переименуйте файл [.env.sample](.env.sample) в [.env](.env.sample) и заполните все переменные в этом файле.
- Для заполнения параметра SECRET_KEY используйте команду в терминале:
    ```bash
    openssl rand -base64 32
    ```
- Выведенное значение в терминале вставьте в переменную SECRET_KEY.

### 4. Для запуска с помощью контейнеризации

- Выполните команду:

  ```bash
    docker-compose up -d --build
  ```

### 5. Для запуска без контейнеризации

- В файле [.env](.env) поменяйте значение переменной `DB_HOST` на localhost
- Выполните команды:

  ```bash
    alembic upgrade head # применение миграции 
    uvicorn main:app --reload
  ```

 ## Документация доступна по адресу: http://127.0.0.1:8000/docs

---

# Тестовые данные

## 🔐 Тестовые пользователи

### Администратор

**Username:** `admin`  
**Password:** `Admin123`

### Обычный пользователь

**Username:** `user1`  
**Password:** `User123`

## 💳 Тестирование платежей

- Для генерации тестового request body для эндпоинта `transaction/payment` выполните:

```bash
python -m routers.services.test_payment
  ```

- Выведенные данные скопируйте в request body

### Пример тела запроса:

```
{
  "transaction_id": "f42aab21-8bfc-4384-acea-6b5dba0374a5",
  "account_id": 1,
  "user_id": 2,
  "amount": 20000.0,
  "signature": "12a141db423aab2c521eb9bc5b6676d07537b28729395e3bbaaace3b993965fd"
}
  ```

--- 

## Цитата

> "Большинство хороших программистов делают свою работу не потому, что ожидают оплаты или признания, а потому что
> получают удовольствие от программирования.* - Linus Torvalds

---

Приятного использования! 🚀
