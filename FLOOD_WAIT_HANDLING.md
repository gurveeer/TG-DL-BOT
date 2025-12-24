# FloodWait & Rate Limiting Enhancements

This document describes the FloodWait handling and rate limiting improvements added to the Telegram Message Saver Bot.

## Overview

Telegram API imposes strict rate limits and returns `420 FLOOD_WAIT` errors when too many requests are sent in a short time. This bot now has robust handling to gracefully recover from these rate limits.

## Key Enhancements

### 1. Per-Destination Rate Limiter

**File**: `core/bot.py` → `RateLimiter` class

A token-bucket rate limiter is applied to each chat/destination to throttle message sends:

- **Rate**: 1 token/second (default, configurable)
- **Burst**: 5 tokens (allows short bursts without waiting)
- **Jitter**: Random +0-1 second added to reduce contention

**Configuration**:
```python
# core/config.py
config.rate_limit_rate = 1.0        # tokens per second
config.rate_limit_per = 1.0          # refill period
config.rate_limit_burst = 5          # max tokens in burst
```

**Environment overrides**:
```bash
RATE_LIMIT_RATE=0.5          # 2 msgs per second
RATE_LIMIT_BURST=10          # allow more burst
```

### 2. Safe Send Wrapper (`safe_send_message`)

**Location**: `core/bot.py`

Sends text messages with automatic FloodWait handling:

```python
async def safe_send_message(client, chat_id, text, max_retries=2, max_wait_cap=60):
    """Send with FloodWait retry and rate limiting."""
```

- Catches `FloodWait` exceptions
- Extracts wait time from error message
- Caps maximum wait at `max_wait_cap` (default: 60s)
- Adds jitter to reduce lock-step retries
- Applies per-destination rate limiting before send

**Usage**:
```python
await safe_send_message(bot_client, chat_id, "Hello!")
```

### 3. Safe Execute Wrapper (`safe_execute_send`)

**Location**: `core/bot.py`

Generic wrapper for any send/upload/copy operation:

```python
async def safe_execute_send(chat_id, send_coro, *args, max_retries=3, max_wait_cap=300, **kwargs):
    """Execute send with rate limiting and FloodWait handling."""
```

Used for:
- `message.copy()`
- `send_photo()`, `send_video()`, etc.
- `send_document()`, `send_audio()`, etc.
- All upload operations

**Features**:
- Rate limiting per destination
- Automatic FloodWait retry with jitter
- Exponential backoff for transient errors (2, 4, 8s)
- Configurable retry count and max wait

### 4. Reduced Concurrency

**File**: `core/config.py`

Worker counts reduced to lower API pressure:

```python
config.bot_client_workers = 4         # was 8
config.userbot_client_workers = 2     # was 4
config.max_concurrent_downloads = 2   # was 5 (batch)
```

**Environment overrides**:
```bash
BOT_WORKERS=2                         # reduce to 2
MAX_CONCURRENT_DOWNLOADS=1            # single download
```

### 5. Exponential Backoff & Jitter

All retries use:
- **Exponential backoff**: 2^attempt + random(0, 0.5)
- **Jitter**: Prevents thundering herd
- **Capped wait**: Maximum wait is configurable

### 6. All Handler Commands Protected

**Files**: `core/handlers/*.py`

All `message.reply_text()` calls now use `safe_execute_send`:

- `/start` - uses safe wrapper
- `/test` - uses safe wrapper
- `/help` - uses safe wrapper
- `/download` - uses safe wrapper
- `/stats` - uses safe wrapper
- `/speed` - uses safe wrapper
- `/batch` - uses safe wrapper
- `/cancel` - uses safe wrapper
- `/cleanup` - uses safe wrapper

## Best Practices for Operators

### 1. Monitor FloodWait Events

Enable DEBUG logging to see FloodWait waits:

```bash
# In logs
[WARNING] Flood wait while sending message: sleeping for 72.5s (attempt 1)
[WARNING] Send operation failed (attempt 1): error_text
```

### 2. Tune Rate Limiter for Your Workload

**For high-volume batch downloads** (reduce concurrency):
```bash
RATE_LIMIT_RATE=0.5          # 2 msgs/sec instead of 1
RATE_LIMIT_BURST=3           # smaller burst
BOT_WORKERS=2
MAX_CONCURRENT_DOWNLOADS=1
```

**For low-volume interactive use** (relax limits):
```bash
RATE_LIMIT_RATE=2.0          # 2 msgs/sec
RATE_LIMIT_BURST=10
BOT_WORKERS=8
MAX_CONCURRENT_DOWNLOADS=3
```

### 3. Monitor Logs for Repeated FloodWait

If you see many consecutive FloodWait errors:
- Stop downloads for 30-60 minutes
- Consider reducing `RATE_LIMIT_RATE` further
- Check for competing API usage (other bots, manual scripts)

### 4. Use Batch Mode for Large Operations

Batch mode uses:
- 2 concurrent downloads (vs 5 in original)
- Rate limiting on status messages
- Jittered retries to avoid load spikes

## Testing

Run unit tests:

```bash
cd /workspaces/TG-DL-BOT
python -m pytest tests/test_flood_wait_handling.py -v
```

Tests cover:
- Rate limiter token-bucket logic
- FloodWait exception handling
- Retry logic and exponential backoff
- Per-destination rate limiting

## Implementation Details

### RateLimiter Algorithm

Token-bucket implementation with per-key tracking:

```python
class RateLimiter:
    def __init__(self, rate=1.0, per=1.0, burst=5):
        self.rate = rate          # tokens per second
        self.per = per            # refill period
        self.burst = burst        # max tokens
        self._allowance = {}      # per-key allowances
        self._last_check = {}     # per-key last check time

    async def acquire(self, key):
        # Refill tokens based on time elapsed
        # If sufficient tokens, decrement and return
        # Otherwise, sleep and retry
```

### FloodWait Extraction

Parses Telegram's error message to extract wait time:

```python
try:
    wait_time = int(re.search(r"\d+", str(fw)).group())
except:
    wait_time = 5  # fallback to 5 seconds
```

Caps to `max_wait_cap` (60s default) to prevent infinite waits.

## Backwards Compatibility

All changes are **backward compatible**:
- Existing code continues to work
- Safe wrappers are transparent
- Default rate limits are relaxed (1 msg/sec burst 5)
- No breaking changes to APIs

## Performance Impact

- **Minimal overhead**: Rate limiter adds <1ms per send
- **Jitter adds <1s to waits** on average
- **Retry logic prevents repeated crashes**
- **Overall improvement**: More reliable, fewer manual restarts

## Future Improvements

Potential enhancements:
- Metrics export (Prometheus format)
- Adaptive rate limiting based on error patterns
- Circuit breaker for transient outages
- Per-user rate limits (if multi-user support added)
