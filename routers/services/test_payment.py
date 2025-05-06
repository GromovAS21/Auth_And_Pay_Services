import hashlib
import uuid

from routers.auth import SECRET_KEY

transaction_id = uuid.uuid4()  # Эмуляция создания транзакции с уникальным идентификатором

data = {
    "transaction_id": str(transaction_id),
    "account_id": 1, # Указываем идентификатор счета
    "user_id": 11, # Указываем идентификатор пользователя
    "amount": 10000.0, # Указываем сумму пополнения
}

payload = f"{data["account_id"]}{data["amount"]}{data["transaction_id"]}{data["user_id"]}{SECRET_KEY}"
expected_signature = hashlib.sha256(payload.encode()).hexdigest()

print(transaction_id) # Для вставки в запрос
print(expected_signature) # Для вставки в запрос
