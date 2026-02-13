from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

async def test_command(client, message: Message):
    logger.info(f"[HANDLER] /test command received from user {message.from_user.id}")
    try:
        # Import safe_execute_send from bot module
        from ..bot import safe_execute_send
        
        await safe_execute_send(message.chat.id, message.reply_text, "[OK] **Test Successful!**\n\nBot is responding correctly to commands.")
        logger.info(f"[HANDLER] /test response sent successfully")
    except Exception as e:
        logger.error(f"[HANDLER] Error in /test handler: {e}")
