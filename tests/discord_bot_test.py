import unittest

from discord_bot.discord_bot import DiscordBot

CONFIG_FILE_PATH = "configs/config.json"
TEST_CONFIG_FILE_PATH = "configs/config.json.template"


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.bot = DiscordBot()

    def test_load_config(self):
        config = self.bot.load_config(TEST_CONFIG_FILE_PATH)
        self.assertEqual(config, {
            "discord_api_endpoint": "https://discordapp.com/api/v6",
            "gateway_api_version": 6,
            "gateway_encoding": "json",
            "handshake_identity": {
                "token": "INSERT BOT TOKEN HERE",
                "properties": {
                    "$os": "windows",
                    "$browser": "disco",
                    "$device": "disco"
                },
                "compress": False,
                "large_threshold": 250,
                "shard": [0, 1]
            }
        })

    def test_get_gateway(self):
        config = self.bot.load_config(CONFIG_FILE_PATH)
        gateway = self.bot.get_gateway(config["discord_api_endpoint"],
                                       config["handshake_identity"]["token"])
        self.assertEqual(gateway, "wss://gateway.discord.gg")


if __name__ == "__main__":
    unittest.main()
