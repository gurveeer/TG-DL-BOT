#!/usr/bin/env python3
"""
Unit tests for FloodWait handling and rate limiting.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pyrogram.errors import FloodWait


class TestRateLimiter:
    """Test the RateLimiter token-bucket implementation."""

    def test_rate_limiter_init(self):
        """Test RateLimiter initialization."""
        from core.bot import RateLimiter
        limiter = RateLimiter(rate=1.0, per=1.0, burst=5)
        assert limiter.rate == 1.0
        assert limiter.per == 1.0
        assert limiter.burst == 5

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_within_burst(self):
        """Test acquiring tokens within burst limit."""
        from core.bot import RateLimiter
        limiter = RateLimiter(rate=1.0, per=1.0, burst=5)
        
        # First 5 acquisitions should be immediate (no wait)
        for i in range(5):
            await limiter.acquire("test_key")
        # 6th should wait
        # Note: this is hard to test without mocking time

    @pytest.mark.asyncio
    async def test_rate_limiter_per_key(self):
        """Test that rate limiter tracks per key."""
        from core.bot import RateLimiter
        limiter = RateLimiter(rate=1.0, per=1.0, burst=5)
        
        await limiter.acquire("key1")
        await limiter.acquire("key2")
        # Different keys should have independent allowances
        assert limiter._allowance.get("key1", 0) != limiter._allowance.get("key2", 0)


class TestSafeSendMessage:
    """Test safe_send_message function."""

    @pytest.mark.asyncio
    async def test_safe_send_message_success(self):
        """Test successful send without FloodWait."""
        from core.bot import safe_send_message
        
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock(return_value="success")
        
        result = await safe_send_message(mock_client, 123, "test message")
        assert result == "success"
        mock_client.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_send_message_flood_wait_retry(self):
        """Test retry on FloodWait exception."""
        from core.bot import safe_send_message
        
        mock_client = AsyncMock()
        # First call raises FloodWait, second succeeds
        mock_client.send_message = AsyncMock(
            side_effect=[
                FloodWait(5),
                "success"
            ]
        )
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await safe_send_message(mock_client, 123, "test message", max_retries=2)
        
        assert result == "success"
        assert mock_client.send_message.call_count == 2

    @pytest.mark.asyncio
    async def test_safe_send_message_max_retries(self):
        """Test that max retries limit is respected."""
        from core.bot import safe_send_message
        
        mock_client = AsyncMock()
        mock_client.send_message = AsyncMock(side_effect=FloodWait(100))
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await safe_send_message(mock_client, 123, "test message", max_retries=2)
        
        assert result is None
        assert mock_client.send_message.call_count == 3  # 0, 1, 2


class TestSafeExecuteSend:
    """Test safe_execute_send wrapper."""

    @pytest.mark.asyncio
    async def test_safe_execute_send_success(self):
        """Test successful execute without errors."""
        from core.bot import safe_execute_send
        
        async def mock_send(*args, **kwargs):
            return "result"
        
        result = await safe_execute_send(123, mock_send)
        assert result == "result"

    @pytest.mark.asyncio
    async def test_safe_execute_send_flood_wait_handling(self):
        """Test FloodWait handling in execute_send."""
        from core.bot import safe_execute_send
        
        call_count = [0]
        
        async def mock_send(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise FloodWait(5)
            return "result"
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await safe_execute_send(123, mock_send, max_retries=3)
        
        assert result == "result"
        assert call_count[0] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
