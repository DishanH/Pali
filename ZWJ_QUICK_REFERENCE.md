# ZWJ Fix - Quick Reference Guide

## What is ZWJ?

**Zero-Width Joiner (U+200D)** is an invisible Unicode character essential for proper Sinhala text rendering, especially for conjunct consonants.

## Problem

Translation files contained literal text placeholders like `[ZWJ]`, `#zwj;`, or `<ZWJ>` instead of the actual Unicode character.

## Quick Commands

### Check for Issues
```bash
python check_all_zwj.py
```

### Fix All Issues
```bash
python fix_zwj_literals.py
```

### Verify Specific Files
```bash
python verify_zwj_fix.py
```

## Supported Formats

The fix script handles all these variations:
- `<ZWJ>` → U+200D
- `[ZWJ]` → U+200D  
- `#zwj;` → U+200D
- `#ZWJ#` → U+200D
- `_ZWJ_` → U+200D
- `&#8205;` → U+200D
- `&zwj;` → U+200D

## Current Status

✅ **All 45 JSON files checked**  
✅ **98 issues fixed across 7 files**  
✅ **Zero remaining issues**

## Files Fixed

1. `Pāthikavaggapāḷi/chapters/dn2-Udumbarikasuttaṃ.json` (6 fixes)
2. `Sīlakkhandhavaggapāḷi/chapters/dn1-Brahmajālasuttaṃ.json` (5 fixes)
3. `Sīlakkhandhavaggapāḷi/chapters/dn13-Tevijjasuttaṃ.json` (2 fixes)
4. `Sīlakkhandhavaggapāḷi/chapters/dn2-Sāmaññaphalasuttaṃ.json` (40 fixes)
5. `Sīlakkhandhavaggapāḷi/chapters/dn9-Poṭṭhapādasuttaṃ.json` (24 fixes)
6. `Sīlakkhandhavaggapāḷi/chapters/dn10-Subhasuttaṃ.json` (8 fixes)
7. `Sīlakkhandhavaggapāḷi/chapters/dn12-Lohiccasuttaṃ.json` (13 fixes)

## Example

**Before:** `ශ්‍ර[ZWJ]මණ`, `බ්‍ර#zwj;ාහ්මණ`, or `ශ්_ZWJ_රමණ`  
**After:** `ශ්‍රමණ`, `බ්‍රාහ්මණ`, and `ශ්‍රමණ` (with proper U+200D)

The ZWJ character is invisible but ensures correct rendering of Sinhala conjuncts.
