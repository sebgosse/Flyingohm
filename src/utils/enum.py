from enum import Enum, unique


@unique
class SmStatus(Enum):
    INIT = 0
    DISARMED = 1
    ARMED = 2
    
@unique
class EventStatus(Enum):
    INIT_TO_DISARMED = 0
    DISARMED_TO_ARMED = 1
    ARMED_TO_DISARMED = 2
    
@unique
class ScreenStatus(Enum):
    ACTIF = "ACTIF"
    INACTIF = "INACTIF"
    UNKNOWN = "UNKNOWN"
    