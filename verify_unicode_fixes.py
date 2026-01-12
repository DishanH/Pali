#!/usr/bin/env python3
"""
Script to verify that Unicode escape sequences have been properly fixed
"""

import os
import sys
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def verify_unicode_fixes():
    """
    Verify that Unicode escape sequences have been properly fixed in the database
    """
    # Get database credentials
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Error: TURSO_DB_URL and TURSO_AUTH_TOKEN must be set in .env file")
        return False
    
    try:
        # Connect to database
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✓ Connected to Turso database")
        
        # Check for Unicode escape sequences in the specific chapter
        chapter_id = "an2.2"
        print(f"\nChecking chapter {chapter_id} for Unicode escape sequences...")
        
        # Query sections for this chapter
        result = client.execute_query("""
            SELECT section_number, sinhala 
            FROM sections 
            WHERE chapter_id = ? 
            ORDER BY section_number
        """, [chapter_id])
        
        if not result.get('results'):
            print("❌ No results found")
            return False
        
        rows = result['results'][0]['response']['result']['rows']
        
        unicode_issues_found = 0
        proper_unicode_found = 0
        
        for row in rows:
            section_number = row[0]['value']
            sinhala_text = row[1]['value'] if row[1]['value'] else ""
            
            # Check for Unicode escape sequences
            if '\\u0DCA' in sinhala_text or '\\u200D' in sinhala_text:
                print(f"  ❌ Section {section_number}: Still contains Unicode escapes")
                unicode_issues_found += 1
            elif 'ප්‍රතිසංඛ්‍යාන' in sinhala_text:
                print(f"  ✅ Section {section_number}: Contains proper Unicode characters")
                proper_unicode_found += 1
            else:
                print(f"  ℹ️  Section {section_number}: No specific Unicode markers found")
        
        print(f"\nUnicode Verification Results:")
        print(f"  Total sections checked: {len(rows)}")
        print(f"  Unicode escape issues found: {unicode_issues_found}")
        print(f"  Proper Unicode characters found: {proper_unicode_found}")
        
        if unicode_issues_found == 0:
            print("\n✅ No Unicode escape issues found in database!")
            if proper_unicode_found > 0:
                print("✅ Proper Unicode characters confirmed in database!")
            return True
        else:
            print(f"\n❌ {unicode_issues_found} sections still have Unicode escape issues")
            return False
        
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Main verification function
    """
    print("=" * 60)
    print("Verifying Unicode Fixes in Turso Database")
    print("=" * 60)
    
    if verify_unicode_fixes():
        print("\n🎉 Unicode verification completed successfully!")
    else:
        print("\n❌ Unicode verification found issues!")

if __name__ == "__main__":
    main()