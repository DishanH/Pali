#!/usr/bin/env python3
"""
Apply Book Translations Script
Reads the translated book JSON files and applies them back to the original locations.
"""

import json
from pathlib import Path
import shutil

class BookTranslationApplier:
    def __init__(self):
        self.input_folder = Path("book_translations_for_manual_work")
        self.reference_file = self.input_folder / "file_reference.json"
        self.applied_count = 0
        self.error_count = 0
    
    def load_reference_mappings(self):
        """Load the file reference mappings"""
        if not self.reference_file.exists():
            print(f"❌ Reference file not found: {self.reference_file}")
            print("Please run extract_book_translations.py first")
            return None
        
        try:
            with open(self.reference_file, 'r', encoding='utf-8') as f:
                reference_data = json.load(f)
            
            mappings = reference_data.get('file_mappings', [])
            print(f"✓ Loaded {len(mappings)} file mappings")
            return mappings
            
        except Exception as e:
            print(f"❌ Error loading reference file: {e}")
            return None
    
    def has_translations(self, obj):
        """Check if an object has any non-empty translations"""
        if isinstance(obj, dict):
            # Check for non-empty English or Sinhala fields
            if obj.get('english', '').strip():
                return True
            if obj.get('sinhala', '').strip():
                return True
            
            # Check nested objects
            for value in obj.values():
                if self.has_translations(value):
                    return True
        
        elif isinstance(obj, list):
            for item in obj:
                if self.has_translations(item):
                    return True
        
        return False
    
    def apply_translation_file(self, mapping):
        """Apply translations from a single file"""
        output_path = Path(mapping['output_path'])
        original_path = Path(mapping['original_path'])
        
        if not output_path.exists():
            print(f"⚠️  Translated file not found: {output_path}")
            return False
        
        if not original_path.exists():
            print(f"⚠️  Original file not found: {original_path}")
            return False
        
        try:
            # Load the translated file
            with open(output_path, 'r', encoding='utf-8') as f:
                translated_data = json.load(f)
            
            # Check if it has any translations
            if not self.has_translations(translated_data):
                print(f"⚠️  No translations found in: {output_path.name}")
                return False
            
            # Create backup of original
            backup_path = original_path.with_suffix('.json.backup')
            shutil.copy2(original_path, backup_path)
            
            # Apply the translated data to original location
            with open(original_path, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Applied: {mapping['collection']}/{mapping['book']}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error applying {output_path.name}: {e}")
            self.error_count += 1
            return False
    
    def run(self):
        """Run the book translation application process"""
        print("=" * 60)
        print("Book Translation Applier")
        print("=" * 60)
        
        # Load reference mappings
        mappings = self.load_reference_mappings()
        if not mappings:
            return
        
        print(f"\n📝 Ready to apply translations from {len(mappings)} files")
        
        # Apply translations
        for mapping in mappings:
            if self.apply_translation_file(mapping):
                self.applied_count += 1
        
        print(f"\n✅ Book translation application complete!")
        print(f"📊 Results:")
        print(f"   - Files applied: {self.applied_count}")
        print(f"   - Errors: {self.error_count}")
        print(f"   - Total files: {len(mappings)}")
        
        if self.applied_count > 0:
            print(f"\n🎉 Success! Translations have been applied to the original book.json files.")
            print(f"   Backup files (.json.backup) have been created for safety.")
            print(f"   You can now run extract_missing_translations.py to verify.")


def main():
    applier = BookTranslationApplier()
    applier.run()


if __name__ == "__main__":
    main()