from collections import deque
from time import time
from typing import Any
from config import Config
import logging

logger = logging.getLogger(__name__)

NEW_ACCOUNT_ID_THRESHOLD: int = 7_500_000_000


class ChannelGuard:
    def __init__(self) -> None:
        self._joins: deque[float] = deque()
        self._recent_ids: deque[tuple[float, int]] = deque()
        self._baseline: float = 0.0
        self._last_baseline_ts: float = 0.0
        self._raid_until: float = 0.0
        self._primed: bool = False

    def is_primed(self) -> bool:
        return self._primed

    def prime(self, timestamps: list[float]) -> None:
        now: float = time()
        for ts in sorted(timestamps):
            if ts >= now - Config.CHANNEL_RATE_WINDOW:
                self._joins.append(ts)
        self._primed = True

    def register_join(self) -> dict[str, Any]:
        now: float = time()
        self._joins.append(now)
        while self._joins and self._joins[0] < now - Config.CHANNEL_RATE_WINDOW:
            self._joins.popleft()

        rate: int = len(self._joins)

        if self._baseline == 0:
            is_spike: bool = rate >= Config.CHANNEL_RATE_FLOOR
        else:
            is_spike = (
                rate >= Config.CHANNEL_RATE_FLOOR
                and rate > self._baseline * Config.CHANNEL_SPIKE_MULTIPLIER
            )

        if is_spike:
            self._raid_until = now + Config.CHANNEL_RAID_COOLDOWN
        elif rate < Config.CHANNEL_RATE_FLOOR and now - self._last_baseline_ts >= Config.CHANNEL_RATE_WINDOW:
            if self._baseline == 0:
                self._baseline = float(rate)
            else:
                self._baseline = (
                    Config.CHANNEL_BASELINE_ALPHA * rate
                    + (1 - Config.CHANNEL_BASELINE_ALPHA) * self._baseline
                )
            self._last_baseline_ts = now

        return {
            'rate': rate,
            'baseline': round(self._baseline, 2),
            'is_spike': is_spike,
            'raid_mode': now < self._raid_until,
        }

    def is_raid(self) -> bool:
        return time() < self._raid_until

    def register_id(self, user_id: int) -> bool:
        now: float = time()
        self._recent_ids.append((now, user_id))
        while self._recent_ids and self._recent_ids[0][0] < now - Config.CHANNEL_RATE_WINDOW:
            self._recent_ids.popleft()

        near: int = sum(
            1 for _, uid in self._recent_ids
            if abs(uid - user_id) <= Config.CHANNEL_SEQ_ID_GAP
        )
        return near >= Config.CHANNEL_SEQ_ID_CLUSTER

    @staticmethod
    def score_account(user: Any, has_photo: bool) -> tuple[int, list[str]]:
        score: int = 0
        reasons: list[str] = []

        if user.username:
            score += 1
        else:
            reasons.append('no_username')

        if getattr(user, 'is_premium', None):
            score += 2

        if has_photo:
            score += 1
        else:
            reasons.append('no_photo')

        if user.id < NEW_ACCOUNT_ID_THRESHOLD:
            score += 1
        else:
            reasons.append('very_new_id')

        name: str = (user.first_name or '').strip()
        if name and not name.isdigit():
            score += 1
        else:
            reasons.append('empty_name')

        return score, reasons
