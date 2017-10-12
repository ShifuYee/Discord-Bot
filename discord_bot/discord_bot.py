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

    def get_gateway(self, **kwargs):
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
        kwargs = dict(header, **kwargs)
        r = requests.get(self.config["discord_gateway_endpoint"], **kwargs)
        assert 200 == r.status_code, r.reason
        return r.json()['url']

    async def send_json(self, payload):
        asyncio.ensure_future(self.websocket.send(json.dumps(payload)))

    async def handshake(self, message):
        """
        When a websocket connection is opened, Hello payload is received. Then, an Identify/Resume payload is sent as
        part of the handshake to authorize this client.

        :param message: dict - hello payload
        """
        self.heartbeat_interval_ms = message["d"]["heartbeat_interval"]  # seconds
        asyncio.ensure_future(self.heartbeat())
        handshake_identity = self.config["handshake_identity"]
        if not self.session_id:
            asyncio.ensure_future(self.send_json({"op": Opcodes.IDENTIFY, "d": handshake_identity}))
        else:
            asyncio.ensure_future(self.send_json({"op": Opcodes.RESUME,
                                                  "d": {"token": self.config["handshake_identity"]["token"],
                                                        "session_id": self.session_id,
                                                        "seq": self.last_seq}}))

    async def heartbeat(self):
        """
        Sends a heartbeat payload every heartbeat interval and allows messages to be sent.
        """
        await asyncio.sleep(self.heartbeat_interval_ms / 1000.0)
        print("Last Sequence: {}".format(self.last_seq))
        asyncio.ensure_future(self.send_json({"op": Opcodes.HEARTBEAT, "d": self.last_seq}))
        asyncio.ensure_future(self.heartbeat())
        # asyncio.ensure_future(self.send_message("embed": {
        #                                             "title": ("{data[repository][owner_name]}/"
        #                                                       "{data[repository][name]} "
        #                                                       "{data[status_message]}"
        #                                                       ).format(data=data),
        #                                             "type": "rich",
        #                                             "description": ("{data[author_name]} {data[type]} "
        #                                                             "<{data[compare_url]}>"
        #                                                             ).format(data=data),
        #                                             "url": data['build_url']}))

    async def gateway_handler(self):
        """
        Creates the websocket, receives responses and acts on them.
        """
        async with websockets.connect("{}/?v={}&encoding={}".format(self.gateway_ws_url,
                                                                    self.config["gateway_api_version"],
                                                                    self.config["gateway_encoding"])) as websocket:
            self.websocket = websocket
            while True:
                response = await self.websocket.recv()
                response = json.loads(response)
                print("{}: {}".format(Opcodes(response["op"]).name, response))
                if response["op"] == Opcodes.HELLO:
                    asyncio.ensure_future(self.handshake(response))
                elif response["op"] == Opcodes.HEARTBEAT_ACK:
                    pass
                elif response["op"] == Opcodes.INVALID_SESSION:
                    print('Invalid Session')
                elif response["op"] == Opcodes.DISPATCH:
                    self.last_seq = response["s"]
                    event = response["t"]
                    if event == 'READY':
                        self.session_id = response["d"]["session_id"]
                else:
                    print(response)

    async def send_message(self, content):
        """
        Post a message into the given channel
        :param content: message sent
        :return: Fires a 'Message Create' Gateway event
        """
        return requests.post("{}{}/messages".format(self.config["discord_channel_endpoint"],
                                                    self.config["my_channel_id"]),
                             json={"content": content})
