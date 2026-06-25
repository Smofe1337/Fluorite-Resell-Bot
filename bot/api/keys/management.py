from fastapi import APIRouter, Depends
from bot.api.keys.schemes import NewKey, DeleteKey, UpdateKeyStatus
from bot.core.error_handlers import hook_exceptions
from bot.api.dashboard.oauth2.security import get_current_user
from bot.enums.keys import KeyStatus
from bot.database.service.keys import KeysService


class KeysRouter:
    def __init__(self, keys_service: KeysService):
        self._keys_service = keys_service
        self.router = APIRouter(dependencies=[Depends(get_current_user)])
        self._register_routes()

    def _register_routes(self):
        self.router.get('/keys/')(self._get_all_keys)
        self.router.get('/keys/stats/')(self._get_keys_stats)
        self.router.post('/keys/add/')(hook_exceptions(self._add_key))
        self.router.post('/keys/update-status/')(hook_exceptions(self._update_key_status))
        self.router.post('/keys/delete/')(hook_exceptions(self._delete_key))

    async def _get_all_keys(self):
        return await self._keys_service.get_all_keys()

    async def _get_keys_stats(self):
        keys = await self._keys_service.get_all_keys()
        total = len(keys)
        available = sum(1 for k in keys if k.get('status') == KeyStatus.AVAILABLE.value)
        sold = sum(1 for k in keys if k.get('status') == KeyStatus.SOLD.value)
        pending = sum(1 for k in keys if k.get('status') == KeyStatus.PENDING.value)
        received = sum(1 for k in keys if k.get('status') == KeyStatus.RECEIVED.value)

        games = {}
        for k in keys:
            game = k.get('game', 'Unknown')
            if game not in games:
                games[game] = {'total': 0, 'available': 0}
            games[game]['total'] += 1
            if k.get('status') == KeyStatus.AVAILABLE.value:
                games[game]['available'] += 1

        return {
            'total': total,
            'available': available,
            'sold': sold,
            'pending': pending,
            'received': received,
            'by_game': games,
        }

    async def _add_key(self, data: NewKey):
        available_duration = [1, 7, 30]
        if data.duration not in available_duration:
            return {
                'Status': False,
                'Message': f'{data.duration} duration not available. Available: {available_duration}'
            }
        return await self._keys_service.on_new_key(data)

    async def _update_key_status(self, data: UpdateKeyStatus):
        statuses = [s.value for s in KeyStatus]
        if data.status not in statuses:
            return {'Status': False, 'Message': 'Invalid status'}
        await self._keys_service.update_key(data.key, data.status)
        return {'Status': True, 'Message': 'Key status updated successfully'}

    async def _delete_key(self, data: DeleteKey):
        await self._keys_service.delete_key(data.key)
        return {
            'Status': True,
            'Message': 'Key deleted successfully'
        }
