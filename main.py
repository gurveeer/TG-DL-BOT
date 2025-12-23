"""
Main entry point for the Telegram Message Saver Bot.
"""

import sys
import asyncio

# Fix for Python 3.10+ asyncio event loop issue with Pyrogram
# This must be done BEFORE importing pyrogram
if sys.platform == 'win32':
    # For Windows, use the default event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
else:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

from core.bot import main

if __name__ == "__main__":
    main()
