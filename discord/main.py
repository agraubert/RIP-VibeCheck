from beymax.bots.core import CoreBot
import os

def init():
    bot = CoreBot()

    @bot.subscribe('message')
    async def on_message(self, message):
        """
        Responds to collected messages
        """
        # Filter based on listening channels
        # Filter out bot users
        # Filter out anything that looks like a command
        # Filter out rich messages (maybe also links)
        # Collect text and anonymous ID (perhaps hash of username or ID)
        pass

    @bot.add_task(300) # 5 minutes
    async def update_status(self):
        """
        Should update the displayed status
        based on current collection process
        """
        pass

    return bot

if __name__ == '__main__':
    init().run(os.environ['DISCORD_TOKEN'])
