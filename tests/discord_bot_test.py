import unittest

from discord_bot.discord_bot import DiscordBot

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


if __name__ == "__main__":
    unittest.main()
