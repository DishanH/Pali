#!/usr/bin/env python3
"""
Example usage of ZWJ Handler for display-time cleaning
This is the RECOMMENDED approach - safe and reversible
"""

import json
from pathlib import Path
from zwj_handler import ZWJHandler

def example_api_endpoint():
    """
    Example: How to use ZWJ handler in an API endpoint
    """
    print("=" * 60)
    print("Example: API Endpoint Usage")
    print("=" * 60)
    
    # Simulate loading chapter data (with #zwj issues)
    chapter_file = Path("Aṅguttaranikāyo/Dasakanipātapāḷi/chapters/an10.11-Samaṇasaññāvaggo.json")
    
    if not chapter_file.exists():
        print("❌ Example file not found")
        return
    
    # Method 1: Clean entire chapter at once
    print("📖 Method 1: Clean entire chapter")
    clean_chapter = ZWJHandler.get_display_ready_chapter(chapter_file)
    
    if clean_chapter:
        print(f"✅ Chapter loaded and cleaned: {clean_chapter['id']}")
        print(f"   Title: {clean_chapter['title']['sinhala']}")
        
        # Show first section with cleaned text
        for section in clean_chapter['sections']:
            if section.get('sinhala') and len(section['sinhala']) > 50:
                print(f"   Section {section['number']}: {section['sinhala'][:100]}...")
                break
    
    print("\n" + "-" * 60)
    
    # Method 2: Clean individual text fields
    print("📝 Method 2: Clean individual text fields")
    
    # Load original data
    with open(chapter_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Clean specific fields as needed
    clean_title = ZWJHandler.clean_text_for_display(original_data['title']['sinhala'])
    print(f"✅ Cleaned title: {clean_title}")
    
    # Clean a section's Sinhala text
    for section in original_data['sections']:
        if section.get('sinhala') and '#zwj;' in section['sinhala']:
            original_text = section['sinhala'][:100] + "..."
            clean_text = ZWJHandler.clean_text_for_display(section['sinhala'])[:100] + "..."
            
            print(f"📄 Section {section['number']}:")
            print(f"   Original: {original_text}")
            print(f"   Cleaned:  {clean_text}")
            break

def example_web_app_usage():
    """
    Example: How to use in a web application
    """
    print("\n" + "=" * 60)
    print("Example: Web Application Usage")
    print("=" * 60)
    
    # Simulate a web app function
    def get_chapter_for_display(chapter_id):
        """Simulate getting chapter data for web display"""
        
        # In real app, this would query your database
        # For demo, we'll load from file
        chapter_files = {
            "an10.11": "Aṅguttaranikāyo/Dasakanipātapāḷi/chapters/an10.11-Samaṇasaññāvaggo.json"
        }
        
        if chapter_id not in chapter_files:
            return None
        
        file_path = Path(chapter_files[chapter_id])
        if not file_path.exists():
            return None
        
        # Load and clean in one step
        return ZWJHandler.get_display_ready_chapter(file_path)
    
    # Usage example
    chapter_data = get_chapter_for_display("an10.11")
    
    if chapter_data:
        print(f"✅ Chapter ready for display: {chapter_data['id']}")
        print(f"   All #zwj; placeholders converted to proper ZWJ characters")
        print(f"   Safe to render in web browser or mobile app")
        
        # Show statistics
        original_file = Path("Aṅguttaranikāyo/Dasakanipātapāḷi/chapters/an10.11-Samaṇasaññāvaggo.json")
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        zwj_count = original_content.count('#zwj;')
        print(f"   Processed {zwj_count} ZWJ placeholders")

def example_database_query_wrapper():
    """
    Example: Wrapper for database queries
    """
    print("\n" + "=" * 60)
    print("Example: Database Query Wrapper")
    print("=" * 60)
    
    def get_section_text_for_display(chapter_id, section_number, language='sinhala'):
        """
        Simulate getting section text from database with ZWJ cleaning
        """
        # In real app, this would be your database query
        # For demo, we'll simulate with file data
        
        chapter_file = Path("Aṅguttaranikāyo/Dasakanipātapāḷi/chapters/an10.11-Samaṇasaññāvaggo.json")
        
        if not chapter_file.exists():
            return None
        
        with open(chapter_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find the section
        for section in data.get('sections', []):
            if section.get('number') == section_number:
                text = section.get(language, '')
                # Clean for display
                return ZWJHandler.clean_text_for_display(text)
        
        return None
    
    # Usage example
    text = get_section_text_for_display("an10.11", 109, 'sinhala')
    
    if text:
        print(f"✅ Section text ready for display")
        print(f"   Length: {len(text)} characters")
        print(f"   Preview: {text[:150]}...")
        print(f"   All ZWJ placeholders cleaned automatically")

def main():
    """
    Run all examples
    """
    print("🎯 ZWJ Handler Usage Examples")
    print("This demonstrates the RECOMMENDED approach: display-time cleaning")
    
    example_api_endpoint()
    example_web_app_usage()
    example_database_query_wrapper()
    
    print("\n" + "=" * 60)
    print("💡 Key Benefits of Display-Time Cleaning:")
    print("=" * 60)
    print("✅ Safe - Original data remains unchanged")
    print("✅ Reversible - Can change approach anytime")
    print("✅ Flexible - Different cleaning rules for different contexts")
    print("✅ Testable - Easy to test rendering without permanent changes")
    print("✅ Maintainable - Centralized cleaning logic")
    
    print("\n🔧 Integration Tips:")
    print("   1. Add ZWJHandler to your application's text processing layer")
    print("   2. Clean text just before rendering/display")
    print("   3. Keep original data in database unchanged")
    print("   4. Test with different fonts and browsers")
    print("   5. Consider caching cleaned text if performance is critical")

if __name__ == "__main__":
    main()