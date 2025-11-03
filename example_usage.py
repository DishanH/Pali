"""
Example usage of the Pali Translator

This script demonstrates how to:
1. Translate a single section
2. Translate a complete chapter
3. Handle rate limits and errors
"""

from translator import PaliTranslator
import os

def example_single_translation():
    """Example: Translate a single Pali passage"""
    print("=" * 60)
    print("Example 1: Single Translation")
    print("=" * 60)
    
    # Initialize translator
    api_key = os.getenv("GOOGLE_API_KEY", "")
    translator = PaliTranslator(api_key)
    
    # Sample Pali text
    pali_text = """
    Evaṃ me sutaṃ – ekaṃ samayaṃ bhagavā mallesu viharati anupiyaṃ nāma 
    mallānaṃ nigamo. Atha kho bhagavā pubbaṇhasamayaṃ nivāsetvā 
    pattacīvaramādāya anupiyaṃ piṇḍāya pāvisi.
    """
    
    print("\nOriginal Pali:")
    print(pali_text)
    
    # Translate to English
    print("\nTranslating to English...")
    english = translator.translate_text(pali_text, "English")
    print("\nEnglish Translation:")
    print(english)
    
    # Translate to Sinhala
    print("\nTranslating to Sinhala...")
    sinhala = translator.translate_text(pali_text, "Sinhala")
    print("\nSinhala Translation:")
    print(sinhala)
    print()


def example_chapter_translation():
    """Example: Translate a complete chapter"""
    print("=" * 60)
    print("Example 2: Chapter Translation")
    print("=" * 60)
    
    # Initialize translator
    api_key = os.getenv("GOOGLE_API_KEY", "")
    translator = PaliTranslator(api_key)
    
    # Sample chapter text (first few sections of Pāthikasuttaṃ)
    chapter_text = """
1. Pāthikasuttaṃ
Sunakkhattavatthu

1. Evaṃ me sutaṃ – ekaṃ samayaṃ bhagavā mallesu viharati anupiyaṃ nāma 
mallānaṃ nigamo. Atha kho bhagavā pubbaṇhasamayaṃ nivāsetvā 
pattacīvaramādāya anupiyaṃ piṇḍāya pāvisi.

2. Atha kho bhagavā yena bhaggavagottassa paribbājakassa ārāmo, yena bhaggavagotto
paribbājako tenupasaṅkami. Atha kho bhaggavagotto paribbājako bhagavantaṃ etadavoca – 
'etu kho, bhante, bhagavā. Svāgataṃ, bhante, bhagavato.'
    """
    
    print("\nTranslating chapter (this will take a few moments due to rate limiting)...")
    
    try:
        chapter_data = translator.translate_chapter(
            pali_text=chapter_text,
            chapter_id="dn1",
            chapter_title="Pāthikasuttaṃ"
        )
        
        print("\n✓ Translation complete!")
        print(f"- Chapter ID: {chapter_data['id']}")
        print(f"- Title (Pali): {chapter_data['title']['pali']}")
        print(f"- Title (English): {chapter_data['title']['english']}")
        print(f"- Title (Sinhala): {chapter_data['title']['sinhala']}")
        print(f"- Number of sections: {len(chapter_data['sections'])}")
        
        # Save to file
        output_path = "example_output.json"
        translator.save_chapter_json(chapter_data, output_path)
        print(f"\n✓ Saved to: {output_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_section_processing():
    """Example: Demonstrate section processing logic"""
    print("=" * 60)
    print("Example 3: Section Processing")
    print("=" * 60)
    
    # Initialize translator
    api_key = os.getenv("GOOGLE_API_KEY", "")
    translator = PaliTranslator(api_key)
    
    # Sample text with multiple sections
    sample_text = """
1. Pāthikasuttaṃ
Sunakkhattavatthu

1. First section with content here.

2. Second section with more content.

3. Third section is very short.

4. Fourth section has adequate length for processing independently.
    """
    
    print("\nOriginal text structure:")
    print(sample_text)
    
    # Split into sections
    sections = translator.split_into_sections(sample_text)
    print(f"\n✓ Split into {len(sections)} initial sections")
    
    # Process sections (combine/split)
    processed = translator.process_sections(sections)
    print(f"✓ Processed into {len(processed)} optimized sections")
    
    print("\nSection details:")
    for i, section in enumerate(processed, 1):
        pali_len = len(section.get('pali', ''))
        title = section.get('title', 'No title')
        print(f"  Section {i}: {pali_len} chars, Title: {title[:30]}...")


def main():
    """Run all examples"""
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        print("=" * 60)
        print("ERROR: No API key found!")
        print("=" * 60)
        print("\nPlease set the GOOGLE_API_KEY environment variable:")
        print("\nWindows (PowerShell):")
        print('  $env:GOOGLE_API_KEY="your-api-key-here"')
        print("\nWindows (Command Prompt):")
        print('  set GOOGLE_API_KEY=your-api-key-here')
        print("\nLinux/Mac:")
        print('  export GOOGLE_API_KEY="your-api-key-here"')
        return
    
    print("\n" + "=" * 60)
    print("Pali Translator - Example Usage")
    print("=" * 60)
    print("\nThis script demonstrates various translator features.")
    print("Each example includes rate limiting delays.")
    print("\nPress Ctrl+C to stop at any time.\n")
    
    try:
        # Run examples
        input("Press Enter to run Example 1 (Single Translation)...")
        example_single_translation()
        
        input("\nPress Enter to run Example 2 (Chapter Translation)...")
        example_chapter_translation()
        
        input("\nPress Enter to run Example 3 (Section Processing)...")
        example_section_processing()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n\nError running examples: {e}")


if __name__ == "__main__":
    main()

