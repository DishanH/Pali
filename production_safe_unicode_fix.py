#!/usr/bin/env python3
"""
PRODUCTION-SAFE COMPREHENSIVE UNICODE FIX
Fixes ALL Unicode issues with extensive safety measures
"""

import json
import re
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

class ProductionSafeUnicodeFixer:
    """
    Production-safe Unicode fixer with comprehensive safety measures
    """
    
    def __init__(self):
        self.backup_dir = Path(f"unicode_fix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.fixed_files = []
        self.failed_files = []
        self.total_fixes = 0
        
    def create_backup(self, file_path):
        """Create backup of original file"""
        try:
            # Convert to absolute paths to avoid relative path issues
            file_path = Path(file_path).resolve()
            backup_path = self.backup_dir / file_path.name  # Just use filename to avoid path issues
            
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file to backup
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"❌ Backup failed for {file_path}: {e}")
            return False
    
    def fix_unicode_issues(self, text):
        """
        Comprehensive Unicode fix function
        """
        if not text:
            return text, 0
        
        original_text = text
        fixes_applied = 0
        
        # 1. Fix #zwj; placeholders
        if '#zwj;' in text:
            old_count = text.count('#zwj;')
            text = text.replace('#zwj;', '\u200D')
            fixes_applied += old_count
        
        # 2. Fix &zwj; HTML entities
        if '&zwj;' in text:
            old_count = text.count('&zwj;')
            text = text.replace('&zwj;', '\u200D')
            fixes_applied += old_count
        
        # 3. Fix {U+XXXX} literal Unicode notation - handle each occurrence
        def replace_unicode_literal(match):
            nonlocal fixes_applied
            try:
                hex_code = match.group(1)
                char_code = int(hex_code, 16)
                fixes_applied += 1
                return chr(char_code)
            except:
                return match.group(0)  # Return original if conversion fails
        
        text = re.sub(r'\{U\+([0-9A-Fa-f]+)\}', replace_unicode_literal, text)
        
        # 4. Fix Unicode escape sequences
        unicode_escapes = {
            '\\u0DCA': '\u0DCA',  # Sinhala Al-lakuna
            '\\u200D': '\u200D',  # Zero Width Joiner
            '\\u200C': '\u200C',  # Zero Width Non-Joiner
            '\\u0D9A': '\u0D9A',  # Sinhala Ka
            '\\u0DBB': '\u0DBB',  # Sinhala Ra
            '\\u0DBA': '\u0DBA',  # Sinhala Ya
            '\\u0DB8': '\u0DB8',  # Sinhala Ma
            '\\u0D0F': '\u0D0F',  # Malayalam Ee (might be misplaced)
        }
        
        for escape, char in unicode_escapes.items():
            if escape in text:
                old_count = text.count(escape)
                text = text.replace(escape, char)
                fixes_applied += old_count
        
        # 5. Fix excessive ZWJ sequences (suspicious patterns) - do this AFTER other fixes
        # Replace multiple consecutive ZWJ with single ZWJ
        excessive_zwj = re.findall(r'\u200D{2,}', text)
        if excessive_zwj:
            fixes_applied += sum(len(match) - 1 for match in excessive_zwj)  # Count extra ZWJs removed
            text = re.sub(r'\u200D{2,}', '\u200D', text)
        
        # 6. Fix malformed Sinhala sequences
        # Remove isolated Al-lakuna not attached to consonants
        isolated_lakuna = re.findall(r'(?<![අ-ෆ])\u0DCA(?![අ-ෆ\u200D])', text)
        if isolated_lakuna:
            fixes_applied += len(isolated_lakuna)
            text = re.sub(r'(?<![අ-ෆ])\u0DCA(?![අ-ෆ\u200D])', '', text)
        
        # 7. Clean up excessive combining marks
        excessive_marks = re.findall(r'[\u0DCA\u200D]{3,}', text)
        if excessive_marks:
            fixes_applied += sum(len(match) - 2 for match in excessive_marks)  # Count extras removed
            text = re.sub(r'[\u0DCA\u200D]{3,}', '\u0DCA\u200D', text)
        
        return text, fixes_applied
    
    def fix_json_file(self, file_path, dry_run=True):
        """
        Fix Unicode issues in a JSON file with safety checks
        """
        try:
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                data = json.loads(original_content)
            
            # Check if file needs fixing
            total_fixes_needed = 0
            
            # Quick check for issues
            if any(marker in original_content for marker in ['#zwj;', '\\u0DCA', '{U+', '&zwj;']):
                # Count potential fixes
                total_fixes_needed += original_content.count('#zwj;')
                total_fixes_needed += original_content.count('&zwj;')
                total_fixes_needed += len(re.findall(r'\{U\+[0-9A-Fa-f]+\}', original_content))
                total_fixes_needed += len(re.findall(r'\\u[0-9A-Fa-f]{4}', original_content))
            
            if total_fixes_needed == 0:
                return True, "No issues found", 0
            
            if dry_run:
                return True, f"Would fix {total_fixes_needed} issues", total_fixes_needed
            
            # Create backup before fixing
            if not self.create_backup(file_path):
                return False, "Backup failed", 0
            
            # Recursively fix all strings in JSON
            def fix_recursive(obj):
                if isinstance(obj, dict):
                    return {k: fix_recursive(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [fix_recursive(item) for item in obj]
                elif isinstance(obj, str):
                    fixed_text, fixes = self.fix_unicode_issues(obj)
                    return fixed_text
                else:
                    return obj
            
            # Apply fixes
            fixed_data = fix_recursive(data)
            
            # Count actual fixes applied
            fixed_content = json.dumps(fixed_data, ensure_ascii=False, indent=2)
            actual_fixes = 0
            
            # Count what was actually fixed
            for marker in ['#zwj;', '&zwj;']:
                actual_fixes += original_content.count(marker) - fixed_content.count(marker)
            
            # Write fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, ensure_ascii=False, indent=2)
            
            return True, f"Fixed {actual_fixes} issues", actual_fixes
            
        except Exception as e:
            return False, f"Error: {e}", 0
    
    def update_database_chapter(self, file_path, client):
        """
        Update a chapter in the database with fixed content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            chapter_id = chapter_data['id']
            
            # Update chapter metadata
            client.execute_query("""
                UPDATE chapters 
                SET title_pali = ?, title_english = ?, title_sinhala = ?
                WHERE id = ?
            """, [
                chapter_data['title']['pali'],
                chapter_data['title']['english'], 
                chapter_data['title']['sinhala'],
                chapter_id
            ])
            
            # Update sections
            sections_updated = 0
            for section in chapter_data['sections']:
                section_number = section['number']
                
                client.execute_query("""
                    UPDATE sections 
                    SET pali = ?, english = ?, sinhala = ?, pali_title = ?
                    WHERE chapter_id = ? AND section_number = ?
                """, [
                    section['pali'],
                    section['english'],
                    section['sinhala'],
                    section.get('paliTitle', ''),
                    chapter_id,
                    section_number
                ])
                sections_updated += 1
            
            return True, f"Updated {sections_updated} sections"
            
        except Exception as e:
            return False, f"Database error: {e}"
    
    def run_comprehensive_fix(self, dry_run=True, update_database=False):
        """
        Run comprehensive Unicode fix with all safety measures
        """
        print("=" * 80)
        print("PRODUCTION-SAFE COMPREHENSIVE UNICODE FIX")
        print("=" * 80)
        
        if not dry_run:
            print("⚠️  WARNING: This will make PERMANENT changes!")
            print("⚠️  Ensure you have database backups!")
        
        # Find all JSON files
        json_files = []
        for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
            dir_path = Path(directory)
            if dir_path.exists():
                json_files.extend(dir_path.rglob("*.json"))
        
        if not json_files:
            print("❌ No JSON files found")
            return False
        
        print(f"📁 Found {len(json_files)} JSON files to process")
        
        # Create backup directory if not dry run
        if not dry_run:
            self.backup_dir.mkdir(exist_ok=True)
            print(f"📦 Backup directory: {self.backup_dir}")
        
        # Process files
        files_to_fix = []
        total_issues = 0
        
        print(f"\n🔍 {'Analyzing' if dry_run else 'Processing'} files...")
        
        for i, json_file in enumerate(json_files, 1):
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(json_files)} files...")
            
            success, message, fix_count = self.fix_json_file(json_file, dry_run)
            
            if fix_count > 0:
                files_to_fix.append((json_file, fix_count))
                total_issues += fix_count
                
                if not dry_run:
                    if success:
                        self.fixed_files.append(json_file)
                        self.total_fixes += fix_count
                        print(f"  ✅ {json_file.name}: {message}")
                    else:
                        self.failed_files.append((json_file, message))
                        print(f"  ❌ {json_file.name}: {message}")
        
        # Report results
        print(f"\n📊 RESULTS:")
        print(f"   Files needing fixes: {len(files_to_fix)}")
        print(f"   Total issues found: {total_issues}")
        
        if dry_run:
            print(f"\n🔍 DRY RUN COMPLETE - No changes made")
            print(f"\n📋 Top 10 files needing fixes:")
            sorted_files = sorted(files_to_fix, key=lambda x: x[1], reverse=True)
            for i, (file_path, count) in enumerate(sorted_files[:10], 1):
                print(f"   {i}. {file_path.name}: {count} issues")
            
            return True
        
        # Real run results
        print(f"\n✅ FILES FIXED: {len(self.fixed_files)}")
        print(f"❌ FILES FAILED: {len(self.failed_files)}")
        print(f"🔧 TOTAL FIXES APPLIED: {self.total_fixes}")
        
        if self.failed_files:
            print(f"\n❌ Failed files:")
            for file_path, error in self.failed_files:
                print(f"   - {file_path.name}: {error}")
        
        # Update database if requested
        if update_database and self.fixed_files:
            print(f"\n🗄️  UPDATING DATABASE...")
            
            db_url = os.getenv("TURSO_DB_URL", "")
            auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
            
            if not db_url or not auth_token:
                print("⚠️  Database credentials not found. Skipping database update.")
                return True
            
            try:
                client = TursoClient(database_url=db_url, auth_token=auth_token)
                print("✅ Connected to database")
                
                db_updated = 0
                db_failed = 0
                
                for file_path in self.fixed_files:
                    # Only update chapter files
                    if 'chapters' in str(file_path) and file_path.name != 'book.json':
                        success, message = self.update_database_chapter(file_path, client)
                        if success:
                            print(f"  ✅ DB: {file_path.name} - {message}")
                            db_updated += 1
                        else:
                            print(f"  ❌ DB: {file_path.name} - {message}")
                            db_failed += 1
                
                print(f"\n📊 DATABASE UPDATE RESULTS:")
                print(f"   Chapters updated: {db_updated}")
                print(f"   Updates failed: {db_failed}")
                
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
        
        print(f"\n🎉 COMPREHENSIVE FIX COMPLETED!")
        print(f"📦 Backups saved in: {self.backup_dir}")
        
        return True

def main():
    """
    Main function with user interaction for production safety
    """
    fixer = ProductionSafeUnicodeFixer()
    
    print("🚨 PRODUCTION DATABASE UNICODE FIX")
    print("This script will fix ALL Unicode issues found in the analysis.")
    print("\nIssues to be fixed:")
    print("  1. #zwj; → actual ZWJ character")
    print("  2. &zwj; → actual ZWJ character") 
    print("  3. {U+200D} → actual ZWJ character")
    print("  4. \\uXXXX escapes → actual characters")
    print("  5. Malformed Sinhala sequences")
    print("  6. Excessive combining marks")
    
    # Step 1: Dry run
    print(f"\n" + "="*50)
    print("STEP 1: DRY RUN ANALYSIS")
    print("="*50)
    
    if not fixer.run_comprehensive_fix(dry_run=True):
        print("❌ Dry run failed!")
        return
    
    # Step 2: Confirm fixes
    print(f"\n" + "="*50)
    print("STEP 2: CONFIRM FIXES")
    print("="*50)
    
    response = input("\nProceed with fixing files? (yes/no): ").lower().strip()
    if response != 'yes':
        print("❌ Operation cancelled.")
        return
    
    # Step 3: Fix files
    print(f"\n" + "="*50)
    print("STEP 3: FIXING FILES")
    print("="*50)
    
    if not fixer.run_comprehensive_fix(dry_run=False, update_database=False):
        print("❌ File fixing failed!")
        return
    
    # Step 4: Confirm database update
    print(f"\n" + "="*50)
    print("STEP 4: DATABASE UPDATE")
    print("="*50)
    
    db_response = input("\nUpdate production database? (yes/no): ").lower().strip()
    if db_response == 'yes':
        print("🗄️  Updating database...")
        
        # Re-run with database update
        if not fixer.run_comprehensive_fix(dry_run=False, update_database=True):
            print("❌ Database update failed!")
            return
    
    print(f"\n🎉 ALL OPERATIONS COMPLETED SUCCESSFULLY!")
    print(f"📦 File backups: {fixer.backup_dir}")
    print(f"🔧 Total fixes: {fixer.total_fixes}")

if __name__ == "__main__":
    main()