"""
Verify that section 73 was properly merged and imported to the database
"""

import os
from dotenv import load_dotenv
from turso_python import TursoClient

load_dotenv()

# Connect to database
client = TursoClient(
    database_url=os.getenv("TURSO_DB_URL"),
    auth_token=os.getenv("TURSO_AUTH_TOKEN")
)

print("=" * 60)
print("Verifying Section 73 in Database")
print("=" * 60)

# Query section 73
result = client.execute_query("""
    SELECT section_number, 
           LENGTH(pali) as pali_length,
           LENGTH(english) as english_length,
           LENGTH(sinhala) as sinhala_length,
           vagga, vagga_english, vagga_sinhala
    FROM sections 
    WHERE chapter_id = 'sn.2.1' AND section_number = 73
""", [])

rows = result['results'][0]['response']['result']['rows']

if rows:
    row = rows[0]
    print(f"\n✓ Section 73 found in database:")
    print(f"  Section number: {row[0]['value']}")
    print(f"  Pali length: {row[1]['value']} chars")
    print(f"  English length: {row[2]['value']} chars")
    print(f"  Sinhala length: {row[3]['value']} chars")
    print(f"  Vagga: {row[4]['value']}")
    print(f"  Vagga English: {row[5]['value']}")
    print(f"  Vagga Sinhala: {row[6]['value']}")
    
    # Check if it contains content from all three original sections
    result2 = client.execute_query("""
        SELECT pali
        FROM sections 
        WHERE chapter_id = 'sn.2.1' AND section_number = 73
    """, [])
    
    pali_text = result2['results'][0]['response']['result']['rows'][0][0]['value']
    
    # Check for markers from each section
    has_section_1 = "satthā pariyesitabbo" in pali_text
    has_section_2 = "Saṅkhāre, bhikkhave" in pali_text
    has_section_3 = "sikkhā karaṇīyā" in pali_text
    
    print(f"\n✓ Content verification:")
    print(f"  Contains section 73 content: {'✓' if has_section_1 else '✗'}")
    print(f"  Contains section 73.1 content: {'✓' if has_section_2 else '✗'}")
    print(f"  Contains section 73.2 content: {'✓' if has_section_3 else '✗'}")
    
    if all([has_section_1, has_section_2, has_section_3]):
        print("\n✅ Section 73 successfully merged and imported!")
    else:
        print("\n⚠️  Some content may be missing")
else:
    print("\n❌ Section 73 not found in database")

# Check total sections for sn.2.1
result3 = client.execute_query("""
    SELECT COUNT(*) 
    FROM sections 
    WHERE chapter_id = 'sn.2.1'
""", [])

total = result3['results'][0]['response']['result']['rows'][0][0]['value']
print(f"\n📊 Total sections in sn.2.1: {total}")

print("=" * 60)
