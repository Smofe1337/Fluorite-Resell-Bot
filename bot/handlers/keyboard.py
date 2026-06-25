from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.copy_text_button import CopyTextButton
from bot.database.service.games import GameService
from bot.database.service.keys import KeysService
from bot.enums.coupons import CouponTypes
from bot.localization.localizer import localize
from bot.utils.maps import get_currency_by_lang
from bot.utils.converters import get_usd_price


class KeyBoard:
    def __init__(self, game_service: GameService, keys_service: KeysService):
        self.game_service = game_service
        self.key_service = keys_service
    

    @staticmethod
    async def get_main(lang):
        catalog = KeyboardButton(text=await localize(lang, 'catalog_btn'))
        gift_key = KeyboardButton(text=await localize(lang, 'gift_key_btn'))
        profile = KeyboardButton(text=await localize(lang, 'profile_btn'))
        return ReplyKeyboardMarkup(keyboard=[[catalog, profile], [gift_key]], resize_keyboard=True)
    

    @staticmethod
    async def get_profile(lang: str):
        reset_hwid = InlineKeyboardButton(
            text=await localize(lang, 'reset_hwid_btn'), 
            callback_data='reset_hwid'
        )

        up_balance = InlineKeyboardButton(
            text=await localize(lang, 'top_up_balance_btn'), 
            callback_data='up_balance'
        )

        referral = InlineKeyboardButton(
            text=await localize(lang, 'ref_program_btn'), 
            callback_data='referral_system'
        )
        
        download_order = InlineKeyboardButton(
            text=await localize(lang, 'download_orders_btn'), 
            callback_data='download_orders'
        )
        
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [reset_hwid, up_balance], 
                [download_order],
                [referral]
            ]
        )
    

    async def get_game(self):
        buttons = []
        games = await self.game_service.get_games()

        for name in games:
            has_key = await self.key_service.has_keys(name)
            if has_key:
                buttons.append([InlineKeyboardButton(text=name, callback_data=f'game_{name}')])
        
        if len(buttons) < 1:
            buttons.append([InlineKeyboardButton(text='No keys', callback_data='ke')])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
        

    async def get_price(self, game_name: str, lang: str):
        currency = get_currency_by_lang(lang)
        prices = await self.game_service.get_game_price(game_name, currency, await get_usd_price())
        prices = prices.get(currency)
        has_duration = await self.key_service.has_duration(game_name)
        buttons = []

        if has_duration['1d']:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=await localize(lang, 'day_btn', prices['price_day']), 
                        callback_data=f'{game_name}_price_day'
                    )
                ]
            )
        
        if has_duration['7d']:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=await localize(lang, 'week_btn', prices['price_week']), 
                        callback_data=f'{game_name}_price_week'
                    )
                ]
            )

        if has_duration['30d']:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=await localize(lang, 'month_btn', prices['price_month']), 
                        callback_data=f'{game_name}_price_month'
                    )
                ]
            )

        buttons.append(
            [
                InlineKeyboardButton(
                    text=await localize(lang, 'back_btn'),
                    callback_data='back_to_games'
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    
    async def get_payment(self, game_name: str, price: str, lang: str):
        buttons = [
            [InlineKeyboardButton(text='CryptoBot', callback_data=f'{game_name}_{price}_payment_cryptobot')],
            [InlineKeyboardButton(text='Nicepay', callback_data=f'{game_name}_{price}_payment_nicepay')],
            [InlineKeyboardButton(text='Balance', callback_data=f'{game_name}_{price}_payment_balance')],
            [InlineKeyboardButton(text='Aaio', callback_data=f'{game_name}_{price}_payment_aaio')],
            [
                InlineKeyboardButton(
                    text=await localize(lang, 'back_btn'),
                    callback_data='back_to_duration'
                )
            ]
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    def get_payment_balance():
        buttons = [
            [InlineKeyboardButton(text='CryptoBot', callback_data='payment_cryptobot_balance')],
            [InlineKeyboardButton(text='Nicepay', callback_data='payment_nicepay_balance')],
            [InlineKeyboardButton(text='Aaio', callback_data='payment_aaio_balance')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)


    async def get_pay(self, lang: str, link: str, order_id: str):
        buttons = [
            [InlineKeyboardButton(text=await localize(lang, 'pay_btn'), url=link)],
            [InlineKeyboardButton(text=await localize(lang, 'cancel_order_btn'), callback_data=f'cancel_order:{order_id}')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    def get_copy_button(text_btn: str, text_to_copy: str):
        btn = InlineKeyboardButton(text=text_btn, copy_text=CopyTextButton(text=text_to_copy))
        return InlineKeyboardMarkup(inline_keyboard=[[btn]])
    

    @staticmethod
    def get_copy_button_with_link(text_buttons: tuple[str], text_to_copy: str, link: str):
        copy_btn = InlineKeyboardButton(text=text_buttons[0], copy_text=CopyTextButton(text=text_to_copy))
        link_btn = InlineKeyboardButton(text=text_buttons[1], url=link)
        return InlineKeyboardMarkup(inline_keyboard=[[link_btn], [copy_btn]])


    @staticmethod
    def get_link_button(text_btn: str, link: str):
        btn = InlineKeyboardButton(text=text_btn, url=link)
        return InlineKeyboardMarkup(inline_keyboard=[[btn]])
    

    async def keys_button(self, user_id: int, offset: int = 0, lang: str = 'ru'):
        buttons = []
        keys = await self.key_service.get_all_keys_by_user(user_id)
        limit = 10

        page_keys = keys[offset:offset + limit]

        for key in page_keys:
            buttons.append([InlineKeyboardButton(text=key, callback_data=f'r_hwid:{key}')])

        navigation_buttons = []

        if offset > 0:
            navigation_buttons.append(InlineKeyboardButton(text='<', callback_data=f'keys_page:{offset - limit}'))

        if offset + limit < len(keys):
            navigation_buttons.append(InlineKeyboardButton(text='>', callback_data=f'keys_page:{offset + limit}'))

        if navigation_buttons:
            buttons.append(navigation_buttons)

        buttons.append([InlineKeyboardButton(
            text=await localize(lang, 'back_btn'), callback_data='back_to_profile'
        )])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    def get_balance_payment(order_id: str):
        buttons = [
            [InlineKeyboardButton(text='Pay', callback_data=f'pay_via_balance:{order_id}')],
            [InlineKeyboardButton(text='Cancel', callback_data=f'cancel_order:{order_id}')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    def get_text_button(text_button: tuple, callback_data: tuple, is_need_back: bool = False):
        buttons = []

        buttons.append([InlineKeyboardButton(text=text_button[0], callback_data=callback_data[0])])

        if is_need_back:
            buttons.append([InlineKeyboardButton(text=text_button[1], callback_data=callback_data[1])])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    async def get_back_button(lang: str, game_name: str, duration: str):
        back = InlineKeyboardButton(text=await localize(lang, 'back_to_purchases_btn'),
                                    callback_data=f'back_to_purchases:{game_name}_{duration}')
        
        return InlineKeyboardMarkup(inline_keyboard=[[back]])
    

    @staticmethod
    async def get_confirm_button(lang: str, order_id: str):
        buttons = [
            [InlineKeyboardButton(text=await localize(lang, 'cancel_yes_btn'), callback_data=f'order_confirm_yes:{order_id}')],
            [InlineKeyboardButton(text=await localize(lang, 'cancel_no_btn'), callback_data=f'order_confirm_no:{order_id}')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    async def back_to_catalog(lang: str):
        button = [
            [InlineKeyboardButton(text=await localize(lang, 'back_to_catalog_btn'), callback_data='back_to_games')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=button)
    

    @staticmethod
    def coupone_type():
        coupone_types = [coupone.value for coupone in CouponTypes]
        buttons = []

        for coupone_type in coupone_types:
            buttons.append([
                InlineKeyboardButton(text=coupone_type, callback_data=f'sected_coupon_type:{coupone_type}')
            ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    @staticmethod
    def get_vip_flag():
        buttons = [
            [InlineKeyboardButton(text='Yes', callback_data='vip_flag:yes')],
            [InlineKeyboardButton(text='No', callback_data='vip_flag:no')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    

    async def get_games_coupon(self):
        buttons = []

        games = await self.game_service.get_games()
        for game_name in games:
            buttons.append([InlineKeyboardButton(text=game_name, callback_data=f'selected_game:{game_name}')])

        return InlineKeyboardMarkup(inline_keyboard=buttons)


    @staticmethod
    def get_duration_coupon():
        buttons = [
            [InlineKeyboardButton(text='1 Day', callback_data='selected_duration:1')],
            [InlineKeyboardButton(text='7 Days', callback_data='selected_duration:7')],
            [InlineKeyboardButton(text='31 Days', callback_data='selected_duration:30')]
        ]

        return InlineKeyboardMarkup(inline_keyboard=buttons)
    