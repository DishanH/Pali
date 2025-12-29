#!/usr/bin/env python3
"""
Bulk Translation JSON Creator
Creates a single JSON file with all missing translations for bulk processing.
If either English or Sinhala is missing, includes both for simplicity.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

class BulkTranslationCreator:
    def __init__(self):
        self.translations_needed = {}  # pali_text -> {contexts, needs_english, needs_sinhala}
        self.stats = {
            'books_scanned': 0,
            'chapters_scanned': 0,
            'sections_scanned': 0,
            'unique_terms': 0
        }
        
        # Collections to scan
        self.collections = [
            "Dīghanikāyo",
            "Majjhimanikāye", 
            "Saṃyuttanikāyo",
            "Aṅguttaranikāyo"
        ]
    
    def is_missing_or_empty(self, text):
        """Check if translation is missing or effectively empty"""
        if not text:
            return True
        if isinstance(text, str):
            text = text.strip()
            if not text or text == "" or text == "N/A" or text == "-":
                return True
        return False
    
    def add_translation_need(self, pali_text, context, needs_english=False, needs_sinhala=False):
        """Add a translation need"""
        if not pali_text or not pali_text.strip():
            return
            
        pali_clean = pali_text.strip()
        
        if pali_clean not in self.translations_needed:
            self.translations_needed[pali_clean] = {
                'contexts': [],
                'needs_english': False,
                'needs_sinhala': False
            }
        
        # Add context if not already present
        if context not in self.translations_needed[pali_clean]['contexts']:
            self.translations_needed[pali_clean]['contexts'].append(context)
        
        # Update needs
        if needs_english:
            self.translations_needed[pali_clean]['needs_english'] = True
        if needs_sinhala:
            self.translations_needed[pali_clean]['needs_sinhala'] = True
    
    def scan_book_metadata(self, book_path, book_data):
        """Scan book.json for missing translations"""
        book_name = book_path.parent.name
        
        # Check book title
        title = book_data.get('title', {})
        if title.get('pali'):
            needs_english = self.is_missing_or_empty(title.get('english'))
            needs_sinhala = self.is_missing_or_empty(title.get('sinhala'))
            
            if needs_english or needs_sinhala:
                self.add_translation_need(
                    title['pali'], 
                    f"Book Title: {book_name}",
                    needs_english, needs_sinhala
                )
        
        # Check vagga/nipata/pannasa names
        for subdivision_type in ['vagga', 'nipata', 'pannasa']:
            if subdivision_type in book_data:
                subdivision = book_data[subdivision_type]
                name = subdivision.get('name', {})
                if name.get('pali'):
                    needs_english = self.is_missing_or_empty(name.get('english'))
                    needs_sinhala = self.is_missing_or_empty(name.get('sinhala'))
                    
                    if needs_english or needs_sinhala:
                        self.add_translation_need(
                            name['pali'],
                            f"{subdivision_type.title()} Name: {book_name}",
                            needs_english, needs_sinhala
                        )
        
        # Check footer
        footer = book_data.get('footer', {})
        if footer.get('pali'):
            needs_english = self.is_missing_or_empty(footer.get('english'))
            needs_sinhala = self.is_missing_or_empty(footer.get('sinhala'))
            
            if needs_english or needs_sinhala:
                self.add_translation_need(
                    footer['pali'],
                    f"Book Footer: {book_name}",
                    needs_english, needs_sinhala
                )
        
        # Check chapter metadata
        chapters = book_data.get('chapters', [])
        for chapter in chapters:
            chapter_id = chapter.get('id', 'unknown')
            
            # Chapter title
            title = chapter.get('title', {})
            if title.get('pali'):
                needs_english = self.is_missing_or_empty(title.get('english'))
                needs_sinhala = self.is_missing_or_empty(title.get('sinhala'))
                
                if needs_english or needs_sinhala:
                    self.add_translation_need(
                        title['pali'],
                        f"Chapter Title: {book_name}/{chapter_id}",
                        needs_english, needs_sinhala
                    )
    
    def scan_chapter_content(self, chapter_path, chapter_data):
        """Scan chapter content for missing translations"""
        chapter_id = chapter_data.get('id', chapter_path.stem)
        
        # Check chapter title
        title = chapter_data.get('title', {})
        if title.get('pali'):
            needs_english = self.is_missing_or_empty(title.get('english'))
            needs_sinhala = self.is_missing_or_empty(title.get('sinhala'))
            
            if needs_english or needs_sinhala:
                self.add_translation_need(
                    title['pali'],
                    f"Chapter Content Title: {chapter_id}",
                    needs_english, needs_sinhala
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
                    needs_english = self.is_missing_or_empty(section.get('englishTitle'))
                    needs_sinhala = self.is_missing_or_empty(section.get('sinhalaTitle'))
                    
                    if needs_english or needs_sinhala:
                        self.add_translation_need(
                            pali_title,
                            f"Section Title: {context_base}",
                            needs_english, needs_sinhala
                        )
            
            # Check vagga titles
            if section.get('vagga'):
                vagga_pali = section['vagga'].strip()
                if vagga_pali:
                    needs_english = self.is_missing_or_empty(section.get('vaggaEnglish'))
                    needs_sinhala = self.is_missing_or_empty(section.get('vaggaSinhala'))
                    
                    if needs_english or needs_sinhala:
                        self.add_translation_need(
                            vagga_pali,
                            f"Vagga Title: {context_base}",
                            needs_english, needs_sinhala
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
    
    def create_bulk_translation_json(self):
        """Create the bulk translation JSON file"""
        
        # For simplicity: if either English or Sinhala is missing, include both
        final_translations = {}
        
        for pali_text, info in self.translations_needed.items():
            if info['needs_english'] or info['needs_sinhala']:
                final_translations[pali_text] = {
                    'pali': pali_text,
                    'english': '',  # Always include both for simplicity
                    'sinhala': '',  # Always include both for simplicity
                    'contexts': info['contexts'],
                    'usage_count': len(info['contexts']),
                    'originally_needed': {
                        'english': info['needs_english'],
                        'sinhala': info['needs_sinhala']
                    }
                }
        
        # Sort by usage count (most frequent first)
        sorted_translations = dict(sorted(
            final_translations.items(),
            key=lambda x: (-x[1]['usage_count'], x[0])
        ))
        
        self.stats['unique_terms'] = len(sorted_translations)
        
        # Create the bulk translation file
        bulk_data = {
            'metadata': {
                'created_date': '2025-12-29',
                'total_terms': len(sorted_translations),
                'instructions': {
                    'purpose': 'Bulk translation of Pali Buddhist terms',
                    'task': 'Fill in the "english" and "sinhala" fields for each term',
                    'context': 'Use the "contexts" field to understand where each term is used',
                    'note': 'Both English and Sinhala translations are requested for simplicity'
                },
                'statistics': self.stats
            },
            'translations': sorted_translations
        }
        
        # Save the bulk translation file
        output_file = Path("bulk_translations.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bulk_data, f, ensure_ascii=False, indent=2)
        
        # Also create a simplified version for easier external processing
        simple_data = []
        for pali_text, info in sorted_translations.items():
            simple_data.append({
                'pali': pali_text,
                'english': '',
                'sinhala': '',
                'usage_count': info['usage_count'],
                'sample_context': info['contexts'][0] if info['contexts'] else ''
            })
        
        simple_file = Path("bulk_translations_simple.json")
        with open(simple_file, 'w', encoding='utf-8') as f:
            json.dump(simple_data, f, ensure_ascii=False, indent=2)
        
        # Create a text file for easy copy-paste to external tools
        text_file = Path("bulk_translations.txt")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("# Pali Buddhist Terms for Translation\n")
            f.write(f"# Total: {len(sorted_translations)} terms\n")
            f.write("# Format: Pali Term | Usage Count | Sample Context\n\n")
            
            for pali_text, info in sorted_translations.items():
                f.write(f"{pali_text} | {info['usage_count']} uses | {info['contexts'][0]}\n")
        
        return output_file, simple_file, text_file
    
    def run(self):
        """Run the complete bulk translation creation process"""
        print("=" * 60)
        print("Bulk Translation JSON Creator")
        print("=" * 60)
        
        # Scan all collections
        for collection in self.collections:
            self.scan_collection(collection)
        
        # Create bulk translation files
        print(f"\n📊 Creating bulk translation files...")
        output_file, simple_file, text_file = self.create_bulk_translation_json()
        
        print(f"\n✅ Bulk translation files created!")
        print(f"📁 Files generated:")
        print(f"   - {output_file} (complete with metadata and contexts)")
        print(f"   - {simple_file} (simplified format)")
        print(f"   - {text_file} (plain text for copy-paste)")
        
        print(f"\n📈 Statistics:")
        print(f"   - Books scanned: {self.stats['books_scanned']}")
        print(f"   - Chapters scanned: {self.stats['chapters_scanned']}")
        print(f"   - Sections scanned: {self.stats['sections_scanned']}")
        print(f"   - Unique terms needing translation: {self.stats['unique_terms']}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Use {simple_file} or {text_file} with Perplexity/external tool")
        print(f"   2. Fill in English and Sinhala translations")
        print(f"   3. Save completed translations back to {output_file}")
        print(f"   4. Run apply_bulk_translations.py to update source files")


def main():
    creator = BulkTranslationCreator()
    creator.run()


if __name__ == "__main__":
    main()