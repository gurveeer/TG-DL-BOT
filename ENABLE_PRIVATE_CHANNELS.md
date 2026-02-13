# Enable Private Channel Access

Your bot currently cannot access private channels because the SESSION string is empty. Follow these steps to enable private channel access:

## Option 1: Generate Session Locally (Recommended)

Run the session generator script on your local machine:

```bash
python core/helpers/session.py
```

This will:
1. Prompt you for your phone number (in international format, e.g., +917691853512)
2. Send a login code to your Telegram app
3. Ask you to enter the code
4. Generate a session string
5. Automatically update your .env file

## Option 2: Manual Session Generation

If you prefer to generate the session manually:

```python
from pyrogram import Client

api_id = 20382730
api_hash = "76d44e9de00f1f6ca4cefdfde84d2508"

app = Client("my_account", api_id=api_id, api_hash=api_hash)

async def main():
    async with app:
        print(await app.export_session_string())

app.run(main())
```

## After Generating the Session

1. Copy the generated session string
2. Update your local .env file:
   ```
   SESSION=<your_session_string_here>
   ```

3. Copy the updated .env to the GCP VM:
   ```bash
   gcloud compute scp --zone=us-central1-b .env medium-vm:telegram-bot/
   ```

4. Restart the bot container:
   ```bash
   gcloud compute ssh medium-vm --zone=us-central1-b --command="docker restart telegram-bot"
   ```

## Verify Private Channel Access

After restarting, check the logs to confirm the userbot is configured:

```bash
gcloud compute ssh medium-vm --zone=us-central1-b --command="docker logs telegram-bot | grep -i userbot"
```

You should see:
```
[OK] Userbot configured - Private channel access enabled
```

## Security Note

⚠️ The session string gives full access to your Telegram account. Keep it secure:
- Never share it publicly
- Store it securely in environment variables
- Regenerate it if compromised
- Use a dedicated account for the bot if possible

## Troubleshooting

If you get "Session expired" errors:
1. Delete old session files in the sessions/ directory
2. Generate a new session string
3. Update the .env file
4. Restart the bot

If you get "FloodWait" errors:
- Wait for the specified time before trying again
- Telegram has rate limits on authentication attempts
