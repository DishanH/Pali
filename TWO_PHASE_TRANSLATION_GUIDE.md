# Two-Phase Translation with Verification

## Overview

The translator now supports a **two-phase translation process** that ensures both **accuracy and readability**:

1. **Phase 1: Primary Translation** - Focuses on doctrinal accuracy
2. **Phase 2: Verification & Improvement** - Enhances readability while preserving accuracy

## How It Works

### Phase 1: Primary Translation
```
Pali Text → Primary AI Model → Initial Translation
```
- Translates Pali to English/Sinhala
- Focuses on **accuracy** and **completeness**
- Preserves all Buddhist terminology
- Maintains doctrinal correctness

### Phase 2: Verification & Improvement
```
Pali Text + Initial Translation → Verification AI Model → Improved Translation
```
- Checks 1-to-1 mapping with Pali (no omissions or additions)
- Improves sentence flow and readability
- Makes language more natural and modern
- Fixes awkward phrasing
- Validates Buddhist terminology usage

## Configuration

### In `config.py`:

```python
# Primary translation model
MODEL_NAME = 'gemini-2.5-flash'

# Verification model (can be same or different)
VERIFY_MODEL_NAME = 'gemini-2.5-flash'  # Or use 'gemini-1.5-pro' for better quality

# Enable/disable verification
ENABLE_VERIFICATION = True  # Set to False to skip verification

# Verification delay (separate rate limiting)
VERIFY_DELAY = 2  # seconds between verification calls
```

### Model Recommendations:

| Primary Model | Verification Model | Use Case |
|--------------|-------------------|----------|
| `gemini-2.5-flash` | `gemini-2.5-flash` | **Fast & Cost-effective** - Good for initial translations |
| `gemini-2.5-flash` | `gemini-1.5-pro` | **Balanced** - Fast primary, thorough verification |
| `gemini-1.5-pro` | `gemini-1.5-pro` | **Highest Quality** - Best accuracy, slower & more expensive |

## Benefits

### 1. **Accuracy Assurance**
- Two models cross-check each other
- Catches hallucinations or omissions
- Verifies 1-to-1 content mapping

### 2. **Improved Readability**
- More natural, modern language
- Better sentence flow
- Accessible to contemporary readers

### 3. **Quality Control**
- Validates Buddhist terminology
- Ensures doctrinal accuracy
- Maintains traditional terms (dhamma, karma, nibbana)

### 4. **Consistency**
- Consistent translation style
- Proper use of Pali terms in parentheses
- Uniform formatting

## Example Output

### Before Verification (Primary Translation):
```
Thus have I heard. At one time the Blessed One was dwelling at Sāvatthī, 
in the Eastern Monastery, in Migāra's mother's palace. Now at that time, 
Vāseṭṭha and Bhāradvāja were living among the monks, desiring monkhood.
```

### After Verification (Improved):
```
Thus have I heard: Once, the Blessed One was staying at Sāvatthī, in the 
Eastern Monastery at Migāra's mother's palace. At that time, Vāseṭṭha and 
Bhāradvāja were living among the monks (bhikkhus), aspiring to become 
fully ordained monastics.
```

**Changes made**:
- ✓ "Thus have I heard. At" → "Thus have I heard:"
- ✓ Added "(bhikkhus)" for clarity
- ✓ "desiring monkhood" → "aspiring to become fully ordained monastics" (more precise)
- ✓ Improved flow and readability

## Performance Impact

### Time Increase:
- With verification: **~2x translation time** (each section gets 4 API calls instead of 2)
- Example: 20 sections × 2 languages × 2 phases = **80 API calls** (vs 40 without verification)

### Cost Increase:
- **~2x API costs** (double the API calls)
- But significantly better quality output

### When to Use:
- ✅ **Final production translations** - Use verification for published works
- ✅ **Important chapters** - Use for critical or complex texts
- ❌ **Draft/preview** - Disable for quick previews or testing
- ❌ **Budget constraints** - Disable if API costs are a concern

