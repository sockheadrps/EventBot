import bot
import settings

logger = settings.logging.getLogger("bot")

if __name__ == "__main__":
    bot.run(root_logger=True)
    logger.info(f"User: {bot.user} (ID {bot.user.id})")

