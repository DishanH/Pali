#!/usr/bin/env python3
"""
Analyze what Unicode issues remain in the database
"""

import os
import re
from dotenv import load_dotenv
from turso_python import TursoClient

# Load environment variables
load_dotenv()

def analyze_unicode_issues(client):
    """Analyze remaining Unicode issues"""
    
    print("🔍 Analyzing remaining Unicode issues...")
    
    # Get sections with issues
    result = client.execute_query("""
        SELECT chapter_id, section_number, sinhala
        FROM sections 
        WHERE sinhala LIKE '%#zwj;%' OR sinhala LIKE '%\\u%'
        LIMIT 10
    """)
    
    if not result.get('results'):
        print("✅ No Unicode issues found!")
        return
    
    rows = result['results'][0]['response']['result']['rows']
    
    print(f"📊 Found {len(rows)} sections with issues (showing first 10):")
    
    for i, row in enumerate(rows, 1):
        chapter_id = row[0]
        if isinstance(chapter_id, dict):
            chapter_id = chapter_id.get('value', '')
        section_num = row[1]
        if isinstance(section_num, dict):
            section_num = section_num.get('value', '')
        sinhala = row[2]
        if isinstance(sinhala, dict):
            sinhala = sinhala.get('value', '')
        
        print(f"\n{i}. {chapter_id} section {section_num}:")
        
        # Find specific issues
        if '#zwj;' in sinhala:
            count = sinhala.count('#zwj;')
            print(f"   ❌ {count} #zwj; placeholders")
        
        # Find Unicode escapes
        unicode_escapes = re.findall(r'\\u[0-9A-Fa-f]{4}', sinhala)
        if unicode_escapes:
            unique_escapes = set(unicode_escapes)
            print(f"   ❌ Unicode escapes: {unique_escapes}")
        
        # Find other patterns
        if '{U+' in sinhala:
            unicode_literals = re.findall(r'\{U\+[0-9A-Fa-f]+\}', sinhala)
            print(f"   ❌ Unicode literals: {set(unicode_literals)}")
        
        # Show sample text
        sample = sinhala[:200].replace('\n', ' ')
        print(f"   📝 Sample: {sample}...")

def main():
    """Analyze remaining Unicode issues"""
    
    print("=" * 60)
    print("ANALYZING REMAINING UNICODE ISSUES")
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
    
    analyze_unicode_issues(client)
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()