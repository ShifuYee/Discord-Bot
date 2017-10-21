from discord_bot.discord_bot import DiscordBot


if __name__ == "__main__":
    bot = DiscordBot()
    # Load the config file and set instance variables based on configs
    bot.setup()
    # Establish a connection to gateway and run event loop
    bot.run()
