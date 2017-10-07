import json
import requests
import asyncio
import websockets

CONFIG_FILE_PATH = 'configs/config.json'
DISCORD_GATEWAY_ENDPOINT = 'https://discordapp.com/api/v6/gateway'


class DiscordBot:

    def __init__(self):

        # instance variables
        self.config = self.load_config()
        self.gateway_ws_url = self.get_gateway()

        # actions below
        asyncio.get_event_loop().run_until_complete(self.gateway_handler())

    @staticmethod
    def load_config():
        with open(CONFIG_FILE_PATH) as f:
            return json.load(f)

    @staticmethod
    def get_gateway():
        r = requests.get(DISCORD_GATEWAY_ENDPOINT)
        return r.json()['url']

    async def handshake(self, websocket):
        identity_obj = {
            "token": self.config["bot_token"],
            "properties": {
                "$os": "windows",
                "$browser": "disco",
                "$device": "disco"
            },
            "compress": False,
            "large_threshold": 250,
            "shard": [1, 10]
        }
        await websocket.send(json.dumps({"op": 2, "d": identity_obj}))

    async def gateway_handler(self):

        async with websockets.connect("{}/?v={}&encoding={}".format(self.gateway_ws_url,
                                                                    self.config["gateway_api_version"],
                                                                    self.config["gateway_encoding"])) as websocket:
            while True:
                message = await websocket.recv()
                print(message)
                message = json.loads(message)
                if message["op"] == 10:
                    await self.handshake(websocket)


# main entry point
if __name__ == "__main__":
    m = DiscordBot()
