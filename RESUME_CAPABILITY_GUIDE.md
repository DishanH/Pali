# Resume Capability & Sinhala Quality Enhancement Guide

## 🎯 New Features Added

### 1. **Resume from Where It Stopped** ✅
The script now automatically saves progress and can resume from the exact section it stopped at if interrupted.

### 2. **Standard Modern Colloquial Sinhala** ✅
Enhanced prompts ensure translations are in natural, readable modern Sinhala with proper grammar, syntax, and terminology.

### 3. **100% Pali Accuracy Enforcement** ✅
Strict requirement that translations match Pali text exactly - no omissions, no additions.

---

## 🔄 Resume Capability

### How It Works

1. **Automatic Progress Tracking**
   - After each section is processed, progress is saved to `<filename>.json.progress`
   - Includes: last completed section number, statistics, timestamp

2. **Automatic Resume**
   - If script is interrupted (Ctrl+C, error, quota exceeded, power loss)
   - Next run automatically detects progress file
   - Resumes from next section after last completed

3. **Progress File Format**
   ```json
   {
     "last_section": 42,
     "stats": {
       "sections_checked": 42,
       "sinhala_fixed": 5,
       ...
     },
     "timestamp": "2025-11-17 15:30:45"
   }
   ```

4. **Automatic Cleanup**
   - Progress file automatically deleted when chapter completes successfully
   - No manual cleanup needed

---

## 📋 Usage Examples

### Scenario 1: Normal Run (No Interruption)
```bash
$ python verify_and_clean_translations.py
```

**Console Output:**
```
============================================================
Translation Verification & Cleaning Tool - OPTIMIZED
============================================================
Token Optimization: English verification DISABLED
Smart skipping: ENABLED
============================================================

Processing: dn01-Brahmajālasuttaṃ.json
Chapter ID: dn01
Total sections: 63

[1/63] Section 1
  ✓ English OK (verification disabled)
  ✓ Sinhala OK (no API call needed)

[2/63] Section 2
  ✓ English OK (verification disabled)
  🔧 Fixing Sinhala translation (1 API call)...
  ✓ Sinhala fixed: Improved modern colloquial tone

...

[63/63] Section 63
  ✓ English OK (verification disabled)
  ✓ Sinhala OK (no API call needed)

✅ Completed:
   Sections checked: 63
   Sinhala issues found: 8, fixed: 8
```

**Result:** Progress file deleted, chapter complete!

---

### Scenario 2: Interrupted Run (Quota Exceeded)
```bash
$ python verify_and_clean_translations.py
```

**Console Output:**
```
Processing: dn01-Brahmajālasuttaṃ.json
Chapter ID: dn01
Total sections: 63

[1/63] Section 1
  ✓ Sinhala OK (no API call needed)

...

[42/63] Section 42
  🔧 Fixing Sinhala translation (1 API call)...
  ❌ Error in section 42: 429 Rate Limit Exceeded
  Progress saved. You can resume from this point.
```

**Progress File Created:**
- `dn01-Brahmajālasuttaṃ.json.progress`
- Contains: `"last_section": 41` (last *completed* section)

---

### Scenario 3: Resume After Interruption
```bash
$ python verify_and_clean_translations.py
# (Run again after quota resets)
```

**Console Output:**
```
Processing: dn01-Brahmajālasuttaṃ.json
Chapter ID: dn01
Total sections: 63
🔄 RESUMING from section 42 (previous run interrupted)
Resuming from section: 42
Remaining sections: 21

[42/63] Section 42  ← Picks up exactly where it left off!
  🔧 Fixing Sinhala translation (1 API call)...
  ✓ Sinhala fixed

...

[63/63] Section 63
  ✓ Sinhala OK

✅ Completed:
   Sections checked: 63
```

**Result:** Progress file deleted, chapter fully complete!

---

## 🛡️ Exception Handling

### What Happens When...

