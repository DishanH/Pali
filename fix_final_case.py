#!/usr/bin/env python3
"""
Fix the final remaining Unicode case
"""

import os
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def main():
    """Fix the final case"""
    
    print("=" * 60)
    print("FIXING FINAL UNICODE CASE")
    print("=" * 60)
    
    # Get database connection
    db_url = os.getenv("TURSO_DB_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")
    
    if not db_url or not auth_token:
        print("❌ Database credentials not found")
        return
    
    try:
        client = TursoClient(database_url=db_url, auth_token=auth_token)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Fix the specific case
    print("🔧 Fixing #ZWJ; (uppercase) patterns...")
    
    # Get the problematic section
    result = client.execute_query("""
        SELECT chapter_id, section_number, sinhala
        FROM sections 
        WHERE chapter_id = 'sn.1.4' AND section_number = 150
    """)
    
    if result.get('results'):
        rows = result['results'][0]['response']['result']['rows']
        if rows:
            chapter_id = rows[0][0]
            if isinstance(chapter_id, dict):
                chapter_id = chapter_id.get('value', '')
            section_num = rows[0][1]
            if isinstance(section_num, dict):
                section_num = section_num.get('value', '')
            sinhala = rows[0][2]
            if isinstance(sinhala, dict):
                sinhala = sinhala.get('value', '')
            
            print(f"📝 Found section {chapter_id} {section_num}")
            
            # Fix #ZWJ; (uppercase)
            if '#ZWJ;' in sinhala:
                count = sinhala.count('#ZWJ;')
                fixed_text = sinhala.replace('#ZWJ;', '\u200D')
                
                # Update database
                client.execute_query("""
                    UPDATE sections 
                    SET sinhala = ?
                    WHERE chapter_id = ? AND section_number = ?
                """, [fixed_text, chapter_id, section_num])
                
                print(f"✅ Fixed {count} #ZWJ; patterns")
            else:
                print("ℹ️  No #ZWJ; patterns found")
    
    # Final verification
    print(f"\n🔍 Final verification...")
    
    result = client.execute_query("""
        SELECT COUNT(*) as count
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%' 
           OR sinhala LIKE '%#ZWJ;%'
           OR sinhala LIKE '%&zwj;%'
           OR sinhala LIKE '%\\u%'
           OR sinhala LIKE '%{U+%'
    """)
    
    if result.get('results'):
        count = result['results'][0]['response']['result']['rows'][0][0]
        if isinstance(count, dict):
            count = count.get('value', 0)
        
        if count == 0:
            print(f"🎉 ALL Unicode issues have been completely fixed!")
        else:
            print(f"⚠️  {count} sections still have Unicode issues")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()