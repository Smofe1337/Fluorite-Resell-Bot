from config import Config
from typing import Dict
import hashlib

def verify_hash(params: Dict[str, any]) -> bool:
    received_hash = params.pop('hash')
    sorted_params = sorted(params.items(), key=lambda x: x[0])

    values = [str(value) for _, value, in sorted_params]
    values.append(Config.NICEPAY_SECRET_KEY)

    hash_string = '{np}'.join(values)
    hash = hashlib.sha256(hash_string.encode()).hexdigest()

    return hash == received_hash


def verif_sign(hash: str, amount: str, currency: str, order_id: str) -> bool:
    raw_srting = f'{Config.AAIO_MERCHANT_ID}:{amount}:{currency}:{Config.AAIO_SECRET_KEY_2}:{order_id}'    
    local_hash = hashlib.sha256(raw_srting.encode()).hexdigest()
        
    return hash == local_hash
