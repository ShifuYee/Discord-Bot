from enum import IntEnum


class Opcodes(IntEnum):
    """
    Opcodes are based on the Gateway Opcodes from the Discord API:
    https://discordapp.com/developers/docs/topics/gateway
    """
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    STATUS_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    VOICE_SERVER_UPDATE = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
