from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

async def start_command(client, message: Message):
    logger.info(f"[HANDLER] /start command received from user {message.from_user.id}")
    try:
        # Import safe_execute_send from bot module
        from . import bot as bot_module
        if not hasattr(bot_module, 'safe_execute_send'):
            from ..bot import safe_execute_send
        else:
            safe_execute_send = bot_module.safe_execute_send
        
        response = (
            "[START] **Welcome to Telegram Message Saver Bot!**\n\n"
            "[OK] Bot is working perfectly!\n\n"
            "**Quick Commands:**\n"
            "• /download <link> - Download a single message\n"
            "• /batch - Start batch processing\n"
            "• /help - Show all commands\n"
            "• /test - Test bot functionality\n\n"
            "**Status:** All systems operational!\n\n"
            "Send me a message link to get started!"
        )
        # Use safe execute for reply
        await safe_execute_send(message.chat.id, message.reply_text, response)
        logger.info(f"[HANDLER] /start response sent successfully")
    except Exception as e:
        logger.error(f"[HANDLER] Error in /start handler: {e}")
