from enum import Enum

class GameStatus(Enum):
    '''All enum values must start with an uppercase letter'''
    SAFE = 'Safe'
    UPDATING = 'Updating'
    