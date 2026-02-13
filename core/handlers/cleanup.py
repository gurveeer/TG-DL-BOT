from pyrogram.types import Message
import logging
import os
import shutil
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def cleanup_command(client, message: Message):
    """Clean up old downloaded files."""
    logger.info(f"[HANDLER] /cleanup command received from user {message.from_user.id}")

    try:
        status_msg = await message.reply_text("[INFO] **Cleaning up old files...**")

        downloads_dir = "downloads"
        if not os.path.exists(downloads_dir):
            await status_msg.edit("[INFO] **No files to clean**\n\nDownloads directory is empty.")
            return

        # Clean files older than 24 hours
        cleaned = 0
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for filename in os.listdir(downloads_dir):
            filepath = os.path.join(downloads_dir, filename)
            if os.path.isfile(filepath):
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_modified < cutoff_time:
                    try:
                        os.remove(filepath)
                        cleaned += 1
                    except Exception as e:
                        logger.warning(f"Could not remove {filename}: {e}")

        # Get updated stats
        total_files = len([f for f in os.listdir(downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))])
        total_size = sum(os.path.getsize(os.path.join(downloads_dir, f)) for f in os.listdir(downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f)))
        
        # Get disk space
        disk_usage = shutil.disk_usage(".")
        free_gb = disk_usage.free / (1024**3)

        cleanup_text = (
            "[SUCCESS] **Cleanup Complete**\n\n"
            f"**Files Removed:** {cleaned}\n"
            f"**Remaining Files:** {total_files}\n"
            f"**Total Size:** {total_size / (1024**2):.1f} MB\n"
            f"**Free Space:** {free_gb:.1f} GB"
        )

        await status_msg.edit(cleanup_text)
    except Exception as e:
        logger.error(f"[HANDLER] Error in /cleanup handler: {e}")
        await message.reply_text(f"[ERROR] Cleanup failed: {str(e)[:100]}")
