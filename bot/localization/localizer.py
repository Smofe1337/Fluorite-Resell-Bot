import json
import os
import logging

logger = logging.getLogger(__name__)


class Localizer:
    def __init__(self, locales_dir: str = 'bot/localization/locales'):
        self._locales_dir = locales_dir
        self._cache: dict[str, dict[str, str]] = {}
        self._mtimes: dict[str, float] = {}
        self._default_lang = 'en'

    def _load_locale(self, lang: str) -> dict[str, str]:
        path = os.path.join(self._locales_dir, f'{lang}.json')
        mtime = os.path.getmtime(path)

        if lang in self._cache and self._mtimes.get(lang) == mtime:
            return self._cache[lang]

        with open(path, 'r', encoding='UTF-8') as f:
            data = json.load(f)

        self._cache[lang] = data
        self._mtimes[lang] = mtime
        return data

    def get(self, lang: str, key: str, *args) -> str:
        if lang not in ['en', 'ru']:
            lang = self._default_lang

        context = self._load_locale(lang)

        if key not in context:
            logger.warning(f'Localization key not found: {key} [{lang}]')
            return key

        return context[key].format(*args)


_localizer = Localizer()


async def localize(lang: str, key: str, *args) -> str:
    return _localizer.get(lang, key, *args)
