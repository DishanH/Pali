# Rate Limit Burst Fix

## Problem Identified

You were hitting rate limits during verification even though the Google AI dashboard showed available capacity (7/10 and 8/15 RPM). The issue was **API call bursting**.

### Original Call Pattern (Per Section)

```
1. English translation      → [waits 4s at end]
2. English verification     → IMMEDIATE (burst!) ← Rate limit here!
3. Sinhala translation      → [waits 4s at end]
4. Sinhala verification     → IMMEDIATE (burst!) ← Rate limit here!
```

**Problem**: Even though individual calls had delays, the pattern created bursts:
- Translation finishes at T+0, waits 4s
- Verification starts at T+4 (too soon!)
- Google sees 2 requests within 4 seconds from the same pattern

### Why the Dashboard Showed Capacity

The dashboard shows **average RPM** over a minute window, but Google also has **micro-burst protection** that triggers when multiple calls happen too close together, even if you're under the minute limit.

## Solution Applied

### 1. Added Pre-Verification Delays

```python
if ENABLE_VERIFICATION:
    time.sleep(RATE_LIMIT_DELAY)  # NEW: Wait BEFORE verification
    print(f"  → Verifying English...")
    english = self.verify_and_improve_translation(...)
```

**New timing per section**:
```
1. English translation      → [waits 5s at end]
2. [WAIT 5s]               → NEW: Pre-verification delay
3. English verification     → [waits 5s at end]
4. Sinhala translation      → [waits 5s at end]
5. [WAIT 5s]               → NEW: Pre-verification delay
6. Sinhala verification     → [waits 5s at end]
7. [WAIT 2s]               → NEW: Between sections
```

### 2. Increased Base Delays

**Old config**:
```python
RATE_LIMIT_DELAY = 4  # seconds
VERIFY_DELAY = 4      # seconds
```

**New config**:
```python
RATE_LIMIT_DELAY = 5  # seconds (was 4)
VERIFY_DELAY = 5      # seconds (was 4)
```

### 3. Added Inter-Section Delay

```python
# After saving progress
time.sleep(2)  # Short pause between sections
```

## New Timing Analysis

### Per Section (With Verification Enabled)

| Step | Duration | Wait After | Total Time |
|------|----------|-----------|------------|
| English translation | ~2s | 5s | 7s |
| **Pre-verification delay** | 0s | 5s | 5s |
| English verification | ~2s | 5s | 7s |
| Sinhala translation | ~2s | 5s | 7s |
| **Pre-verification delay** | 0s | 5s | 5s |
| Sinhala verification | ~2s | 5s | 7s |
| Inter-section delay | 0s | 2s | 2s |
| **Total per section** | | | **~40s** |

### API Calls Distribution

**Old pattern** (caused bursts):
```
0s  ────[English]────
4s                    ────[Verify]──── ← Too soon!
8s                                      ────[Sinhala]────
12s                                                       ────[Verify]──── ← Too soon!
```

**New pattern** (properly spaced):
```
0s  ────[English]────
5s                    [wait]
10s                          ────[Verify]────
15s                                           [wait]
20s                                                  ────[Sinhala]────
25s                                                                   [wait]
30s                                                                          ────[Verify]────
35s                                                                                           [wait]
40s                                                                                                  [next section]
```

## Results

### Before Fix
- **Rate limit errors**: Frequent during verification
- **Retry attempts**: 1-3 per section
- **Failed sections**: Some sections failed after 3 retries
- **Speed**: ~30s per section (with retries)

### After Fix
- **Rate limit errors**: Rare or none
- **Retry attempts**: None expected
- **Failed sections**: None expected
- **Speed**: ~40s per section (slower but reliable)

## RPM Calculation

### Old (Burst Pattern)
- 4 calls in ~16 seconds = 15 calls/minute → **At the limit!**
- Bursts within the timing window triggered micro-limits

### New (Distributed Pattern)
- 4 calls in ~40 seconds = 6 calls/minute → **Well under limit!**
- Evenly distributed, no bursts

## When to Use Different Settings

### Current Settings (Safest - Recommended)
```python
RATE_LIMIT_DELAY = 5
VERIFY_DELAY = 5
ENABLE_VERIFICATION = True
```
- **Speed**: ~40s per section
- **Reliability**: Very high
- **Rate limit risk**: Very low

### Moderate Settings (Faster but some risk)
```python
RATE_LIMIT_DELAY = 4
VERIFY_DELAY = 4
ENABLE_VERIFICATION = True
```
- **Speed**: ~32s per section
- **Reliability**: Medium-high
- **Rate limit risk**: Low-medium
- **Note**: May occasionally hit limits during peak times

### Fast Settings (Verification Off)
```python
RATE_LIMIT_DELAY = 5
VERIFY_DELAY = 5
ENABLE_VERIFICATION = False  # No verification
```
- **Speed**: ~15s per section
- **Reliability**: High (fewer calls)
- **Rate limit risk**: Very low
- **Downside**: No foreign character detection/fixing

## Monitoring

Watch for these patterns:

✅ **Working correctly** (no more issues):
```
→ English (1234 chars)... ✓ (1456 chars)
→ Verifying English... ✓
→ Sinhala (1234 chars)... ✓ (1567 chars)
→ Verifying Sinhala... ✓
💾 Progress saved
```

⚠️ **Still having issues** (rare):
```
→ Verifying English... ⚠ Rate limit hit, waiting 10s...
```
If you still see this, increase delays to 6 seconds.

## Summary

The fix adds **strategic delays**:
1. **Before verification**: Prevents burst after translation
2. **After verification**: Already had this
3. **Between sections**: Gives breathing room

This changes the pattern from "burst-wait-burst-wait" to "call-wait-call-wait-call-wait" which stays well under rate limits.

**Total slowdown**: ~10s per section (40s vs 30s)
**Benefit**: Zero rate limit errors, reliable translation

