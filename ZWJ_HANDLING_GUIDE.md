# ZWJ (Zero Width Joiner) Handling Guide

## Issue Overview
Found `#zwj;` placeholders in Sinhala text across JSON files. These are placeholders for the Zero Width Joiner (ZWJ) character, which is essential for proper Sinhala conjunct consonant rendering.

## Analysis Results
- **Files affected**: 15 JSON files
- **Total occurrences**: 305 `#zwj;` placeholders
- **Most affected**: `an11.2-Anussativaggo.json` (68 occurrences)
- **Common patterns**: `සත්#zwj;ත්වයෝ`, `ධර්‍#zwj;මය`, `භාග්‍ය#zwj;වතුන්`

## What is ZWJ?
- **ZWJ (Zero Width Joiner)**: Unicode character U+200D
- **Purpose**: Forms conjunct consonants in Sinhala script
- **Critical**: Essential for proper text rendering
- **Example**: `සත්#zwj;ත්වයෝ` should render as `සත්‍ත්වයෝ`

## Recommended Approach: Display-Time Cleaning ✅

### Why Display-Time Cleaning?
1. **Safe**: Original data remains unchanged
2. **Reversible**: Can modify approach anytime
3. **Flexible**: Different rules for different contexts
4. **Testable**: Easy to test without permanent changes
5. **Maintainable**: Centralized cleaning logic

### Implementation

#### 1. Use ZWJHandler Class
```python
from zwj_handler import ZWJHandler

# Clean individual text
clean_text = ZWJHandler.clean_text_for_display(original_text)

# Clean entire chapter
clean_chapter = ZWJHandler.get_display_ready_chapter(file_path)

# Clean any JSON object
clean_data = ZWJHandler.clean_json_object_for_display(data)
```

#### 2. Integration Examples

**API Endpoint:**
```python
def get_chapter(chapter_id):
    # Load from database/file
    raw_data = load_chapter_data(chapter_id)
    
    # Clean for display
    return ZWJHandler.clean_json_object_for_display(raw_data)
```

**Database Query Wrapper:**
```python
def get_section_text(chapter_id, section_num, language='sinhala'):
    raw_text = query_database(chapter_id, section_num, language)
    return ZWJHandler.clean_text_for_display(raw_text)
```

**Web Application:**
```python
# In your template rendering
chapter_data = ZWJHandler.get_display_ready_chapter(file_path)
render_template('chapter.html', chapter=chapter_data)
```

## Alternative: Permanent Database Fix ⚠️

### When to Consider
- You want to eliminate the issue permanently
- You have good backups
- You've tested rendering thoroughly
- You're confident about the replacement

### Implementation
```bash
# CAUTION: Makes permanent changes!
python fix_zwj_optional.py
```

### What It Does
1. Replaces all `#zwj;` with actual ZWJ character (`\u200D`)
2. Updates JSON files permanently
3. Updates Turso database with fixed text
4. Provides dry-run option first

## Files Created

### Core Handler (Recommended)
- `zwj_handler.py` - Main ZWJ handling utilities
- `zwj_usage_example.py` - Usage examples and integration guide

### Analysis Tools
- `analyze_zwj_issue.py` - Comprehensive analysis of ZWJ issues

### Optional Fix (Use with Caution)
- `fix_zwj_optional.py` - Permanent fix script with safety checks

## Usage Recommendations

### For Development/Testing
```python
# Test rendering with cleaned text
from zwj_handler import ZWJHandler

# Load and clean a chapter
chapter = ZWJHandler.get_display_ready_chapter('path/to/chapter.json')

# Test in your application
render_chapter(chapter)
```

### For Production
```python
# Add to your text processing pipeline
class TextProcessor:
    @staticmethod
    def prepare_for_display(text, language='sinhala'):
        if language == 'sinhala':
            text = ZWJHandler.clean_text_for_display(text)
        return text
```

### For API Responses
```python
# Clean data before sending to frontend
@app.route('/api/chapter/<chapter_id>')
def get_chapter_api(chapter_id):
    raw_data = load_chapter(chapter_id)
    clean_data = ZWJHandler.clean_json_object_for_display(raw_data)
    return jsonify(clean_data)
```

## Testing Checklist

### Before Implementation
- [ ] Test ZWJ rendering in target browsers/apps
- [ ] Verify fonts support ZWJ properly
- [ ] Test with different Sinhala text samples
- [ ] Check mobile device rendering

### After Implementation
- [ ] Compare original vs cleaned text rendering
- [ ] Test search functionality (if applicable)
- [ ] Verify copy/paste behavior
- [ ] Check accessibility tools compatibility

## Performance Considerations

### Optimization Tips
1. **Cache cleaned text** if processing is expensive
2. **Clean only when needed** (e.g., only Sinhala text)
3. **Batch process** multiple texts together
4. **Use lazy loading** for large datasets

### Example Caching
```python
from functools import lru_cache

class CachedZWJHandler:
    @staticmethod
    @lru_cache(maxsize=1000)
    def clean_text_cached(text):
        return ZWJHandler.clean_text_for_display(text)
```

## Troubleshooting

### Common Issues
1. **Text appears broken**: Font may not support ZWJ
2. **Performance slow**: Consider caching or batch processing
3. **Copy/paste issues**: ZWJ characters may behave differently

### Solutions
1. **Font issues**: Test with Unicode-compliant Sinhala fonts
2. **Performance**: Implement caching or clean only visible text
3. **Copy/paste**: Document expected behavior for users

## Migration Path

### Phase 1: Implement Display-Time Cleaning
1. Add `ZWJHandler` to your codebase
2. Implement in one component/endpoint
3. Test thoroughly
4. Gradually expand to other components

### Phase 2: Optimize (Optional)
1. Add caching if needed
2. Optimize for performance
3. Consider permanent fix if confident

### Phase 3: Permanent Fix (Optional)
1. Ensure thorough testing
2. Create backups
3. Run `fix_zwj_optional.py` with dry-run first
4. Apply permanent fix
5. Remove display-time cleaning code

## Status: ✅ READY FOR IMPLEMENTATION

**Recommended Action**: Start with display-time cleaning using `ZWJHandler`
- Safe and reversible
- Easy to test and implement
- Maintains data integrity
- Provides immediate solution

**Files Ready**:
- `zwj_handler.py` - Production-ready handler
- `zwj_usage_example.py` - Integration examples
- `analyze_zwj_issue.py` - Analysis tools
- `fix_zwj_optional.py` - Optional permanent fix