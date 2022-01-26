from enum import Enum


class InviteStatus(Enum):
    ACCEPTED = 1
    WAITING = 2


class MembershipStatus(Enum):
    ALLOWED = 1
    WAITING = 2
    DENIED = 3
