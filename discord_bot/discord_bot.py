import asyncio
import json
import requests
import websockets

from .opcodes import Opcodes


CONFIG_FILE_PATH = 'configs/config.json'
DISCORD_GATEWAY_ENDPOINT = 'https://discordapp.com/api/v6/gateway'


class DiscordBot:
    """
    Establishes a connection to the discord gateway and handles varied messages
    """
    def __init__(self):
        # instance variables
        self.config = self.load_config()
        self.gateway_ws_url = self.get_gateway()
        self.heartbeat_interval = None
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

    @staticmethod
    def get_gateway():
        """
        Caches a gateway value and retrieves a new URL
        :return: gateway URL
        """
        r = requests.get(DISCORD_GATEWAY_ENDPOINT)
        return r.json()['url']

    async def send_json(self, payload):
        await self.websocket.send(json.dumps(payload))

    async def handshake(self, message):
        """
        When a websocket connection is opened, Hello payload is received. Then, an Identify payload is sent as
        part of the handshake to authorize this client.

        :param message: dict - hello payload
        """
        self.heartbeat_interval = message["d"]["heartbeat_interval"]
        await self.heartbeat()

        handshake_identity = self.config["handshake_identity"]
        await self.send_json({"op": Opcodes.IDENTIFY, "d": handshake_identity})

    async def heartbeat(self):
        """
        Sends a heartbeat payload every heartbeat interval.
        """
        # await asyncio.sleep(self.heartbeat_interval / 1000.0)
        await asyncio.sleep(5)
        await self.send_json({"op": Opcodes.HEARTBEAT, "d": self.last_seq})
        self.event_loop.create_task(self.heartbeat())

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
                self.last_seq = message["s"]
                print("{}: {}".format(Opcodes(message["op"]).name, message))
                if message["op"] == Opcodes.HELLO:
                    await self.handshake(message)
                elif message["op"] == Opcodes.DISPATCH:
                    pass