| Exception Type | Behavior | Resume Point |
|---------------|----------|--------------|
| **Rate Limit (429)** | Save progress, show error | Last completed section |
| **Quota Exceeded** | Save progress, exit gracefully | Last completed section |
| **Network Error** | Save progress, retry with backoff | Last completed section |
| **API Timeout** | Save progress, show timeout | Last completed section |
| **Server Overload (503)** | Save progress, wait & retry | Last completed section |
| **Ctrl+C (User)** | Save progress, exit | Last completed section |
| **Power Loss** | Progress already saved | Last completed section |
| **Any Other Error** | Save progress, log error | Last completed section |

### Error Recovery Flow

```
Section 40: Processing... ✓ (saved)
Section 41: Processing... ✓ (saved)
Section 42: Processing... ❌ ERROR!
          ↓
    Progress saved (last_section: 41)
          ↓
    Script exits with error message
          ↓
    User fixes issue / waits for quota reset
          ↓
    Run script again
          ↓
    Auto-resumes from section 42 ✓
```

---

## 📊 Standard Modern Colloquial Sinhala

### What It Means

The script now ensures:

1. **Modern Language**
   - Contemporary Sinhala words and phrases
   - Not archaic or overly classical
   - Natural for modern readers

2. **Colloquial Tone**
   - Conversational but respectful
   - Not overly formal or stilted
   - Appropriate for Dhamma texts

3. **Proper Grammar & Syntax**
   - Correct Sinhala sentence structure
   - Natural word order
   - Proper verb conjugations

4. **Buddhist Terminology**
   - Traditional Sinhala Buddhist terms
   - Respectful language for Triple Gem
   - Appropriate honorifics

5. **Unicode Compliance**
   - Only Sinhala Unicode (U+0D80-U+0DFF)
   - Proper Zero-Width Joiner (ZWJ) usage
   - Correct conjunct formation

### Enhanced Verification Prompt

```
CRITICAL REQUIREMENTS:
1. 100% accurate to Pali meaning - NO omissions, NO additions
2. Standard Modern Colloquial Sinhala (not archaic/overly formal)
3. Natural Sinhala grammar, syntax, and word order
4. Proper Buddhist terminology in Sinhala
5. ONLY Sinhala Unicode (U+0D80-U+0DFF) - NO Tamil/Hindi/other scripts
6. PRESERVE Zero-Width Joiner (U+200D) for proper conjuncts: භාග්‍යවතුන්
7. Remove metadata like "Here is translation", numbered notes
8. Natural tone suitable for modern Sinhala readers
```

---

## 🎯 100% Pali Accuracy

### Strict Matching

The script enforces:

1. **No Omissions**
   - Every Pali concept must be translated
   - No skipping words or phrases
   - Complete sentences only

2. **No Additions**
   - No extra explanations
   - No commentary
   - No meta-information
   - Pure translation only

3. **Meaning Preservation**
   - Exact doctrinal accuracy
   - Correct Buddhist concepts
   - Proper technical terms

### Example

**BAD Translation (has additions):**
```sinhala
1. භාග්‍යවතුන් වහන්සේ (මේ යන්නෙ බුදුරජාණන් වහන්සේයි) මෙසේ වදාළ සේක.
```
*Problem: Contains "(මේ යන්නෙ බුදුරජාණන් වහන්සේයි)" which is explanatory addition*

**GOOD Translation (accurate, no additions):**
```sinhala
භාග්‍යවතුන් වහන්සේ මෙසේ වදාළ සේක.
```
*Correct: Pure translation, no extra explanations*

---

## 🔍 Progress Tracking Files

### Files Created During Processing

| File | Purpose | When Created | When Deleted |
|------|---------|--------------|--------------|
| `<chapter>.json` | Main chapter file | Always exists | Never (output) |
| `<chapter>.json.progress` | Resume tracking | After each section | On completion |
| `<chapter>.json.partial` | Temp save file | During saves | Immediately replaced |

### Manual Progress Management

#### Check Progress Status
```bash
# See if progress file exists
ls *.progress

# View progress details
cat dn01-Brahmajālasuttaṃ.json.progress
```

#### Force Fresh Start (Delete Progress)
```bash
# Delete progress file to start from beginning
rm dn01-Brahmajālasuttaṃ.json.progress

# Or delete all progress files
rm *.progress
```

#### Resume from Specific Section (Advanced)
```json
// Edit .progress file manually
{
  "last_section": 20,  // Change this to start from section 21
  "stats": {...},
  "timestamp": "2025-11-17 15:30:45"
}
```

