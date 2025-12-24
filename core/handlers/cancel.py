from pyrogram.types import Message
import logging
from ..bot import user_states, active_downloads, safe_execute_send

logger = logging.getLogger(__name__)

async def cancel_command(client, message: Message):
    """Cancel current operation."""
    logger.info(f"[HANDLER] /cancel command received from user {message.from_user.id}")
    user_id = message.from_user.id

    # Clean up any active state
    user_states.pop(user_id, None)
    active_downloads.pop(user_id, None)

    await safe_execute_send(message.chat.id, message.reply_text, "[OK] **Operation cancelled**\n\nAll current operations have been stopped.")
