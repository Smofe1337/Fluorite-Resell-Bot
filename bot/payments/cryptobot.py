import logging
import hashlib
import aiohttp

logger = logging.getLogger(__name__)


class CryptoBot:
    def __init__(self, token: str, base_url: str):
        self._token = token
        self._base_url = base_url
        self._headers = {
            'Crypto-Pay-API-Token': token,
            'Content-Type': 'application/json'
        }

    async def create_invoice(self, amount: float, currency: str) -> tuple[int, str] | None:
        async with aiohttp.ClientSession() as session:
            data = {
                'currency_type': 'fiat',
                'fiat': currency,
                'amount': amount,
                'expires_in': 1500,
            }
            async with session.post(url=self._base_url + 'createInvoice', json=data, headers=self._headers) as resp:
                json_data = await resp.json()

                if json_data['ok']:
                    result = json_data['result']
                    invoice_id = result['invoice_id']
                    pay_url = result['mini_app_invoice_url']
                    return invoice_id, pay_url

    async def delete(self, invoice_id: int) -> bool:
        async with aiohttp.ClientSession() as session:
            data = {
                'invoice_id': invoice_id
            }

            async with session.post(url=self._base_url + 'deleteInvoice', headers=self._headers, json=data) as resp:
                json_object = await resp.json()
                if json_object['ok']:
                    if json_object['result']:
                        return True
                    return False
                return False

    def verify_signature(self, body: bytes, signature: str) -> bool:
        import hmac
        secret = hashlib.sha256(self._token.encode()).digest()
        expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
