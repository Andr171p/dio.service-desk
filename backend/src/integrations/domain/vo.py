from enum import StrEnum


class Direction(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Transport(StrEnum):
    WEBHOOK = "webhook"
    POLLING = "polling"
