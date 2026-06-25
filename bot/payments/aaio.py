import logging
import aiohttp
import hashlib
from bot.core.exceptions import FailedCreatePayment, FailedParseResponse

logger = logging.getLogger(__name__)


class Aaio:
    def __init__(self, merchant_id: str, secret_key_1: str, api_key: str, base_url: str):
        self._merchant_id = merchant_id
        self._secret_key_1 = secret_key_1
        self._api_key = api_key
        self._base_url = base_url

    def _sign_order(self, amount: float, currency: str, order_id: str) -> str:
        raw_string = f'{self._merchant_id}:{amount}:{currency}:{self._secret_key_1}:{order_id}'
        return hashlib.sha256(raw_string.encode()).hexdigest()

    async def create_invoice(self, amount: float, order_id: str, currency: str, lang: str) -> tuple[str, str] | None:
        params = {
            'merchant_id': self._merchant_id,
            'amount': amount,
            'order_id': order_id,
            'sign': self._sign_order(amount, currency, order_id),
            'currency': currency,
            'lang': lang
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with aiohttp.ClientSession() as client:
            async with client.post(self._base_url + 'merchant/get_pay_url', data=params, headers=headers) as response:
                if response.status != 200:
                    raise FailedCreatePayment()

                json_object = await response.json()

                pay_url: str = json_object['url']
                invoice_id = pay_url.split('invoice_uid=')[1].split('&')[0]

                if invoice_id is None:
                    return None

                return pay_url, invoice_id

    async def get_order_info(self, order_id: str) -> str:
        params = {
            'merchant_id': self._merchant_id,
            'order_id': order_id
        }

        headers = {
            'Accept': 'application/json',
            'X-Api-Key': self._api_key
        }

        async with aiohttp.ClientSession() as client:
            async with client.get(self._base_url + 'api/info-pay', headers=headers, params=params) as response:
                if response.status != 200:
                    raise FailedParseResponse()

                json_object = await response.json()
                expired_date = json_object['expired_date']
                return expired_date

    async def get_valid_ip_address(self) -> list[str]:
        async with aiohttp.ClientSession() as client:
            async with client.get(self._base_url + 'api/public/ips') as response:
                if response.status != 200:
                    raise FailedParseResponse()

                json_object = await response.json()
                ip_address = json_object['list']
                return ip_address
