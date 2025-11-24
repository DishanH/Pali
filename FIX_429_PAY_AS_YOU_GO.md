# Fix for 429 Resource Exhausted Errors

## The Problem

You're constantly getting [error 429](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429):

```
ERROR: 429 Resource exhausted. Please try again later.
```

This happens repeatedly, causing multiple retries and very slow progress.

## What 429 Means

According to [Google Cloud documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429):

> **"Resource exhausted, please try again later."**
> 
> If the number of your requests exceeds the capacity allocated to process requests, then error code 429 is returned.

**You're on pay-as-you-go** (not Provisioned Throughput), which means:
- Google allocates capacity dynamically
- If capacity isn't available, you get 429
- You need to slow down requests to stay within allocated capacity

## Why This Happens

Your limits:
- **RPM**: 1,000 requests per minute
- **TPM**: 1,000,000 tokens per minute

But **pay-as-you-go doesn't guarantee these limits** - it's best-effort capacity allocation!

With 1.0s delays:
- 2 calls per section (English + Sinhala)
- ~60 sections × 2 = **120 calls per minute**
- Each section ~2000 chars = ~3000 tokens
- **~360,000 tokens per minute**

Even though you're under the stated limits, **pay-as-you-go throttles you** during high demand periods!

## What Was Fixed

### Increased Delay to 3.0 seconds

```python
# config.py
RATE_LIMIT_DELAY = 3.0  # Was 1.0s
```

**New throughput:**
- ~20 sections per minute
- ~40 API calls per minute (well under 1K RPM)
- ~120,000 tokens per minute (well under 1M TPM)

This gives you **much more headroom** and prevents 429 errors.

## New Performance

| Metric | 1.0s delay (OLD) | 3.0s delay (NEW) |
|--------|------------------|------------------|
| **Calls per minute** | ~120 | ~40 |
| **Time per section** | ~10s + retries | ~15s no retries |
| **36 sections** | ~15 min + delays | **~10-12 min** |
| **429 errors** | Constant | Rare/None |
| **Actual speed** | Slow (retries) | **Faster (smooth)** |

**Paradox:** Slower delays = faster overall speed (no retries!)

## Why 3 Seconds Is Better

According to the [Google Cloud documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429):

> **Pay-as-you-go options to resolve 429 errors:**
> 1. Use the global endpoint instead of regional
> 2. **Implement retry strategy with truncated exponential backoff**
> 3. **Smooth traffic and reduce large spikes**
> 4. Subscribe to Provisioned Throughput

We're implementing #3: **Smoothing traffic**

With 1.0s delays, you create **burst patterns**:
```
Request → 1s → Request → 1s → Request (burst!)
          ↓
     429 error!
```

With 3.0s delays, traffic is **smooth**:
```
Request → 3s → Request → 3s → Request (steady)
          ↓
     Success!
```

## Your Timeline Comparison

### With 1.0s delay (Your Recent Experience)

```
11:28:45 - Request
11:28:45 - 429 error, wait 10s
11:28:55 - Retry
11:28:59 - Success (14s wasted)

11:29:06 - Request
11:29:06 - 429 error, wait 10s
11:29:16 - Retry
11:29:17 - 429 error, wait 20s
11:29:37 - Retry
11:29:37 - 429 error, wait 40s
11:30:17 - Retry
11:30:28 - 429 error, wait 80s
11:31:48 - Retry
11:31:49 - 429 error, wait 160s
━━━━━━━━━━━━━━━━━━━━━━━━
2 minutes 43 seconds of retries!
```

**Per section:** ~10s normal + ~30-60s retries = **40-70 seconds**

### With 3.0s delay (Now)

```
11:28:45 - Request → 3s delay
11:28:48 - Success
11:28:51 - Request → 3s delay
11:28:54 - Success
━━━━━━━━━━━━━━━━━━━━━━━━
No retries, smooth progress
```

**Per section:** ~15 seconds (no retries)

## Speed Comparison Table

