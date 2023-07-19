from enum import Enum, unique


@unique
class SmStatus(Enum):
    INIT = 0
    DISARMED = 1
    ARMED = 2