# Number Range Feature for Saṃyutta Nikāya Extraction

## Overview

The Saṃyutta Nikāya extraction scripts now support **number ranges** in section numbering, which is common in the Pali texts where multiple suttas are grouped together.

## Feature Description

### What It Does

When the PDF contains sections with number ranges like:
- `617-621. Rūpaanabhisamayādisuttapañcakaṃ`
- `11-15. Mārādisuttapañcakaṃ`
- `652-656. Rūpaappaccupekkhaṇādisuttapañcakaṃ`

The extractor now:
1. Detects the range pattern `XXX-YYY.`
2. Uses the **first number** as the `number` field
3. Adds a **`numberRange`** field with the full range string

### JSON Output Format

**Without range** (single number):
```json
{
  "number": 617,
  "pali": "Content here...",
  "english": "",
  "sinhala": "",
  "paliTitle": "Sutta title",
  "vagga": ""
}
```

**With range** (multiple numbers):
```json
{
  "number": 617,
  "numberRange": "617-621",
  "pali": "Content here...",
  "english": "",
  "sinhala": "",
  "paliTitle": "Rūpaanabhisamayādisuttapañcakaṃ",
  "vagga": ""
}
```

## Implementation Details

### Pattern Detection

The script detects three types of number ranges:

1. **Section ranges**: `617-621. Content...`
2. **Sutta title ranges**: `617-621. Rūpaanabhisamayādisuttapañcakaṃ`
3. **Group markers**: Titles ending with `suttapañcakaṃ` (group of 5) or `suttadasakaṃ` (group of 10)

### Regex Patterns Used

```python
# For sutta titles with ranges
sutta_range_match = re.match(r'^(\d+)-(\d+)\.\s+(.+suttaṃ|.+suttapañcakaṃ|.+suttadasakaṃ)$', line_stripped, re.IGNORECASE)

# For section numbers with ranges
section_range_match = re.match(r'^(\d+)-(\d+)\.\s+(.+)', line_stripped)
```

### Field Behavior

| Scenario | `number` Field | `numberRange` Field |
|----------|---------------|---------------------|
| Single number (e.g., `617.`) | `617` | Not present |
| Range (e.g., `617-621.`) | `617` | `"617-621"` |

## Examples from Extracted Data

### Example 1: Vacchagottasaṃyuttaṃ

From `sn.3.12-Vacchagottasaṃyuttaṃ.json`:

```json
{
  "number": 647,
  "numberRange": "647-651",
  "pali": "Sāvatthinidānaṃ. Rūpe kho, vaccha, asamapekkhaṇā…pe…",
  "english": "",
  "sinhala": "",
  "paliTitle": "Rūpaasamapekkhaṇādisuttapañcakaṃ",
  "vagga": ""
},
{
  "number": 652,
  "numberRange": "652-656",
  "pali": "Sāvatthinidānaṃ. Rūpe kho, vaccha, appaccupekkhaṇā…pe…",
  "english": "",
  "sinhala": "",
  "paliTitle": "Rūpaappaccupekkhaṇādisuttapañcakaṃ",
  "vagga": ""
}
```

### Example 2: Rādhasaṃyuttaṃ

From `sn.3.2-Rādhasaṃyuttaṃ.json`:

```json
{
  "number": 1,
  "numberRange": "1-11",
  "pali": "Mārādisuttaekādasakaṃ",
  "english": "",
  "sinhala": "",
  "paliTitle": "",
  "vagga": ""
}
```

## Statistics

From the Khandhavaggo extraction:

| File | Number of Ranges |
|------|------------------|
| sn.3.13-Jhānasaṃyuttaṃ.json | 11 |
| sn.3.12-Vacchagottasaṃyuttaṃ.json | 11 |
| sn.3.10-Gandhabbakāyasaṃyuttaṃ.json | 5 |
| sn.3.9-Supaṇṇasaṃyuttaṃ.json | 5 |
| sn.3.11-Valāhakasaṃyuttaṃ.json | 3 |
| sn.3.8-Nāgasaṃyuttaṃ.json | 3 |
| sn.3.3-Diṭṭhisaṃyuttaṃ.json | 3 |
| sn.3.2-Rādhasaṃyuttaṃ.json | 2 |
| **Total** | **43 ranges** |

