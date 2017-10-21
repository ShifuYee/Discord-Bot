from discord_bot.discord_bot import DiscordBot


if __name__ == "__main__":
    # 3 steps
    # create the bot
    bot = DiscordBot()
    # load the config file and set instance variables based on configs
    bot.setup()
    # establish a connection to gateway and run event loop
    bot.run()
