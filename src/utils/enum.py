from enum import unique, Enum


@unique
class SmStateStatus(Enum):
    INIT = 0
    DISARMED = 1
    ARMED = 2