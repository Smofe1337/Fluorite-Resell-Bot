duration_map_int = {
    'day': 1,
    'week': 7,
    'month': 30
}

duration_map_string = {
    1: 'day',
    7: 'week',
    30: 'month'
}

async def get_days(lang: str, days: int):
    from bot.localization.localizer import localize

    days_map = {
        1: await localize(lang, 'one_day'),
        7: await localize(lang, 'seven_days'),
        30: await localize(lang, 'thirty_days')
    }

    return days_map.get(days)


def get_currency_by_lang(lang: str):
    if lang == 'ru':
        return 'rub'
    else:
        return 'usd'
