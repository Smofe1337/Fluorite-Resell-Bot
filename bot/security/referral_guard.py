from collections import defaultdict, deque
from time import time
from config import Config
import random
import logging

logger = logging.getLogger(__name__)


def generate_captcha() -> tuple[str, int]:
    op = random.choice(['+', '-', '*'])
    if op == '*':
        a, b = random.randint(2, 10), random.randint(2, 10)
    else:
        a, b = random.randint(10, 50), random.randint(10, 50)
    if op == '-' and a < b:
        a, b = b, a
    answer = {'+': a + b, '-': a - b, '*': a * b}[op]
    return f"{a} {op} {b}", answer


class ReferralGuard:
    def __init__(self):
        self._timestamps: dict[int, deque] = defaultdict(deque)
        self._captcha_mode: set[int] = set()
        self._pending_users: dict[int, int] = {}
        self._captcha_data: dict[int, dict] = {}

    def check(self, inviter_id: int) -> str:
        now = time()
        ts = self._timestamps[inviter_id]
        ts.append(now)

        while ts and ts[0] < now - Config.ATTACK_WINDOW:
            ts.popleft()

        count = len(ts)

        if count >= Config.ATTACK_THRESHOLD:
            self._captcha_mode.discard(inviter_id)
            return 'attack'

        recent = sum(1 for t in ts if t >= now - Config.CAPTCHA_WINDOW)
        if recent >= Config.CAPTCHA_THRESHOLD or inviter_id in self._captcha_mode:
            self._captcha_mode.add(inviter_id)
            return 'captcha'

        return 'ok'

    def set_captcha(self, user_id: int, inviter_id: int, answer: int):
        self._pending_users[user_id] = inviter_id
        self._captcha_data[user_id] = {
            'answer': answer,
            'created_at': time(),
            'inviter_id': inviter_id,
        }

    def verify_captcha(self, user_id: int, user_answer: int) -> str:
        data = self._captcha_data.get(user_id)
        if not data:
            return 'expired'

        if time() - data['created_at'] > Config.CAPTCHA_TIMEOUT:
            self._cleanup_user(user_id)
            return 'expired'

        if user_answer == data['answer']:
            self._cleanup_user(user_id)
            return 'ok'

        return 'wrong'

    def get_captcha_inviter(self, user_id: int) -> int | None:
        data = self._captcha_data.get(user_id)
        return data['inviter_id'] if data else None

    def get_pending_for_inviter(self, inviter_id: int) -> list[int]:
        return [uid for uid, iid in self._pending_users.items() if iid == inviter_id]

    def cleanup_inviter(self, inviter_id: int) -> list[int]:
        pending = self.get_pending_for_inviter(inviter_id)
        for uid in pending:
            self._cleanup_user(uid)
        self._timestamps.pop(inviter_id, None)
        self._captcha_mode.discard(inviter_id)
        return pending

    def is_pending(self, user_id: int) -> bool:
        return user_id in self._captcha_data

    def _cleanup_user(self, user_id: int):
        self._pending_users.pop(user_id, None)
        self._captcha_data.pop(user_id, None)
