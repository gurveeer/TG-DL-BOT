from pyrogram.types import Message
import logging
import os
import shutil
from ..performance import performance_optimizer
from ..managers.download_manager import download_manager
<<<<<<< HEAD
=======
from ..managers.file_manager import file_manager
from ..bot import safe_execute_send
>>>>>>> bf07a5f1b572c91ba24a45691e9118da095d0034

logger = logging.getLogger(__name__)

async def stats_command(client, message: Message):
    """Show performance statistics."""
    logger.info(f"[HANDLER] /stats command received from user {message.from_user.id}")
    try:
        perf_stats = performance_optimizer.get_metrics()
        dl_stats = download_manager.get_stats()

        # Get disk space info
        try:
            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free / (1024**3)
            disk_info = {"free_gb": free_gb, "warning": free_gb < 1.0}
        except Exception:
            disk_info = {"free_gb": 0, "warning": False}
        
        # Get directory stats
        try:
            downloads_dir = "downloads"
            if os.path.exists(downloads_dir):
                total_files = len([f for f in os.listdir(downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))])
                total_size = sum(os.path.getsize(os.path.join(downloads_dir, f)) for f in os.listdir(downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f)))
                dir_stats = {"total_files": total_files, "total_size_mb": total_size / (1024**2)}
            else:
                dir_stats = {"total_files": 0, "total_size_mb": 0}
        except Exception:
            dir_stats = {"total_files": 0, "total_size_mb": 0}

        stats_text = (
            "[METRICS] **Performance Statistics**\n\n"
            f"**Downloads:** {perf_stats['total_downloads']}\n"
            f"**Uploads:** {perf_stats['total_uploads']}\n"
            f"**Data Downloaded:** {perf_stats['total_data_downloaded_mb']} MB\n"
            f"**Data Uploaded:** {perf_stats['total_data_uploaded_mb']} MB\n"
            f"**Avg Download Speed:** {perf_stats['average_download_speed_mbps']} MB/s\n"
            f"**Avg Upload Speed:** {perf_stats['average_upload_speed_mbps']} MB/s\n"
            f"**Success Rate:** {perf_stats['success_rate']}%\n"
            f"**Failed Operations:** {perf_stats['failed_operations']}\n"
            f"**Retry Count:** {perf_stats['retry_count']}\n"
            f"**Uptime:** {perf_stats['uptime_seconds']}s\n\n"
            f"**Download Manager:**\n"
            f"• Max Concurrent: {dl_stats['max_concurrent']}\n"
            f"• Active Tasks: {dl_stats['active_tasks']}\n"
            f"• Available Slots: {dl_stats['available_slots']}\n\n"
            f"**Disk Usage:**\n"
            f"• Files: {dir_stats['total_files']}\n"
            f"• Size: {dir_stats['total_size_mb']:.1f} MB\n"
            f"• Free Space: {disk_info.get('free_gb', 0):.1f} GB"
        )

        if disk_info.get('warning'):
            stats_text += "\n\n[WARNING] Low disk space! Use /cleanup"

        await safe_execute_send(message.chat.id, message.reply_text, stats_text)
    except Exception as e:
        logger.error(f"[HANDLER] Error in /stats handler: {e}")
        await safe_execute_send(message.chat.id, message.reply_text, f"[ERROR] Could not retrieve stats: {str(e)[:100]}")
