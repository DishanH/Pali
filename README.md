# Pali Buddhist Text Translator

An AI-powered translator for Pali Buddhist texts that uses Google's Generative AI to translate ancient Pali texts into English and Sinhala, with intelligent handling of rate limits and character limits.

## Features

✨ **Smart Translation**
- Translates Pali Buddhist texts to English and Sinhala
- Preserves Buddhist terminology and philosophical accuracy
- Uses modern, accessible language

🎯 **Intelligent Section Management**
- Automatically splits text into logical sections
- Combines small sections (< 100 chars) to optimize API calls
- Splits large sections (> 4000 chars) to handle character limits
- Preserves document structure and paragraph breaks

⚡ **Rate Limit Handling**
- Built-in rate limiting (2-second delay between API calls)
- Configurable delay settings
- Robust error handling

📄 **Structured JSON Output**
- Creates organized chapter JSON files
- Maintains consistent structure across translations
- Easy to integrate with web applications

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Get Google Generative AI API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Save it securely

## Configuration

You can configure the translator by editing these variables in `translator.py`:

```python
MAX_CHUNK_SIZE = 4000  # Characters per translation chunk
RATE_LIMIT_DELAY = 2   # Seconds between API calls
MIN_SECTION_SIZE = 100 # Minimum characters for a section
```

## Usage

### Basic Usage

Run the translator:
```bash
python translator.py
```

You'll be prompted to:
1. Enter your Google Generative AI API key (or set `GOOGLE_API_KEY` environment variable)
2. Choose which chapter(s) to translate

### Environment Variable (Recommended)

Set your API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your-api-key-here"
python translator.py
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
python translator.py
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY="your-api-key-here"
python translator.py
```

### Translating Specific Chapters

When prompted, you can:
- Enter a chapter number (e.g., `1` for the first chapter)
- Enter `all` to translate all chapters

## Output Structure

The translator creates JSON files in the following structure:

```json
{
  "id": "dn1",
  "title": {
    "pali": "Pāthikasuttaṃ",
    "english": "The Pāthika Discourse",
    "sinhala": "පාථික සූත්‍රය"
  },
  "sections": [
    {
      "number": 1,
      "pali": "Evaṃ me sutaṃ...",
      "english": "Thus have I heard...",
      "sinhala": "මා විසින් මෙසේ අසන ලදී..."
    }
  ]
}
```

## Translation Quality

The translator is optimized for:

1. **Doctrinal Accuracy**: Preserves exact Buddhist philosophical meanings
2. **Traditional Terminology**: Keeps key Buddhist terms (dhamma, karma, nibbana, bhikkhu)
3. **Modern Language**: Uses accessible, contemporary language
4. **Completeness**: Ensures all sentences are complete and properly translated
5. **Structure**: Maintains paragraph breaks and document organization

## Translation Process

1. **Text Parsing**: Splits the Pali text into logical sections
2. **Section Optimization**: 
   - Combines sections under 100 characters
   - Splits sections over 4000 characters
3. **Translation**: Translates each section to English and Sinhala
4. **Cleaning**: Removes page numbers, prefixes, and formatting artifacts
5. **JSON Generation**: Creates structured JSON files

## Rate Limits & Best Practices

- **Default Delay**: 2 seconds between API calls
- **Chunk Size**: 4000 characters per request
- **Error Handling**: Automatic retry logic for transient errors
- **Logging**: Detailed logs for monitoring progress

## File Structure

```
Pāthikavaggapāḷi/
├── book.json                              # Chapter metadata
├── Pāthikavaggapāḷi_pali_extracted.txt   # Source Pali text
├── sample.txt                             # Sample text
└── chapters/
    ├── dn1-Pāthikasuttaṃ.json            # Translated chapters
    ├── dn2-Udumbarikasuttaṃ.json
    └── ...
```

## Troubleshooting

### API Key Issues
```
ERROR: No API key provided
```
**Solution**: Set the `GOOGLE_API_KEY` environment variable or enter it when prompted.

### Rate Limit Errors
```
ERROR: Rate limit exceeded
```
**Solution**: Increase `RATE_LIMIT_DELAY` in the configuration.

### Character Encoding Issues
```
ERROR: Unicode decode error
```
**Solution**: Ensure all files are saved with UTF-8 encoding.

## Advanced Usage

### Custom Translation Prompt

You can modify the translation prompt in the `translate_text` method to adjust:
- Translation style
- Level of detail
- Terminology preferences
- Output format

### Batch Processing

For large-scale translations, consider:
1. Splitting work across multiple sessions
2. Implementing checkpoint/resume functionality
3. Using multiple API keys for parallel processing

## License

This project is for educational and religious purposes. Please respect Buddhist teachings and use translations responsibly.

## Contributing

Contributions are welcome! Please ensure:
- Code follows Python best practices
- Translations maintain doctrinal accuracy
- Rate limiting is respected
- Documentation is updated

## Acknowledgments

- Buddhist texts from the Pali Canon
- Google Generative AI for translation capabilities
- The Buddhist community for preserving these teachings

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs for detailed error messages
3. Ensure API key and internet connectivity
4. Verify file paths and permissions

---

**Note**: This translator uses AI and should be used as a study aid. For canonical references, consult traditional translations and scholars.