---

## 💡 Best Practices

### 1. **Let It Resume Automatically**
   - Don't delete progress files unless you want to start over
   - Script handles resume automatically
   - No manual intervention needed

### 2. **Monitor Progress**
   - Check console output for section numbers
   - Note last completed section before interruption
   - Progress file timestamp shows last run time

### 3. **Handle Quota Limits**
   ```bash
   # If you hit quota limit:
   # 1. Script saves progress automatically
   # 2. Wait for quota to reset (check Google Cloud Console)
   # 3. Run script again (auto-resumes)
   ```

### 4. **Batch Processing**
   - Process one directory at a time
   - Each file has its own progress tracking
   - Can interrupt and resume entire directory

### 5. **Check Logs**
   ```bash
   # See what happened during processing
   tail -f translator.log
   
   # Check for errors
   grep "ERROR" translator.log
   
   # See resume points
   grep "Resuming" translator.log
   ```

---

## 🐛 Troubleshooting

### Progress File Won't Delete
```bash
# Manually delete if stuck
rm *.progress

# Check file permissions
ls -la *.progress
```

### Resume Not Working
```bash
# Verify progress file exists
ls *.progress

# Check progress file is valid JSON
cat file.json.progress | python -m json.tool

# Delete and start fresh if corrupted
rm file.json.progress
```

### Keeps Reprocessing Same Section
- Progress file might be corrupted
- Delete it and start fresh
- Check log file for actual errors

### Want to Process Multiple Files
```bash
# Script handles this automatically in process_directory()
python verify_and_clean_translations.py
# Enter directory path: Mahāvaggapāḷi/chapters

# Each file gets its own progress tracking
# Can interrupt and resume entire batch
```

---

## 📈 Performance with Resume

### Time Savings

| Scenario | Without Resume | With Resume | Benefit |
|----------|---------------|-------------|---------|
| **Full Run** | 20 min | 20 min | Same |
| **Interrupted at 50%** | 20 min (restart) | 10 min (resume) | **50% faster** |
| **Interrupted at 90%** | 20 min (restart) | 2 min (resume) | **90% faster** |
| **Quota Limit Hit** | Wait & restart | Wait & continue | **Seamless** |

### Cost Savings

With resume capability:
- No wasted API calls on already-processed sections
- Only pay for new sections
- Retry logic handles temporary failures
- Progress preserved across runs

**Example:**
- 100 sections, interrupted at section 80
- Without resume: Reprocess all 100 (pay for 100)
- With resume: Process remaining 20 (pay for 20)
- **Savings: 80% of API costs** for resumed run

---

## ✅ Summary

### Key Features

✅ **Automatic Progress Saving** - After every section  
✅ **Automatic Resume** - Picks up where it left off  
✅ **Exception Handling** - Graceful error recovery  
✅ **Progress Cleanup** - Auto-deletes on completion  
✅ **Standard Modern Sinhala** - Natural, readable translations  
✅ **100% Pali Accuracy** - No omissions, no additions  
✅ **Proper Unicode & ZWJ** - Correct Sinhala rendering  

### Zero Configuration Needed

Just run the script - resume capability works automatically!

```bash
python verify_and_clean_translations.py
```

That's it! The script handles everything else. 🎉

---

## 🎓 Advanced: Understanding the Code

### Progress Tracking Functions

```python
# Save progress after each section
self.save_progress(json_path, section_number, stats)

# Load progress on startup
progress = self.load_progress(json_path)
last_section = progress.get('last_section', 0)

# Clear progress on completion
self.clear_progress(json_path)
```

### Resume Logic

```python
# Skip already-processed sections
for i, section in enumerate(sections):
    if i < last_completed_section:
        continue  # Skip this section
    
    # Process section...
    
    # Save progress
    self.save_progress(json_path, i + 1, stats)
```

### Exception Handling

```python
try:
    # Process section
    ...
except Exception as e:
    # Save progress before exiting
    self.save_progress(json_path, i, stats)
    print("Progress saved. You can resume from this point.")
    raise  # Re-raise error
```

---

**Your verification script is now production-ready with enterprise-grade resume capability!** 🚀