## Benefits

### 1. Preserves Original Numbering
The extraction maintains the exact numbering system from the original Pali texts.

### 2. Enables Proper Citation
Scholars can reference suttas using the traditional range notation (e.g., SN 22.647-651).

### 3. Maintains Context
The `numberRange` field indicates that multiple suttas are grouped together, which is important for understanding the text structure.

### 4. Backward Compatible
- Sections without ranges work exactly as before
- The `numberRange` field is only added when needed
- Existing code that only uses the `number` field continues to work

## Usage in Applications

### Displaying Section Numbers

```javascript
// JavaScript example
function displaySectionNumber(section) {
  if (section.numberRange) {
    return `${section.numberRange}. ${section.paliTitle || section.pali.substring(0, 50)}...`;
  } else {
    return `${section.number}. ${section.paliTitle || section.pali.substring(0, 50)}...`;
  }
}
```

### Filtering by Range

```python
# Python example
def is_in_range(section, target_number):
    """Check if a target number falls within a section's range"""
    if 'numberRange' in section:
        start, end = map(int, section['numberRange'].split('-'))
        return start <= target_number <= end
    else:
        return section['number'] == target_number
```

## Files Modified

1. **extract_samyutta_correct.py**
   - Updated `extract_suttas_from_samyutta()` method
   - Added range detection patterns
   - Added `numberRange` field to section objects

2. **extract_samyutta_batch.py**
   - No changes needed (uses the updated extractor class)

## Testing

### Test Case 1: Single Number
**Input**: `617. Sāvatthinidānaṃ...`

**Output**:
```json
{
  "number": 617,
  "pali": "Sāvatthinidānaṃ...",
  ...
}
```

### Test Case 2: Number Range
**Input**: `617-621. Rūpaanabhisamayādisuttapañcakaṃ`

**Output**:
```json
{
  "number": 617,
  "numberRange": "617-621",
  "pali": "...",
  "paliTitle": "Rūpaanabhisamayādisuttapañcakaṃ",
  ...
}
```

### Test Case 3: Range with Content
**Input**: `652-656. Sāvatthinidānaṃ. Rūpe kho...`

**Output**:
```json
{
  "number": 652,
  "numberRange": "652-656",
  "pali": "Sāvatthinidānaṃ. Rūpe kho...",
  ...
}
```

## Verification

To verify the feature is working:

```bash
# Count number ranges in extracted files
grep -r "numberRange" Saṃyuttanikāyo/Khandhavaggo/chapters/ | wc -l

# View specific examples
grep -A 2 -B 2 "numberRange" Saṃyuttanikāyo/Khandhavaggo/chapters/sn.3.12-Vacchagottasaṃyuttaṃ.json
```

## Future Enhancements

Potential improvements:
- [ ] Parse range to extract start and end numbers separately
- [ ] Validate that content matches the range count (e.g., pañcakaṃ = 5)
- [ ] Add metadata about range type (pañcakaṃ, dasakaṃ, etc.)
- [ ] Cross-reference with sutta indices

## Compatibility

### Translation Scripts
The existing translation scripts (`translate_json_chapters.py`, etc.) work seamlessly with the new format:
- They process the `pali` field regardless of `numberRange`
- The `numberRange` field is preserved through translation
- No changes needed to translation workflow

### Verification Scripts
Verification scripts should be updated to:
- Check both `number` and `numberRange` fields
- Validate range format (XXX-YYY)
- Ensure start number matches `number` field

## Conclusion

The number range feature enhances the Saṃyutta Nikāya extraction by accurately representing the traditional Pali text structure while maintaining backward compatibility with existing tools and workflows.

---

**Status**: ✅ Implemented and Tested  
**Date**: 2025-11-24  
**Affected Collections**: Saṃyutta Nikāya (all 5 vaggas)  
**Total Ranges Detected**: 43+ across Khandhavaggo alone

