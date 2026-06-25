import logging
import aiohttp
from bot.core.exceptions import FailedParseResponse, FailedCreatePayment

logger = logging.getLogger(__name__)


class NicePay:
    def __init__(self, merchant_id: str, secret_key: str, payment_url: str):
        self._merchant_id = merchant_id
        self._secret_key = secret_key
        self._payment_url = payment_url

    async def create_payment(self, order_id: str, email: str, amount: float, currency: str) -> tuple[str, str, int]:
        async with aiohttp.ClientSession() as session:
            data = {
                'merchant_id': self._merchant_id,
                'secret': self._secret_key,
                'order_id': order_id,
                'customer': email,
                'amount': amount * 100,
                'currency': currency.upper()
            }
            async with session.post(url=self._payment_url, data=data) as resp:
                json_data = await resp.json()

                if json_data:
                    status = json_data['status']
                    if status == 'success':
                        payment_id = json_data['data']['payment_id']
                        link = json_data['data']['link']
                        expired = json_data['data']['expired']
                        return payment_id, link, expired
                    else:
                        raise FailedCreatePayment()
                else:
                    raise FailedParseResponse()
