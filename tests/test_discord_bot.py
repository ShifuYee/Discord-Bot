import unittest
import asyncio

from discord_bot.discord_bot import DiscordBot

TEST_CONFIG_FILE_PATH = "configs/config.json.template"


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.bot = DiscordBot()

    def test_load_config(self):
        """
        This test verifies the load_config function
        """
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
            },
            "log_level": "INFO",
            "momoi_id": "INSERT MOMOI BOT ID HERE",
            "user_agent": "MomoiBot (https://github.com/ShifuYee/Discord-Bot)"
        })

    def test_get_gateway(self):
        """
        This test verifies the get_gateway function
        """
        self.bot.config = {
            "discord_api_endpoint": "https://discordapp.com/api/v6"
        }
        # TODO: Mock out Discord API endpoint
        loop = asyncio.get_event_loop()
        gateway = loop.run_until_complete(self.bot.get_gateway())
        self.assertEqual(gateway, "wss://gateway.discord.gg")


if __name__ == "__main__":
    unittest.main()