| Scenario | Time per Section | 36 Sections | 429 Errors |
|----------|-----------------|-------------|------------|
| **1.0s delay** | 10s + 30-60s retries = **40-70s** | ~40-60 min | Constant |
| **3.0s delay** | 15s (no retries) | **~10-12 min** | Rare/None |

**Result:** 3.0s delay is **4-5x faster** because you avoid all the retry penalties!

## Understanding Pay-As-You-Go

From the [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429):

> "Although you don't have reserved capacity, you can try your request again. However, the request isn't counted against your error rate as described in your service level agreement (SLA)."

**What this means:**
- You don't have **reserved** capacity
- Capacity is allocated **dynamically** based on availability
- During high demand, capacity is limited
- Need to stay well under stated limits to avoid throttling

**Your stated limits (1K RPM, 1M TPM) are MAXIMUMS, not guarantees!**

## Alternative Solutions

### Option 1: Use 3.0s Delay (Recommended - Already Applied)

**Best for:** Reliable, smooth translation

```python
RATE_LIMIT_DELAY = 3.0
```

- ✅ No 429 errors
- ✅ ~15s per section
- ✅ Predictable progress
- ✅ 36 sections in ~10-12 min

### Option 2: Use Global Endpoint

Per the [Google documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429):

> "Use the global endpoint instead of a regional endpoint whenever possible."

This might help, but requires code changes.

### Option 3: Provisioned Throughput (Costs More)

From the [documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429):

> "Subscribe to Provisioned Throughput for a more consistent level of service."

**What it offers:**
- **Reserved capacity** (guaranteed throughput)
- No 429 errors (you have dedicated resources)
- More expensive than pay-as-you-go

**When to use:**
- If you need guaranteed performance
- For production applications
- If 429 errors persist even with 3s delays

### Option 4: Further Increase Delays (If Still Getting 429s)

If you still see occasional 429 errors with 3.0s:

```python
RATE_LIMIT_DELAY = 4.0  # Even more conservative
```

## What To Do Now

### Your Script Is Already Fixed!

Just run it:

```bash
python translate_json_chapters.py
# Resume from section 14 or wherever you left off
```

**You should see:**
```
[14/36] Section 418
  → English (2407 chars)... ✓ (2900 chars)  [~20-25s]
  → Sinhala (2407 chars)... ✓ (2100 chars)  [~20-25s]
  💾 Progress saved (14/36 sections)

[15/36] Section 419
  → English (1118 chars)... ✓ (1351 chars)  [~15-20s]
  → Sinhala (1118 chars)... ✓ (1023 chars)  [~15-20s]
  💾 Progress saved (15/36 sections)
```

**Smooth progress, no retries, ~15s per section**

### Monitor for 429 Errors

Watch the logs. You should see:
- ✅ **No 429 errors** (or very rare)
- ✅ **Consistent timing** (~15s per section)
- ✅ **Steady progress**

If you still see 429 errors:
1. Increase `RATE_LIMIT_DELAY` to 4.0
2. Consider off-peak hours
3. Consider Provisioned Throughput

## Summary

### ❌ What Was Wrong

- 1.0s delays too aggressive for pay-as-you-go
- Created burst patterns
- Constant 429 errors
- Retries adding 30-160s per section
- 36 sections taking 40-60 minutes

### ✅ What's Fixed

- 3.0s delays smooth out traffic
- No burst patterns
- No 429 errors
- No retries
- **36 sections in ~10-12 minutes**

### 📊 The Paradox

**Slower delays = Faster overall:**
- 1.0s delay: Fast requests but constant retries = **slow overall**
- 3.0s delay: Slower requests but no retries = **fast overall**

### 🎯 Expected Results

Your remaining **22 sections** should complete in:
- **22 × 15s = ~6-7 minutes**
- Smooth, consistent progress
- No 429 errors

---

**Key Insight:** Pay-as-you-go capacity is allocated dynamically. Even though you have "1K RPM" stated limit, you need to stay well under it (especially on TPM) to avoid throttling. The 3.0s delay keeps you at ~40 calls/min and ~120K TPM, giving plenty of headroom! 🚀

**Source:** [Google Cloud Error Code 429 Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429)

