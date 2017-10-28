import asyncio
import json
import logging
import websockets

from aiohttp import ClientSession
from .discord_bot_exception import DiscordBotException
from .events import Events
from .opcodes import Opcodes


CONFIG_FILE_PATH = "configs/config.json"


class DiscordBot:
    """
    Establishes a connection to the discord gateway and handles varied messages
    """

    def __init__(self):
        # instance variables
        self.config = None
        self.gateway_ws_url = None
        self.heartbeat_interval_ms = None
        self.last_seq = None
        self.logger = None
        self.event_loop = None
        self.websocket = None
        self.session_id = None

    # TODO: Docstrings for setup and runs
    def setup(self):
        self.config = self.load_config(CONFIG_FILE_PATH)

        logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.config["log_level"])

        self.event_loop = asyncio.get_event_loop()
        self.gateway_ws_url = self.event_loop.run_until_complete(self.get_gateway())

    def run(self):
        self.event_loop.run_until_complete(self.gateway_handler())
        self.event_loop.close()

    @staticmethod
    def load_config(config_file_path):
        """
        Loads the configurations
        :return: dict - the configurations
        """
        with open(config_file_path) as f:
            return json.load(f)

    async def get_gateway(self):
        """
        Caches a gateway value, authenticates, and retrieves a new URL
        :return: gateway URL
        """
        # TODO: configurable timeout for all of our REST requests
        async with ClientSession() as session:
            async with session.request("GET", "{}/gateway".format(self.config["discord_api_endpoint"])) as r:
                if r.status == 200:
                    json_response = await r.json()
                    return json_response["url"]
                else:
                    raise DiscordBotException(
                        f"Expected gateway URL, received HTTP status code: {r.status} instead of 200, aborting program."
                    )

    # TODO: Docstring
    async def send_json(self, payload):
        asyncio.ensure_future(self.websocket.send(json.dumps(payload)))

    async def handshake(self):
        """
        When a websocket connection is opened, Hello payload is received. Then, an Identify/Resume payload is sent as
        part of the handshake to authorize this client.
        """
        handshake_identity = self.config["handshake_identity"]
        if self.session_id:
            asyncio.ensure_future(self.send_json(
                {
                    "op": Opcodes.RESUME,
                    "d": {
                        "token": self.config["handshake_identity"]["token"],
                        "session_id": self.session_id,
                        "seq": self.last_seq
                    }
                }
            ))
        else:
            asyncio.ensure_future(self.send_json(
                {
                    "op": Opcodes.IDENTIFY,
                    "d": handshake_identity
                }
            ))

    async def heartbeat(self):
        """
        Sends a heartbeat payload every heartbeat interval.
        """
        await asyncio.sleep(self.heartbeat_interval_ms / 1000.0)
        self.logger.info("Last Sequence: {}".format(self.last_seq))
        asyncio.ensure_future(self.send_json(
            {
                "op": Opcodes.HEARTBEAT,
                "d": self.last_seq
            }
        ))
        asyncio.ensure_future(self.heartbeat())

    async def hello_handler(self, message):
        """
        Does the following methods when the Opcode is "HELLO"
        :param message: Hello message
        """
        self.heartbeat_interval_ms = message["d"]["heartbeat_interval"]
        asyncio.ensure_future(self.heartbeat())
        asyncio.ensure_future(self.handshake())

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
                self.logger.info("{}: {}".format(Opcodes(message["op"]).name, message))
                if message["s"] is not None:
                    self.last_seq = message["s"]

                if message["op"] == Opcodes.HELLO:
                    asyncio.ensure_future(self.hello_handler(message))
                elif message["op"] == Opcodes.HEARTBEAT_ACK:
                    pass
                elif message["op"] == Opcodes.INVALID_SESSION:
                    self.logger.warning("Invalid Session")
                elif message["op"] == Opcodes.DISPATCH:
                    event = message["t"]
                    if event == Events.READY:
                        self.session_id = message["d"]["session_id"]
                else:
                    self.logger.exception("Unexpected opcode {}: {}".format(message["op"], message))

    # TODO: Remove this test code
    # async def send_message(self, recipient_id, content):
    #     """
    #     Post a message into the given channel
    #     :param recipient_id: num - the recipient to open a DM channel with
    #     :param content: obj - message sent
    #     :return: dict - Fires a "Message Create" Gateway event
    #     """
    #     channel = requests.post("{}", json={"recipient_id": recipient_id}).json()
    #
    #     return requests.post(
    #         "{}/channels/{}/messages".format(
    #             self.config["discord_api_endpoint"], channel["id"]),
    #         json={
    #             "content": content
    #         }).json()
