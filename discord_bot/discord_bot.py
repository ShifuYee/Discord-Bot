import asyncio
import json
import requests
import websockets

from .opcodes import Opcodes

CONFIG_FILE_PATH = 'configs/config.json'
EVENTS = {1: 'READY',
          2: 'RESUMED',
          3: 'CHANNEL_CREATE',
          4: 'CHANNEL_UPDATE',
          5: 'CHANNEL_DELETE',
          6: 'CHANNEL_PINS_UPDATE',
          7: 'GUILD_CREATE',
          8: 'GUILD_UPDATE',
          9: 'GUILD_BAN_ADD',
          10: 'GUILD_BAN_REMOVE',
          11: 'GUILD_EMOJIS_UPDATE',
          12: 'GUILD_INTEGRATIONS_UPDATE',
          13: 'GUILD_MEMBER_ADD',
          14: 'GUILD_MEMBER_REMOVE',
          15: 'GUILD_MEMBER_UPDATE',
          16: 'GUILD_MEMBERS_CHUNK',
          17: 'GUILD_ROLE_CREATE',
          18: 'GUILD_ROLE_UPDATE',
          19: 'GUILD_ROLE_DELETE',
          20: 'MESSAGE_CREATE',
          21: 'MESSAGE_UPDATE',
          22: 'MESSAGE_DELETE',
          23: 'MESSAGE_DELETE_BULK',
          24: 'MESSAGE_REACTION_ADD',
          25: 'MESSAGE_REACTION_REMOVE',
          26: 'MESSAGE_REACTION_REMOVE_ALL',
          27: 'PRESENCE_UPDATE',
          28: 'TYPING_START',
          29: 'USER_UPDATE',
          30: 'VOICE_STATE_UPDATE',
          31: 'VOICE_SERVER_UPDATE',
          32: 'WEBHOOKS_UPDATE'
          }


class DiscordBot:
    """
    Establishes a connection to the discord gateway and handles varied messages
    """

    def __init__(self):
        # instance variables
        self.config = self.load_config()
        self.gateway_ws_url = self.get_gateway
        self.heartbeat_interval_ms = None
        self.last_seq = None
        self.event_loop = asyncio.get_event_loop()
        self.websocket = None
        self.session_id = None

        # actions
        self.event_loop.run_until_complete(self.gateway_handler())
        self.event_loop.close()

    @staticmethod
    def load_config():
        """
        Loads the configurations
        :return: dict - the configurations
        """
        with open(CONFIG_FILE_PATH) as f:
            return json.load(f)

    @property
    def get_gateway(self):
        """
        Caches a gateway value, authenticates, and retrieves a new URL
        :return: gateway URL
        """
        header = {
            "headers": {
                "Authorization": "Bot {}".format(self.config["handshake_identity"]["token"]),
                "User-Agent": "DiscordBot (https://github.com/ShifuYee/Discord-Bot, 0.0.1)"
            }
        }
        r = requests.get(self.config["discord_gateway_endpoint"], header)
        assert (200 == r.status_code), r.reason
        return r.json()['url']

    async def send_json(self, payload):
        asyncio.ensure_future(self.websocket.send(json.dumps(payload)))

    async def handshake(self, message):
        """
        When a websocket connection is opened, Hello payload is received. Then, an Identify/Resume payload is sent as
        part of the handshake to authorize this client.

        :param message: dict - hello payload
        """
        self.heartbeat_interval_ms = message["d"]["heartbeat_interval"]
        asyncio.ensure_future(self.heartbeat())
        handshake_identity = self.config["handshake_identity"]
        if self.session_id:
            asyncio.ensure_future(self.send_json(
                                                {"op": Opcodes.RESUME,
                                                  "d": {"token": self.config["handshake_identity"]["token"],
                                                        "session_id": self.session_id,
                                                        "seq": self.last_seq
                                                        }
                                                 }))
        else:
            asyncio.ensure_future(self.send_json({"op": Opcodes.IDENTIFY, "d": handshake_identity}))

    async def heartbeat(self):
        """
        Sends a heartbeat payload every heartbeat interval.
        """
        await asyncio.sleep(self.heartbeat_interval_ms / 1000.0)
        print("Last Sequence: {}".format(self.last_seq))
        asyncio.ensure_future(self.send_json({"op": Opcodes.HEARTBEAT, "d": self.last_seq}))
        asyncio.ensure_future(self.heartbeat())

    async def gateway_handler(self):
        """
        Creates the websocket, receives responses and acts on them.
        """
        async with websockets.connect("{}/?v={}&encoding={}".format(self.gateway_ws_url,
                                                                    self.config["gateway_api_version"],
                                                                    self.config["gateway_encoding"])) as websocket:
            self.websocket = websocket
            while True:
                message = await self.websocket.recv()
                message = json.loads(message)
                print("{}: {}".format(Opcodes(message["op"]).name, message))
                if message["op"] == Opcodes.HELLO:
                    asyncio.ensure_future(self.handshake(message))
                elif message["op"] == Opcodes.HEARTBEAT_ACK:
                    pass
                elif message["op"] == Opcodes.INVALID_SESSION:
                    self.last_seq = message["s"]
                    print('Invalid Session')
                elif message["op"] == Opcodes.DISPATCH:
                    self.last_seq = message["s"]
                    event = message["t"]
                    if event == EVENTS[1]:
                        self.session_id = message["d"]["session_id"]
                else:
                    print(message)

    async def send_message(self, recipient_id, content):
        """
        Post a message into the given channel
        :param recipient_id: num - the recipient to open a DM channel with
        :param content: obj - message sent
        :return: dict - Fires a 'Message Create' Gateway event
        """
        channel = requests.post("{}", json={"recipient_id": recipient_id}).json()

        return requests.post("{}{}/messages".format(self.config["discord_channel_endpoint"],
                                                    channel["id"],
                             json={"content": content})).json()
