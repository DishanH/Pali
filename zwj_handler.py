#!/usr/bin/env python3
"""
ZWJ Handler - Utilities for handling #zwj placeholders in Sinhala text
"""

import json
import re
from pathlib import Path

class ZWJHandler:
    """
    Handler for ZWJ (Zero Width Joiner) placeholders in Sinhala text
    """
    
    @staticmethod
    def clean_text_for_display(text):
        """
        Clean text for display by replacing #zwj; with actual ZWJ character
        This is the RECOMMENDED approach - do replacement at display time
        
        Args:
            text (str): Text containing #zwj; placeholders
            
        Returns:
            str: Text with proper ZWJ characters
        """
        if not text:
            return text
        
        # Replace #zwj; with actual Zero Width Joiner (U+200D)
        cleaned_text = text.replace('#zwj;', '\u200D')
        
        return cleaned_text
    
    @staticmethod
    def clean_json_object_for_display(obj):
        """
        Recursively clean a JSON object for display
        
        Args:
            obj: JSON object (dict, list, or primitive)
            
        Returns:
            Cleaned object with ZWJ characters
        """
        if isinstance(obj, dict):
            return {k: ZWJHandler.clean_json_object_for_display(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ZWJHandler.clean_json_object_for_display(item) for item in obj]
        elif isinstance(obj, str):
            return ZWJHandler.clean_text_for_display(obj)
        else:
            return obj
    
    @staticmethod
    def get_display_ready_chapter(file_path):
        """
        Load a chapter JSON file and return it with cleaned ZWJ characters
        
        Args:
            file_path (str): Path to JSON file
            
        Returns:
            dict: Chapter data with cleaned text
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clean the entire object
            cleaned_data = ZWJHandler.clean_json_object_for_display(data)
            
            return cleaned_data
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    @staticmethod
    def preview_zwj_changes(text, max_examples=5):
        """
        Preview what changes would be made to text
        
        Args:
            text (str): Text to preview
            max_examples (int): Maximum number of examples to show
            
        Returns:
            list: List of (before, after) tuples
        """
        if not text or '#zwj;' not in text:
            return []
        
        # Find all #zwj patterns with context
        patterns = re.findall(r'\S*#zwj;\S*', text)
        
        examples = []
        seen = set()
        
        for pattern in patterns:
            if len(examples) >= max_examples:
                break
            
            if pattern not in seen:
                cleaned = pattern.replace('#zwj;', '\u200D')
                examples.append((pattern, cleaned))
                seen.add(pattern)
        
        return examples

def demonstrate_zwj_handling():
    """
    Demonstrate ZWJ handling with examples
    """
    print("=" * 70)
    print("ZWJ Handler Demonstration")
    print("=" * 70)
    
    # Example text with #zwj
    sample_text = "සත්#zwj;ත්වයෝ ධර්‍#zwj;මය භාග්‍ය#zwj;වතුන්"
    
    print(f"Original text: {sample_text}")
    print(f"Cleaned text:  {ZWJHandler.clean_text_for_display(sample_text)}")
    
    # Preview changes
    print(f"\nPreview of changes:")
    examples = ZWJHandler.preview_zwj_changes(sample_text)
    for i, (before, after) in enumerate(examples, 1):
        print(f"  {i}. '{before}' → '{after}'")
    
    # Test with a real file
    test_file = Path("Aṅguttaranikāyo/Dasakanipātapāḷi/chapters/an10.11-Samaṇasaññāvaggo.json")
    if test_file.exists():
        print(f"\nTesting with real file: {test_file.name}")
        
        # Load original
        with open(test_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Get cleaned version
        cleaned_data = ZWJHandler.get_display_ready_chapter(test_file)
        
        if cleaned_data:
            # Show example from first section with #zwj
            for section in original_data.get('sections', []):
                sinhala_text = section.get('sinhala', '')
                if '#zwj;' in sinhala_text:
                    print(f"\nExample from section {section.get('number', '?')}:")
                    
                    # Show first 100 characters
                    original_snippet = sinhala_text[:100] + "..." if len(sinhala_text) > 100 else sinhala_text
                    cleaned_snippet = ZWJHandler.clean_text_for_display(original_snippet)
                    
                    print(f"Original: {original_snippet}")
                    print(f"Cleaned:  {cleaned_snippet}")
                    break
    
    print(f"\n💡 Usage Recommendations:")
    print(f"   1. Use ZWJHandler.clean_text_for_display() when displaying text")
    print(f"   2. Use ZWJHandler.get_display_ready_chapter() for full chapters")
    print(f"   3. Keep original data unchanged in database/files")
    print(f"   4. Apply cleaning only at presentation layer")

if __name__ == "__main__":
    demonstrate_zwj_handling()