## Disabling Verification

### Option 1: In `config.py`
```python
ENABLE_VERIFICATION = False
```

### Option 2: Command Line (future enhancement)
```bash
python translator.py --no-verify
```

## Monitoring

### Log Output:
```
2025-11-05 14:30:00 - INFO - Translating 1234 characters to English
2025-11-05 14:30:10 - INFO - Translation completed: 1850 characters
2025-11-05 14:30:12 - INFO - Verifying English translation (1850 chars)
2025-11-05 14:30:20 - INFO - Verification adjusted length: 1850 → 1920 chars
2025-11-05 14:30:22 - INFO - Translating 1234 characters to Sinhala
2025-11-05 14:30:35 - INFO - Translation completed: 1650 characters
2025-11-05 14:30:37 - INFO - Verifying Sinhala translation (1650 chars)
2025-11-05 14:30:50 - INFO - Verification completed (no length change)
```

### Console Output:
```
[1/23] Translating section 49...
  → English translation (1234 chars)... ✓ (1850 chars)
  → Sinhala translation (1234 chars)... ✓ (1650 chars)
  → Verifying English... ✓ (1920 chars)
  → Verifying Sinhala... ✓ (1650 chars)
```

## Verification Prompt

The verification model receives:
1. **Original Pali text** - For accuracy checking
2. **Initial translation** - To verify and improve
3. **Specific instructions** - What to check and improve

### What It Checks:
- ✓ All Pali content is translated (no omissions)
- ✓ No extra content added (no hallucinations)
- ✓ Buddhist terms are correct
- ✓ Grammar and flow are natural
- ✓ Sentences are complete
- ✓ Modern, accessible language

### What It Improves:
- Awkward phrasing → Natural flow
- Overly literal → Idiomatic but accurate
- Complex sentences → Clear and accessible
- Missing context → Adds Pali terms in parentheses
- Inconsistent style → Uniform format

## Fallback Behavior

If verification fails (API error, timeout, etc.):
```
2025-11-05 14:30:50 - WARNING - Verification failed: API timeout. Using original translation.
```

The system automatically falls back to the primary translation, ensuring the translation process continues even if verification fails.

## Best Practices

### 1. **Start with Verification Enabled**
- Get the best quality output
- Identify any systematic issues

### 2. **Monitor the Logs**
- Check if verification is making significant changes
- If no changes, you might disable it for speed

### 3. **Use Different Models**
- Primary: Fast model (gemini-2.5-flash)
- Verification: Powerful model (gemini-1.5-pro)
- Gets best of both worlds

### 4. **Adjust Delays**
- Increase `VERIFY_DELAY` if hitting rate limits
- Balance between speed and API limits

### 5. **Spot Check Results**
- Manually review some verified translations
- Ensure verification is helping, not hurting

## Troubleshooting

### Issue: Verification making things worse
**Solution**: 
- Try a different verification model
- Adjust the verification prompt in `config.py`
- Disable verification temporarily

### Issue: Too slow
**Solution**:
- Disable verification for draft work
- Use same fast model for both phases
- Increase parallel processing (future feature)

### Issue: Rate limit errors
**Solution**:
- Increase `VERIFY_DELAY`
- Use different API keys for primary and verification (future feature)
- Process fewer sections at once

## Future Enhancements

Planned features:
- [ ] Selective verification (only for sections > X chars)
- [ ] Batch verification (verify multiple sections at once)
- [ ] Comparative metrics (before/after verification stats)
- [ ] Human-in-the-loop approval
- [ ] A/B testing mode (compare with/without verification)

---

## Summary

The two-phase translation system provides:
- ✅ **Better accuracy** through cross-checking
- ✅ **Improved readability** through refinement
- ✅ **Quality assurance** through validation
- ✅ **Flexibility** through enable/disable option

**Recommendation**: Keep verification **enabled** for production translations, **disabled** for testing/drafts.

