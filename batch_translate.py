#!/usr/bin/env python3
"""
Batch Translation Script
Uses Google Translate API to translate missing terms efficiently.
Handles rate limiting and batch processing to maximize free quota usage.
"""

import json
import csv
import time
import os
from pathlib import Path
from googletrans import Translator
import argparse

class BatchTranslator:
    def __init__(self):
        self.translator = Translator()
        self.translations_applied = 0
        self.errors = 0
        
        # Language mappings
        self.lang_codes = {
            'english': 'en',
            'sinhala': 'si'
        }
    
    def translate_text(self, text, target_lang, source_lang='auto'):
        """Translate a single text with error handling"""
        try:
            # Clean the text
            text = text.strip()
            if not text:
                return None
            
            # Translate
            result = self.translator.translate(text, dest=target_lang, src=source_lang)
            return result.text
            
        except Exception as e:
            print(f"❌ Translation error for '{text}': {e}")
            self.errors += 1
            return None
    
    def translate_batch_from_csv(self, csv_file, language, batch_size=20, start_row=0):
        """Translate a batch of terms from CSV file"""
        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        target_lang = self.lang_codes.get(language)
        if not target_lang:
            print(f"❌ Unsupported language: {language}")
            return
        
        print(f"\n🔄 Translating batch from {csv_file.name}")
        print(f"   Language: {language} ({target_lang})")
        print(f"   Batch size: {batch_size}")
        print(f"   Starting from row: {start_row}")
        
        # Read CSV
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if start_row >= len(rows):
            print(f"❌ Start row {start_row} exceeds total rows {len(rows)}")
            return
        
        # Process batch
        end_row = min(start_row + batch_size, len(rows))
        batch_rows = rows[start_row:end_row]
        
        print(f"📝 Processing rows {start_row+1} to {end_row} of {len(rows)}")
        
        updated_rows = []
        for i, row in enumerate(batch_rows):
            pali_text = row['Pali Text'].strip()
            current_translation = row[f'{language.title()} Translation'].strip()
            
            # Skip if already translated
            if current_translation:
                print(f"  {start_row + i + 1:2d}. ✓ Already translated: {pali_text}")
                updated_rows.append(row)
                continue
            
            # Translate
            print(f"  {start_row + i + 1:2d}. Translating: {pali_text}")
            translation = self.translate_text(pali_text, target_lang, 'pi')  # 'pi' for Pali
            
            if translation:
                row[f'{language.title()} Translation'] = translation
                print(f"      → {translation}")
                self.translations_applied += 1
            else:
                print(f"      → Failed to translate")
            
            updated_rows.append(row)
            
            # Rate limiting - small delay between requests
            if i < len(batch_rows) - 1:  # Don't delay after last item
                time.sleep(0.1)  # 100ms delay
        
        # Update the original rows
        for i, updated_row in enumerate(updated_rows):
            rows[start_row + i] = updated_row
        
        # Write back to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if rows:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"✅ Batch complete: {self.translations_applied} translations applied")
    
    def translate_interactive(self, csv_file, language):
        """Interactive translation mode"""
        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        target_lang = self.lang_codes.get(language)
        if not target_lang:
            print(f"❌ Unsupported language: {language}")
            return
        
        # Read CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"\n🎯 Interactive Translation Mode")
        print(f"   File: {csv_file.name}")
        print(f"   Language: {language}")
        print(f"   Total terms: {len(rows)}")
        print(f"   Commands: 'q' to quit, 's' to skip, 'a' for auto-translate")
        
        updated = False
        for i, row in enumerate(rows):
            pali_text = row['Pali Text'].strip()
            current_translation = row[f'{language.title()} Translation'].strip()
            contexts = row['Contexts']
            
            # Skip if already translated
            if current_translation:
                continue
            
            print(f"\n📝 Term {i+1}/{len(rows)}: {pali_text}")
            print(f"   Contexts: {contexts}")
            
            # Get auto-translation suggestion
            auto_translation = self.translate_text(pali_text, target_lang, 'pi')
            if auto_translation:
                print(f"   Suggested: {auto_translation}")
            
            # Get user input
            user_input = input("   Translation (or 'a' for auto, 's' to skip, 'q' to quit): ").strip()
            
            if user_input.lower() == 'q':
                break
            elif user_input.lower() == 's':
                continue
            elif user_input.lower() == 'a' and auto_translation:
                row[f'{language.title()} Translation'] = auto_translation
                print(f"   ✓ Applied auto-translation: {auto_translation}")
                updated = True
                self.translations_applied += 1
            elif user_input:
                row[f'{language.title()} Translation'] = user_input
                print(f"   ✓ Applied manual translation: {user_input}")
                updated = True
                self.translations_applied += 1
        
        # Save if updated
        if updated:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if rows:
                    fieldnames = rows[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            print(f"\n✅ Saved {self.translations_applied} translations to {csv_file.name}")
    
    def show_progress(self, csv_file, language):
        """Show translation progress"""
        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        total = len(rows)
        translated = sum(1 for row in rows if row[f'{language.title()} Translation'].strip())
        remaining = total - translated
        progress = (translated / total * 100) if total > 0 else 0
        
        print(f"\n📊 Translation Progress for {language.title()}")
        print(f"   File: {csv_file.name}")
        print(f"   Total terms: {total}")
        print(f"   Translated: {translated}")
        print(f"   Remaining: {remaining}")
        print(f"   Progress: {progress:.1f}%")
        
        if remaining > 0:
            days_at_20_per_day = (remaining + 19) // 20  # Round up
            print(f"   Days needed (20/day): {days_at_20_per_day}")


def main():
    parser = argparse.ArgumentParser(description='Batch translate missing terms')
    parser.add_argument('language', choices=['english', 'sinhala'], 
                       help='Target language for translation')
    parser.add_argument('--mode', choices=['batch', 'interactive', 'progress'], 
                       default='batch', help='Translation mode')
    parser.add_argument('--batch-size', type=int, default=20, 
                       help='Number of terms to translate in batch mode')
    parser.add_argument('--start-row', type=int, default=0, 
                       help='Starting row for batch mode (0-based)')
    parser.add_argument('--translation-dir', default='missing_translations',
                       help='Directory containing translation files')
    
    args = parser.parse_args()
    
    # Check translation directory
    translation_path = Path(args.translation_dir)
    if not translation_path.exists():
        print(f"❌ Translation directory not found: {args.translation_dir}")
        print("Please run extract_missing_translations.py first")
        return
    
    # Get CSV file
    csv_file = translation_path / f"missing_{args.language}_translations.csv"
    
    # Initialize translator
    translator = BatchTranslator()
    
    print("=" * 60)
    print("Batch Translator")
    print("=" * 60)
    
    if args.mode == 'progress':
        translator.show_progress(csv_file, args.language)
    elif args.mode == 'interactive':
        translator.translate_interactive(csv_file, args.language)
    else:  # batch mode
        translator.translate_batch_from_csv(
            csv_file, args.language, args.batch_size, args.start_row
        )
    
    if translator.errors > 0:
        print(f"\n⚠️  {translator.errors} translation errors occurred")


if __name__ == "__main__":
    main()