#!/usr/bin/env python3
"""
Script to verify that the binary data has been properly fixed in the database
"""

import os
import sys
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def verify_fixed_data():
    """
    Verify that the binary data has been properly fixed in the database
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
        
        # Check for binary data markers in the specific chapter
        chapter_id = "an2.2"
        print(f"\nChecking chapter {chapter_id} for binary data issues...")
        
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
        
        binary_issues_found = 0
        fixed_text_found = 0
        
        for row in rows:
            section_number = row[0]['value']
            sinhala_text = row[1]['value'] if row[1]['value'] else ""
            
            # Check for binary data markers
            if '<binary data, 1 bytes>' in sinhala_text:
                print(f"  ❌ Section {section_number}: Still contains binary data")
                binary_issues_found += 1
            elif 'ප්‍රතිසංඛ' in sinhala_text:
                print(f"  ✓ Section {section_number}: Contains properly fixed Sinhala text")
                fixed_text_found += 1
            else:
                print(f"  ℹ️  Section {section_number}: No specific markers found")
        
        print(f"\nVerification Results:")
        print(f"  Total sections checked: {len(rows)}")
        print(f"  Binary data issues found: {binary_issues_found}")
        print(f"  Properly fixed text found: {fixed_text_found}")
        
        if binary_issues_found == 0:
            print("\n✅ No binary data issues found in database!")
            if fixed_text_found > 0:
                print("✅ Fixed Sinhala text confirmed in database!")
            return True
        else:
            print(f"\n❌ {binary_issues_found} sections still have binary data issues")
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
    print("Verifying Fixed Data in Turso Database")
    print("=" * 60)
    
    if verify_fixed_data():
        print("\n🎉 Verification completed successfully!")
    else:
        print("\n❌ Verification found issues!")

if __name__ == "__main__":
    main()