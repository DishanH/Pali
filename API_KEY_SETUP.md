# API Key Auto-Rotation Setup

## Quick Setup

1. **Install dependency:**
   ```bash
   pip install python-dotenv
   ```

2. **Create `.env` file** in your project root:
   ```env
   GOOGLE_API_KEY_1=your_first_key_here
   GOOGLE_API_KEY_2=your_second_key_here
   GOOGLE_API_KEY_3=your_third_key_here
   
   MAX_REQUESTS_PER_KEY=220
   QUOTA_WARNING_THRESHOLD=200
   ```

3. **Run your script:**
   ```bash
   python translate_titles_and_footer.py
   ```
   When asked "Use automatic API key rotation?", press Enter (yes).

## How It Works

- Starts with Key #1
- Warns you at 200 requests
- Auto-switches to Key #2 at 220 requests
- Continues seamlessly through all your keys

## Configuration

| Setting | Default | What it does |
|---------|---------|--------------|
| `MAX_REQUESTS_PER_KEY` | 220 | Switch keys at this count (out of 250 quota) |
| `QUOTA_WARNING_THRESHOLD` | 200 | Show warning at this count |

## Troubleshooting

**"No API keys found"**: Check your `.env` file - keys must be named `GOOGLE_API_KEY_1`, `GOOGLE_API_KEY_2`, etc.

**Reset state**: Delete `api_key_state.json` file

That's it! The system handles everything else automatically.



