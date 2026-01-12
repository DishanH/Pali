#!/usr/bin/env python3
"""
Test the Unicode fix on a small sample before production use
"""

import json
from production_safe_unicode_fix import ProductionSafeUnicodeFixer

def test_unicode_fixes():
    """
    Test all Unicode fix patterns
    """
    print("=" * 60)
    print("TESTING UNICODE FIX PATTERNS")
    print("=" * 60)
    
    fixer = ProductionSafeUnicodeFixer()
    
    # Test cases covering all issues found
    test_cases = [
        # ZWJ placeholders
        ("සත්#zwj;ත්වයෝ", "සත්‍ත්වයෝ"),
        ("ධර්‍#zwj;මය", "ධර්‍මය"),  # Excessive ZWJ cleaned up
        ("භාග්‍ය#zwj;වතුන්", "භාග්‍ය‍වතුන්"),
        
        # HTML entities
        ("සත්&zwj;ත්වයෝ", "සත්‍ත්වයෝ"),
        
        # Literal Unicode notation - consecutive {U+200D} should be cleaned
        ("උ{U+200D}ර්මිභය සූත{U+200D}්{U+200D}රය", "උ‍ර්මිභය සූත්‍රය"),
        
        # Unicode escapes
        ("ප්\\u200Dරතිසංඛ", "ප්‍රතිසංඛ"),
        ("අ\\u0DCAකුසල", "අ්කුසල"),
        
        # Multiple consecutive ZWJ (should be cleaned to single ZWJ)
        ("සත්‍‍‍ත්වයෝ", "සත්‍ත්වයෝ"),
        
        # Mixed issues - excessive ZWJ will be cleaned
        ("ධර්‍#zwj;මය\\u200Dන්", "ධර්‍මය‍න්"),
    ]
    
    print("🧪 Testing fix patterns:")
    all_passed = True
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        fixed_text, fix_count = fixer.fix_unicode_issues(input_text)
        
        if fixed_text == expected:
            print(f"  ✅ Test {i}: PASS ({fix_count} fixes)")
            print(f"     Input:    {repr(input_text)}")
            print(f"     Expected: {repr(expected)}")
            print(f"     Got:      {repr(fixed_text)}")
        else:
            print(f"  ❌ Test {i}: FAIL")
            print(f"     Input:    {repr(input_text)}")
            print(f"     Expected: {repr(expected)}")
            print(f"     Got:      {repr(fixed_text)}")
            all_passed = False
        print()
    
    return all_passed

def test_on_real_file():
    """
    Test on a real file that has issues
    """
    print("=" * 60)
    print("TESTING ON REAL FILE")
    print("=" * 60)
    
    # Test on the file we know has issues
    from pathlib import Path
    test_file = Path("Saṃyuttanikāyo/Mahāvaggo/chapters/sn.5.12-Saccasaṃyuttaṃ.json")
    
    if not test_file.exists():
        print("❌ Test file not found")
        return False
    
    fixer = ProductionSafeUnicodeFixer()
    
    # Test dry run
    success, message, fix_count = fixer.fix_json_file(test_file, dry_run=True)
    
    print(f"📄 Test file: {test_file.name}")
    print(f"🔍 Dry run result: {message}")
    print(f"🔧 Fixes needed: {fix_count}")
    
    if fix_count > 0:
        print(f"\n📝 Sample of issues in file:")
        
        # Show some examples
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find examples of each issue type
        import re
        
        zwj_examples = re.findall(r'[^\s]*#zwj;[^\s]*', content)[:3]
        unicode_examples = re.findall(r'[^\s]*\{U\+[0-9A-Fa-f]+\}[^\s]*', content)[:3]
        
        if zwj_examples:
            print(f"   #zwj; examples: {zwj_examples}")
        
        if unicode_examples:
            print(f"   {{U+XXXX}} examples: {unicode_examples}")
    
    return success

def main():
    """
    Run all tests
    """
    print("🧪 UNICODE FIX TESTING SUITE")
    print("Testing before production use...")
    
    # Test 1: Pattern fixes
    patterns_ok = test_unicode_fixes()
    
    # Test 2: Real file
    real_file_ok = test_on_real_file()
    
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if patterns_ok and real_file_ok:
        print("✅ ALL TESTS PASSED!")
        print("🚀 Ready for production use")
        print("\nNext steps:")
        print("1. Run: python production_safe_unicode_fix.py")
        print("2. Follow the interactive prompts")
        print("3. Review dry run results carefully")
        print("4. Proceed with fixes if satisfied")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🛑 DO NOT use in production until fixed")
        
        if not patterns_ok:
            print("   - Pattern fix tests failed")
        if not real_file_ok:
            print("   - Real file test failed")

if __name__ == "__main__":
    main()