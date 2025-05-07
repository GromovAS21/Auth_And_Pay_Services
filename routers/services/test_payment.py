"""Скрипт-эмуляция создания транзакции с уникальным идентификатором и вычисление подписи из другого сервиса."""

import hashlib
import json
import uuid

from config import SECRET_KEY


transaction_id = uuid.uuid4()  # Эмуляция создания транзакции с уникальным идентификатором

data = {
    "transaction_id": str(transaction_id),
    "account_id": 1,  # Указываем идентификатор счета
    "user_id": 2,  # Указываем идентификатор пользователя
    "amount": 20000.0,  # Указываем сумму пополнения (Должно быть вещественным числом, pydantic приводит к типу float)
}

payload = f"{data["account_id"]}{data["amount"]}{data["transaction_id"]}{data["user_id"]}{SECRET_KEY}"
expected_signature = hashlib.sha256(payload.encode()).hexdigest()
data["signature"] = expected_signature
print(json.dumps(data, indent=2))  # Копируем полученные данные в запрос для эмуляции получения с другого сервиса
