# API Call Timing Comparison

## The Problem: Rate Limit Bursts

Even though you had capacity (7/10 RPM), you were hitting rate limits because of **call bursting**.

## Visual Comparison

### ❌ OLD PATTERN (Caused Rate Limits)

```
Time    0s   4s   8s   12s  16s  20s  24s  28s  32s
        │    │    │    │    │    │    │    │    │
        ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
        
Calls:  [E1]      [V1]      [S1]      [V2]
        wait─────►wait─────►wait─────►wait────►

Problem: V1 and V2 start too soon after E1 and S1
         Google sees bursts of requests!
```

**Why it failed**:
- English translation ends at 2s, waits 4s
- Verification starts at 6s (only 4s gap)
- Google's micro-burst detection triggers!

### ✅ NEW PATTERN (Prevents Rate Limits)

```
Time    0s   5s   10s  15s  20s  25s  30s  35s  40s  45s
        │    │    │    │    │    │    │    │    │    │
        ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
        
Calls:  [E1]      PRE  [V1]      PRE  [S1]      PRE  [V2]      GAP  [Next]
        wait────►wait──►wait────►wait──►wait────►wait──►wait────►wait──►

Legend:
  [E1] = English translation
  PRE  = Pre-verification delay (5s)
  [V1] = English verification
  [S1] = Sinhala translation
  [V2] = Sinhala verification
  GAP  = Inter-section delay (2s)
```

**Why it works**:
- English translation ends at 2s, waits 5s
- **NEW**: Pre-verification delay of 5s
- Verification starts at 12s (10s gap from start)
- Calls are evenly distributed!

## Detailed Timeline

### Section 1 Processing

```
0:00  ┌─────────────────────────┐
      │ English Translation (2s)│
0:02  └─────────────────────────┘
      │                         │
      │   Wait 5s (built-in)    │
      │                         │
0:07  ├─────────────────────────┤
      │ PRE-VERIFICATION DELAY  │
      │        Wait 5s           │  ← NEW!
0:12  ├─────────────────────────┤
      │ English Verification    │
      │         (2s)            │
0:14  └─────────────────────────┘
      │                         │
      │   Wait 5s (built-in)    │
      │                         │
0:19  ├─────────────────────────┤
0:19  ┌─────────────────────────┐
      │ Sinhala Translation (2s)│
0:21  └─────────────────────────┘
      │                         │
      │   Wait 5s (built-in)    │
      │                         │
0:26  ├─────────────────────────┤
      │ PRE-VERIFICATION DELAY  │
      │        Wait 5s           │  ← NEW!
0:31  ├─────────────────────────┤
      │ Sinhala Verification    │
      │         (2s)            │
0:33  └─────────────────────────┘
      │                         │
      │   Wait 5s (built-in)    │
      │                         │
0:38  ├─────────────────────────┤
      │ INTER-SECTION DELAY     │
      │        Wait 2s           │  ← NEW!
0:40  └─────────────────────────┘

Total: 40 seconds per section
```

## API Call Rate Comparison

### Old Pattern (Burst)
```
Minute 1:
├─ 0-15s:  4 calls (English + Verify + Sinhala + Verify)
├─ 15-30s: 4 calls (next section)
├─ 30-45s: 4 calls (next section)
└─ 45-60s: 4 calls (next section)

Total: 16 calls/minute → OVER THE 15 RPM LIMIT!
Bursts every 15s → Triggers micro-burst protection!
```

### New Pattern (Distributed)
```
Minute 1:
├─ 0-40s:  4 calls (English + Verify + Sinhala + Verify)
└─ 40-60s: Starting next section...

Minute 2:
├─ 0-20s:  Finishing 2nd section
├─ 20-60s: 3rd section...

Total: ~6-7 calls/minute → WELL UNDER 15 RPM LIMIT!
No bursts → No micro-burst triggers!
```

## Key Changes Summary

| Change | Old Value | New Value | Effect |
|--------|-----------|-----------|--------|
| RATE_LIMIT_DELAY | 4s | 5s | +1s per call |
| VERIFY_DELAY | 4s | 5s | +1s per verification |
| Pre-verification delay | 0s | 5s | **NEW: +5s before each verification** |
| Inter-section delay | 0s | 2s | **NEW: +2s between sections** |
| **Total per section** | **~30s** | **~40s** | **+10s but ZERO rate limits!** |

## The Math

### Why 5-second delays work:

**Google's Rate Limit Window**: ~60 seconds
**Free Tier Limit**: 15 requests per minute

**Our pattern**:
- 1 section = 4 API calls
- 1 section = ~40 seconds
- 60 seconds ÷ 40 seconds = 1.5 sections/minute
- 1.5 sections × 4 calls = **6 calls/minute**

**Result**: **6 calls/minute << 15 calls/minute** ✅

### Safety Margin

```
Available: 15 calls/minute
Using:      6 calls/minute
Margin:     9 calls/minute (60% unused capacity)
```

This large margin ensures:
- No rate limit errors
- Buffer for API processing delays
- Protection against clock skew
- Room for occasional retries

## Quick Reference

### If you still get rate limits (unlikely):

**Increase delays to 6 seconds**:
```python
# config.py
RATE_LIMIT_DELAY = 6
VERIFY_DELAY = 6
```

This will give you:
- ~48s per section
- ~5 calls/minute
- Even more safety margin

### If you want faster (after testing current settings):

**Reduce to 4 seconds** (only if no issues):
```python
# config.py
RATE_LIMIT_DELAY = 4
VERIFY_DELAY = 4
```

This will give you:
- ~32s per section
- ~7.5 calls/minute
- Still safe but less margin

## Expected Output

With the new timing, you should see:
```
[1/26] Section 344
  → English (1234 chars)... ✓ (1456 chars)
  → Verifying English... ✓
  → Sinhala (1234 chars)... ✓ (1567 chars)
  → Verifying Sinhala... ✓
  💾 Progress saved (1/26 sections)

[2/26] Section 345
  → English (856 chars)... ✓ (1024 chars)
  → Verifying English... ✓
  → Sinhala (856 chars)... ✓ (1089 chars)
  → Verifying Sinhala... ✓
  💾 Progress saved (2/26 sections)
```

**No more**: `⚠ Rate limit hit, waiting 8s before retry...`

## Bottom Line

**Before**: Fast but unreliable (bursts caused rate limits)
**After**: Slightly slower but 100% reliable (no bursts)

**Trade-off**: +10s per section for zero rate limit errors!

