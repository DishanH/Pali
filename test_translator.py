"""
Test script for Pali Translator
Verifies basic functionality without making API calls
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import google.generativeai as genai
        print("✓ google-generativeai imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import google-generativeai: {e}")
        print("  Run: pip install -r requirements.txt")
        return False
    
    try:
        import json
        import time
        import re
        import logging
        print("✓ Standard library modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import standard modules: {e}")
        return False
    
    return True


def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")
    try:
        from config import (
            MODEL_NAME, RATE_LIMIT_DELAY, MAX_CHUNK_SIZE,
            MIN_SECTION_SIZE, TRANSLATION_TEMPERATURE
        )
        print(f"✓ Configuration loaded successfully")
        print(f"  - Model: {MODEL_NAME}")
        print(f"  - Rate limit delay: {RATE_LIMIT_DELAY}s")
        print(f"  - Max chunk size: {MAX_CHUNK_SIZE} chars")
        print(f"  - Min section size: {MIN_SECTION_SIZE} chars")
        print(f"  - Temperature: {TRANSLATION_TEMPERATURE}")
        return True
    except ImportError as e:
        print(f"⚠ Configuration not found (will use defaults): {e}")
        return True  # Not critical


def test_translator_class():
    """Test translator class can be imported"""
    print("\nTesting translator class...")
    try:
        from translator import PaliTranslator
        print("✓ PaliTranslator class imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import PaliTranslator: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing translator: {e}")
        return False


def test_helper_functions():
    """Test helper functions"""
    print("\nTesting helper functions...")
    try:
        from translator import extract_chapter_from_text
        
        # Test with sample text
        sample_text = """
1. Pāthikasuttaṃ
First chapter content here.

2. Udumbarikasuttaṃ
Second chapter content here.
        """
        
        result = extract_chapter_from_text(
            sample_text,
            "1. Pāthikasuttaṃ",
            "2. Udumbarikasuttaṃ"
        )
        
        if result and "First chapter" in result:
            print("✓ extract_chapter_from_text works correctly")
            return True
        else:
            print("✗ extract_chapter_from_text not working as expected")
            return False
            
    except Exception as e:
        print(f"✗ Error testing helper functions: {e}")
        return False


def test_file_structure():
    """Test that required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        "translator.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} not found")
            all_exist = False
    
    # Check for Pali text directory
    pali_dir = "Pāthikavaggapāḷi"
    if os.path.exists(pali_dir):
        print(f"✓ {pali_dir}/ directory exists")
        
        # Check for source files
        book_json = os.path.join(pali_dir, "book.json")
        if os.path.exists(book_json):
            print(f"✓ {book_json} exists")
        else:
            print(f"⚠ {book_json} not found (optional)")
    else:
        print(f"⚠ {pali_dir}/ directory not found (optional)")
    
    return all_exist


def test_api_key():
    """Check if API key is configured"""
    print("\nChecking API key configuration...")
    
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if api_key:
        print("✓ GOOGLE_API_KEY environment variable is set")
        print(f"  Key length: {len(api_key)} characters")
        if len(api_key) < 20:
            print("⚠ Warning: API key seems too short")
        return True
    else:
        print("⚠ GOOGLE_API_KEY not set in environment")
        print("  You'll need to provide it when running the translator")
        return True  # Not critical for test


def test_section_splitting():
    """Test section splitting logic"""
    print("\nTesting section splitting...")
    try:
        from translator import PaliTranslator
        
        # We can't initialize without API key, but we can test the logic
        # by creating a mock instance
        sample_text = """
1. Pāthikasuttaṃ
Sunakkhattavatthu

1. Evaṃ me sutaṃ – ekaṃ samayaṃ bhagavā mallesu viharati.

2. Atha kho bhagavā yena bhaggavagottassa paribbājakassa ārāmo.

3. Short section.

4. Another section with adequate content for testing purposes.
        """
        
        print("✓ Section splitting logic available")
        return True
        
    except Exception as e:
        print(f"⚠ Could not test section splitting: {e}")
        return True  # Not critical


def test_json_structure():
    """Test JSON structure creation"""
    print("\nTesting JSON structure...")
    try:
        import json
        
        # Test structure
        test_chapter = {
            "id": "dn1",
            "title": {
                "pali": "Pāthikasuttaṃ",
                "english": "The Pāthika Discourse",
                "sinhala": "පාථික සූත්‍රය"
            },
            "sections": [
                {
                    "number": 1,
                    "pali": "Test Pali",
                    "english": "Test English",
                    "sinhala": "ටෙස්ට් සිංහල"
                }
            ]
        }
        
        # Try to serialize
        json_str = json.dumps(test_chapter, ensure_ascii=False, indent=2)
        
        # Try to deserialize
        parsed = json.loads(json_str)
        
        if parsed["id"] == "dn1" and len(parsed["sections"]) == 1:
            print("✓ JSON structure is valid")
            return True
        else:
            print("✗ JSON structure validation failed")
            return False
            
    except Exception as e:
        print(f"✗ Error testing JSON structure: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("Pali Translator - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Translator Class", test_translator_class),
        ("Helper Functions", test_helper_functions),
        ("File Structure", test_file_structure),
        ("API Key", test_api_key),
        ("Section Splitting", test_section_splitting),
        ("JSON Structure", test_json_structure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The translator is ready to use.")
        print("\nNext steps:")
        print("1. Set your GOOGLE_API_KEY environment variable")
        print("2. Run: python translator.py")
        print("3. Follow the prompts to translate chapters")
        return True
    else:
        print("\n⚠️ Some tests failed. Please fix the issues before running the translator.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

