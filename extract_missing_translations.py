#!/usr/bin/env python3
"""
Extract Missing Translations Script
Scans all Buddhist text collections and extracts missing translations for:
- Book titles, descriptions, footers
- Chapter titles, descriptions  
- Section titles (paliTitle, englishTitle, sinhalaTitle)
- Vagga titles within sections

Organizes output to maximize Google Translate free quota efficiency.
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import csv

class MissingTranslationExtractor:
    def __init__(self):
        self.missing_translations = {
            'english': defaultdict(list),  # pali -> [contexts where it appears]
            'sinhala': defaultdict(list)   # pali -> [contexts where it appears]
        }
        
        # Collections to scan
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
        
        self.stats = {
            'books_scanned': 0,
            'chapters_scanned': 0,
            'sections_scanned': 0,
            'missing_english': 0,
            'missing_sinhala': 0
        }
    
    def is_missing_or_empty(self, text):
        """Check if translation is missing or effectively empty"""
        if not text:
            return True
        if isinstance(text, str):
            text = text.strip()
            if not text or text == "" or text == "N/A" or text == "-":
                return True
        return False
    
    def add_missing_translation(self, pali_text, target_lang, context):
        """Add a missing translation to our collection"""
        if not pali_text or not pali_text.strip():
            return
            
        pali_clean = pali_text.strip()
        if pali_clean not in self.missing_translations[target_lang]:
            self.missing_translations[target_lang][pali_clean] = []
        
        # Add context if not already present
        if context not in self.missing_translations[target_lang][pali_clean]:
            self.missing_translations[target_lang][pali_clean].append(context)
    
    def scan_book_metadata(self, book_path, book_data):
        """Scan book.json for missing translations"""
        book_name = book_path.parent.name
        
        # Check book title
        title = book_data.get('title', {})
        if title.get('pali'):
            if self.is_missing_or_empty(title.get('english')):
                self.add_missing_translation(
                    title['pali'], 'english', 
                    f"Book Title: {book_name}"
                )
            if self.is_missing_or_empty(title.get('sinhala')):
                self.add_missing_translation(
                    title['pali'], 'sinhala', 
                    f"Book Title: {book_name}"
                )
        
        # Check vagga/nipata/pannasa names
        for subdivision_type in ['vagga', 'nipata', 'pannasa']:
            if subdivision_type in book_data:
                subdivision = book_data[subdivision_type]
                name = subdivision.get('name', {})
                if name.get('pali'):
                    if self.is_missing_or_empty(name.get('english')):
                        self.add_missing_translation(
                            name['pali'], 'english',
                            f"{subdivision_type.title()} Name: {book_name}"
                        )
                    if self.is_missing_or_empty(name.get('sinhala')):
                        self.add_missing_translation(
                            name['pali'], 'sinhala',
                            f"{subdivision_type.title()} Name: {book_name}"
                        )
        
        # Check description
        description = book_data.get('description', {})
        # Note: descriptions are usually only in English/Sinhala, not translated from Pali
        
        # Check footer
        footer = book_data.get('footer', {})
        if footer.get('pali'):
            if self.is_missing_or_empty(footer.get('english')):
                self.add_missing_translation(
                    footer['pali'], 'english',
                    f"Book Footer: {book_name}"
                )
            if self.is_missing_or_empty(footer.get('sinhala')):
                self.add_missing_translation(
                    footer['pali'], 'sinhala',
                    f"Book Footer: {book_name}"
                )
        
        # Check chapter metadata
        chapters = book_data.get('chapters', [])
        for chapter in chapters:
            chapter_id = chapter.get('id', 'unknown')
            
            # Chapter title
            title = chapter.get('title', {})
            if title.get('pali'):
                if self.is_missing_or_empty(title.get('english')):
                    self.add_missing_translation(
                        title['pali'], 'english',
                        f"Chapter Title: {book_name}/{chapter_id}"
                    )
                if self.is_missing_or_empty(title.get('sinhala')):
                    self.add_missing_translation(
                        title['pali'], 'sinhala',
                        f"Chapter Title: {book_name}/{chapter_id}"
                    )
    
    def scan_chapter_content(self, chapter_path, chapter_data):
        """Scan chapter content for missing translations"""
        chapter_id = chapter_data.get('id', chapter_path.stem)
        
        # Check chapter title
        title = chapter_data.get('title', {})
        if title.get('pali'):
            if self.is_missing_or_empty(title.get('english')):
                self.add_missing_translation(
                    title['pali'], 'english',
                    f"Chapter Content Title: {chapter_id}"
                )
            if self.is_missing_or_empty(title.get('sinhala')):
                self.add_missing_translation(
                    title['pali'], 'sinhala',
                    f"Chapter Content Title: {chapter_id}"
                )
        
        # Check sections
        sections = chapter_data.get('sections', [])
        for i, section in enumerate(sections):
            section_num = section.get('number', i + 1)
            context_base = f"{chapter_id}/Section {section_num}"
            
            # Check paliTitle
            if section.get('paliTitle'):
                pali_title = section['paliTitle'].strip()
                if pali_title:
                    if self.is_missing_or_empty(section.get('englishTitle')):
                        self.add_missing_translation(
                            pali_title, 'english',
                            f"Section Title: {context_base}"
                        )
                    if self.is_missing_or_empty(section.get('sinhalaTitle')):
                        self.add_missing_translation(
                            pali_title, 'sinhala',
                            f"Section Title: {context_base}"
                        )
            
            # Check vagga titles
            if section.get('vagga'):
                vagga_pali = section['vagga'].strip()
                if vagga_pali:
                    if self.is_missing_or_empty(section.get('vaggaEnglish')):
                        self.add_missing_translation(
                            vagga_pali, 'english',
                            f"Vagga Title: {context_base}"
                        )
                    if self.is_missing_or_empty(section.get('vaggaSinhala')):
                        self.add_missing_translation(
                            vagga_pali, 'sinhala',
                            f"Vagga Title: {context_base}"
                        )
    
    def scan_collection(self, collection_name):
        """Scan an entire collection for missing translations"""
        collection_path = Path(collection_name)
        
        if not collection_path.exists():
            print(f"⚠️  Collection not found: {collection_name}")
            return
        
        print(f"\n📚 Scanning {collection_name}...")
        
        # Get all book folders
        book_folders = [f for f in collection_path.iterdir() 
                       if f.is_dir() and f.name.lower() != "pdfs"]
        
        for book_folder in book_folders:
            book_json_path = book_folder / "book.json"
            
            if not book_json_path.exists():
                print(f"  ⚠️  No book.json in {book_folder.name}")
                continue
            
            try:
                # Scan book metadata
                with open(book_json_path, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)
                
                self.scan_book_metadata(book_json_path, book_data)
                self.stats['books_scanned'] += 1
                
                # Scan chapter content files
                chapters_folder = book_folder / "chapters"
                if chapters_folder.exists():
                    chapter_files = list(chapters_folder.glob("*.json"))
                    
                    for chapter_file in chapter_files:
                        try:
                            with open(chapter_file, 'r', encoding='utf-8') as f:
                                chapter_data = json.load(f)
                            
                            self.scan_chapter_content(chapter_file, chapter_data)
                            self.stats['chapters_scanned'] += 1
                            
                            # Count sections
                            sections = chapter_data.get('sections', [])
                            self.stats['sections_scanned'] += len(sections)
                            
                        except Exception as e:
                            print(f"    ❌ Error reading {chapter_file.name}: {e}")
                
                print(f"  ✓ {book_folder.name}")
                
            except Exception as e:
                print(f"  ❌ Error reading {book_json_path}: {e}")
    
    def generate_translation_files(self):
        """Generate organized files for translation"""
        
        # Count unique missing translations
        self.stats['missing_english'] = len(self.missing_translations['english'])
        self.stats['missing_sinhala'] = len(self.missing_translations['sinhala'])
        
        # Create output directory
        output_dir = Path("missing_translations")
        output_dir.mkdir(exist_ok=True)
        
        # Generate files for each language
        for lang in ['english', 'sinhala']:
            if not self.missing_translations[lang]:
                continue
                
            # Sort by frequency (most common first) and then alphabetically
            sorted_items = sorted(
                self.missing_translations[lang].items(),
                key=lambda x: (-len(x[1]), x[0])  # -count, then alphabetical
            )
            
            # Generate CSV for easy translation
            csv_file = output_dir / f"missing_{lang}_translations.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Pali Text', f'{lang.title()} Translation', 'Contexts', 'Usage Count'])
                
                for pali_text, contexts in sorted_items:
                    writer.writerow([
                        pali_text,
                        '',  # Empty column for translation
                        ' | '.join(contexts[:3]) + ('...' if len(contexts) > 3 else ''),
                        len(contexts)
                    ])
            
            # Generate JSON for programmatic use
            json_file = output_dir / f"missing_{lang}_translations.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'language': lang,
                    'total_missing': len(sorted_items),
                    'translations': {
                        pali: {
                            'contexts': contexts,
                            'usage_count': len(contexts),
                            'translation': ''
                        }
                        for pali, contexts in sorted_items
                    }
                }, f, ensure_ascii=False, indent=2)
            
            # Generate prioritized batches for Google Translate quota
            batch_size = 20  # Google's free daily limit
            batch_file = output_dir / f"missing_{lang}_batch_{batch_size}.txt"
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(f"# Missing {lang.title()} Translations - Prioritized Batch\n")
                f.write(f"# Total: {len(sorted_items)} items\n")
                f.write(f"# Batch size: {batch_size} (Google free daily limit)\n\n")
                
                for i, (pali_text, contexts) in enumerate(sorted_items[:batch_size]):
                    f.write(f"{i+1:2d}. {pali_text}\n")
                    f.write(f"    Contexts: {contexts[0]}")
                    if len(contexts) > 1:
                        f.write(f" (+{len(contexts)-1} more)")
                    f.write(f"\n    Translation: _______________\n\n")
        
        return output_dir
    
    def generate_summary_report(self, output_dir):
        """Generate a summary report"""
        report_file = output_dir / "translation_summary.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Missing Translations Summary\n\n")
            
            f.write("## Statistics\n")
            f.write(f"- **Books scanned**: {self.stats['books_scanned']}\n")
            f.write(f"- **Chapters scanned**: {self.stats['chapters_scanned']}\n")
            f.write(f"- **Sections scanned**: {self.stats['sections_scanned']}\n")
            f.write(f"- **Missing English translations**: {self.stats['missing_english']}\n")
            f.write(f"- **Missing Sinhala translations**: {self.stats['missing_sinhala']}\n\n")
            
            f.write("## Translation Strategy\n")
            f.write("Given Google Translate's free quota of 20 requests per day:\n\n")
            f.write("1. **Prioritized by frequency**: Most commonly used terms first\n")
            f.write("2. **Batch files created**: 20-item batches for daily translation\n")
            f.write("3. **Context provided**: Shows where each term is used\n")
            f.write("4. **Multiple formats**: CSV for manual editing, JSON for automation\n\n")
            
            f.write("## Files Generated\n")
            for file in output_dir.glob("*"):
                if file.is_file():
                    f.write(f"- `{file.name}`: {self.get_file_description(file.name)}\n")
            
            f.write("\n## Usage Instructions\n")
            f.write("1. Start with `missing_english_batch_20.txt` or `missing_sinhala_batch_20.txt`\n")
            f.write("2. Translate 20 items per day using Google Translate\n")
            f.write("3. Update the CSV files with translations\n")
            f.write("4. Use the update script (to be created) to apply translations back to source files\n")
    
    def get_file_description(self, filename):
        """Get description for generated files"""
        descriptions = {
            'missing_english_translations.csv': 'CSV file for manual English translation editing',
            'missing_sinhala_translations.csv': 'CSV file for manual Sinhala translation editing',
            'missing_english_translations.json': 'JSON file with English translation data',
            'missing_sinhala_translations.json': 'JSON file with Sinhala translation data',
            'missing_english_batch_20.txt': 'Daily batch of 20 English terms for Google Translate',
            'missing_sinhala_batch_20.txt': 'Daily batch of 20 Sinhala terms for Google Translate',
            'translation_summary.md': 'This summary report'
        }
        return descriptions.get(filename, 'Generated file')
    
    def run(self):
        """Run the complete extraction process"""
        print("=" * 60)
        print("Missing Translation Extractor")
        print("=" * 60)
        
        # Scan all collections
        for collection in self.collections:
            self.scan_collection(collection)
        
        # Generate output files
        print(f"\n📊 Generating translation files...")
        output_dir = self.generate_translation_files()
        
        # Generate summary
        self.generate_summary_report(output_dir)
        
        print(f"\n✅ Extraction complete!")
        print(f"📁 Output directory: {output_dir}")
        print(f"📈 Statistics:")
        print(f"   - Books scanned: {self.stats['books_scanned']}")
        print(f"   - Chapters scanned: {self.stats['chapters_scanned']}")
        print(f"   - Sections scanned: {self.stats['sections_scanned']}")
        print(f"   - Missing English: {self.stats['missing_english']}")
        print(f"   - Missing Sinhala: {self.stats['missing_sinhala']}")
        
        if self.stats['missing_english'] > 0 or self.stats['missing_sinhala'] > 0:
            print(f"\n💡 Next steps:")
            print(f"   1. Check {output_dir}/missing_*_batch_20.txt for daily translation batches")
            print(f"   2. Use Google Translate (20 free requests/day)")
            print(f"   3. Update CSV files with translations")
            print(f"   4. Run update script to apply translations back to source files")


def main():
    extractor = MissingTranslationExtractor()
    extractor.run()


if __name__ == "__main__":
    main()