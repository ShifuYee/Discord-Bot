import asyncio
import json
import requests
import websockets

from .opcodes import Opcodes

CONFIG_FILE_PATH = 'configs/config.json'


class DiscordBot:
    """
    Establishes a connection to the discord gateway and handles varied messages
    """

    def __init__(self):
        # instance variables
        self.config = self.load_config()
        self.gateway_ws_url = self.get_gateway()
        self.heartbeat_interval_ms = None
        self.last_seq = None
        self.event_loop = asyncio.get_event_loop()
        self.websocket = None

        # actions
        self.event_loop.run_until_complete(self.gateway_handler())

    @staticmethod
    def load_config():
        """
        Loads the configurations
        :return: dict - the configurations
        """
        with open(CONFIG_FILE_PATH) as f:
            return json.load(f)

    def get_gateway(self):
        """
        Caches a gateway value and retrieves a new URL
        :return: gateway URL
        """
        r = requests.get(self.config["discord_gateway_endpoint"])
        return r.json()['url']

    async def send_json(self, payload):
        asyncio.ensure_future(self.websocket.send(json.dumps(payload)))

    async def handshake(self, message):
        """
        When a websocket connection is opened, Hello payload is received. Then, an Identify payload is sent as
        part of the handshake to authorize this client.

        :param message: dict - hello payload
        """
        self.heartbeat_interval_ms = message["d"]["heartbeat_interval"]
        asyncio.ensure_future(self.heartbeat())

        handshake_identity = self.config["handshake_identity"]
        asyncio.ensure_future(self.send_json({"op": Opcodes.IDENTIFY, "d": handshake_identity}))

    async def heartbeat(self):
        """
        Sends a heartbeat payload every heartbeat interval.
        """
        # await asyncio.sleep(self.heartbeat_interval_ms / 1000.0)
        await asyncio.sleep(5)
        print(self.last_seq)
        asyncio.ensure_future(self.send_json({"op": Opcodes.HEARTBEAT, "d": self.last_seq}))
        asyncio.ensure_future(self.heartbeat())

    async def gateway_handler(self):
        """
        Creates the websocket, receives messages and acts on them.
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
                elif message["op"] == Opcodes.DISPATCH:
                    self.last_seq = message["s"]
                elif message["op"] != Opcodes.HEARTBEAT_ACK:
                    self.last_seq = message["s"]
                else:
                    pass
