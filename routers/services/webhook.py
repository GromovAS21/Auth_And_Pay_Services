import hashlib

from config import SECRET_KEY
from schemas import WebhookRequestSchema


async def verify_signature(data: WebhookRequestSchema) -> bool:
    """Проверяет подпись вебхука"""
    payload = f"{data.account_id}{data.amount}{data.transaction_id}{data.user_id}{SECRET_KEY}"
    expected_signature = hashlib.sha256(payload.encode()).hexdigest()
    return expected_signature == data.signature
