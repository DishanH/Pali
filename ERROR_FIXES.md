# Error Fixes & Solutions

## 504 Stream Cancelled Error

### Problem
```
504 Stream cancelled; RPC from prefill servable to decode servable failed
```

This error occurs when:
1. **Text is too large** - The Pali section has too many characters (>4000 typically)
2. **Request timeout** - The API takes too long to process the request
3. **Model overload** - Google's servers are under heavy load

### Solution Implemented

The script now automatically handles 504 errors with the following strategy:

#### 1. **Automatic Text Chunking**
- If a section is larger than `MAX_CHUNK_SIZE` (4000 chars by default), it's automatically split
- Splitting happens at:
  - Paragraph breaks (`\n\n`) first
  - Sentence boundaries (`.`, `!`, `?`, `।`, `॥`) if paragraphs are too large
  - Force-split if individual sentences are too large

#### 2. **Intelligent Retry on 504**
When a 504 error occurs:
1. **First attempt**: If text is >2000 chars, automatically split into smaller chunks (2000 chars each)
2. **Second attempt**: Retry with exponential backoff (30s, 60s, 90s...)
3. **Up to 5 retries** before giving up

#### 3. **Progress Tracking**
- Shows chunk progress: `📦 Split into 3 chunks`
- Shows individual chunk translation: `→ Chunk 1/3 (1847 chars)... ✓`

### Configuration Options

In `config.py`, you can adjust:

```python
# Maximum characters per translation chunk
MAX_CHUNK_SIZE = 4000  # Reduce to 2000-3000 if you get frequent 504 errors

# API request timeout (seconds)
API_TIMEOUT = 120  # Increase to 180 if sections are very complex

# Retry delay for server errors (seconds)
SERVER_OVERLOAD_RETRY_DELAY = 30  # Increase to 60 for better success rate

# Maximum retries
MAX_RETRIES = 5  # Increase to 8 for more persistence
```

### How to Handle 504 Errors

1. **Let it auto-retry** - The script will automatically split and retry
2. **If it fails after retries**:
   - Reduce `MAX_CHUNK_SIZE` to 2000 in `config.py`
   - Increase `API_TIMEOUT` to 180
   - Increase `SERVER_OVERLOAD_RETRY_DELAY` to 60
   - Run the script again - it will resume from where it failed

3. **Manual intervention** (if needed):
   - The script saves progress after each section
   - Use the resume feature: when prompted, enter the section number that failed
   - The script will skip already-translated sections

### Example Output

When handling a large section:
```
[10/50] Section 10
  ⚠️  Text is large (6847 chars), splitting into chunks...
  📦 Split into 3 chunks
    → Chunk 1/3 (2247 chars)... ✓
    → Chunk 2/3 (2198 chars)... ✓
    → Chunk 3/3 (2402 chars)... ✓
  ✓ English (6847 chars)
```

When getting a 504 error:
```
  ⚠️  Request timeout (504) - text may be too large (3421 chars)
  📦 Splitting into smaller chunks and retrying...
    → Chunk 1/2 (1685 chars)... ✓
    → Chunk 2/2 (1736 chars)... ✓
  ✓ Successfully recovered from 504 error
```

## Batch Folder Processing

### New Feature
You can now provide either:
- **Single file**: `Aṅguttaranikāyo/Aṭṭhakanipātapāḷi/chapters/an8.3-Gahapativaggo.json`
- **Entire folder**: `Aṅguttaranikāyo/Aṭṭhakanipātapāḷi/chapters`

The script will:
1. Find all JSON files in the folder (recursively)
2. Check which ones need translation (missing English or Sinhala)
3. Show you a summary
4. Process only the files that need work
5. Skip already-translated sections within each file

### Example Output
```
📁 Found 10 JSON file(s)
  ✓  an8.1-Mettāvaggo.json - fully translated
  ⚠️  an8.2-Mahāvaggo.json - 3 missing translation(s)
  ⚠️  an8.3-Gahapativaggo.json - 5 missing translation(s)
  ✓  an8.4-Dānavaggo.json - fully translated

📝 2 file(s) need translation

Process 2 file(s)? (Y/n):
```

## Other Error Types

### 503 Server Overload
- Automatic retry with increasing delays: 30s, 60s, 90s...
- No text splitting (not a size issue)

### 429 Rate Limit
- Automatic exponential backoff
- Respects configured RPM limits

### 500 Empty Response / Blocked Response
- Automatic retry with backoff
- Checks `finish_reason` for safety filters

### Quota Exceeded
- Stops processing immediately
- Shows resume section number
- Saves all progress up to that point

## Tips for Success

1. **Use appropriate RPM limit**: Set correctly for your API tier (10 for free, 15+ for paid)
2. **Adjust chunk size**: Reduce `MAX_CHUNK_SIZE` if you get frequent timeouts
3. **Enable auto-resume**: Let the script handle transient errors automatically
4. **Check progress files**: `.partial` files are created during processing for safety
5. **Monitor logs**: Check `translator.log` for detailed error information

