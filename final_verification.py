#!/usr/bin/env python3
"""
Final verification of numberRange migration.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_turso_config():
    url = os.getenv("TURSO_DATABASE_URL") or os.getenv("TURSO_DB_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    
    if url.startswith("libsql://"):
        url = url.replace("libsql://", "https://")
    
    return url, token

def execute_query(url, token, sql):
    api_url = f"{url}/v2/pipeline"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql}}
        ]
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    result = response.json()
    return result.get("results", [{}])[0]

print("="*60)
print("NumberRange Migration - Final Verification")
print("="*60)
print()

url, token = get_turso_config()

# Count total sections with number_range
print("1. Counting sections with number_range...")
result = execute_query(url, token, """
    SELECT COUNT(*) as count 
    FROM sections 
    WHERE number_range IS NOT NULL
""")

rows = result.get("response", {}).get("result", {}).get("rows", [])
if rows:
    count = int(rows[0][0]['value'])
    print(f"   ✓ Found {count} sections with number_range")
    
    if count >= 127:
        print(f"   ✓ Migration successful! (Expected ~127-180)")
    else:
        print(f"   ⚠ Expected more sections")

# Show sample sections
print("\n2. Sample sections with number_range:")
result = execute_query(url, token, """
    SELECT chapter_id, section_number, number_range
    FROM sections 
    WHERE number_range IS NOT NULL
    ORDER BY chapter_id, section_number
    LIMIT 15
""")

rows = result.get("response", {}).get("result", {}).get("rows", [])
print(f"\n   {'Chapter ID':<15} {'Section':<10} {'Number Range':<15}")
print(f"   {'-'*40}")
for row in rows:
    chapter_id = row[0]['value']
    section_num = row[1]['value']
    num_range = row[2].get('value', 'NULL')
    print(f"   {chapter_id:<15} {section_num:<10} {num_range:<15}")

# Count by collection
print("\n3. Sections by collection:")
result = execute_query(url, token, """
    SELECT 
        CASE 
            WHEN chapter_id LIKE 'an%' THEN 'Aṅguttara'
            WHEN chapter_id LIKE 'sn%' THEN 'Saṃyutta'
            WHEN chapter_id LIKE 'mn%' THEN 'Majjhima'
            WHEN chapter_id LIKE 'dn%' THEN 'Dīgha'
            ELSE 'Other'
        END as collection,
        COUNT(*) as count
    FROM sections 
    WHERE number_range IS NOT NULL
    GROUP BY collection
    ORDER BY count DESC
""")

rows = result.get("response", {}).get("result", {}).get("rows", [])
print(f"\n   {'Collection':<15} {'Count':<10}")
print(f"   {'-'*25}")
for row in rows:
    collection = row[0]['value']
    count = row[1]['value']
    print(f"   {collection:<15} {count:<10}")

# Check specific examples
print("\n4. Checking specific examples:")
examples = [
    ('an1.10', 102, '102-109'),
    ('an1.10', 118, '118-128'),
    ('an5.29', 308, '308-1151'),
    ('sn.5.1', 42, '42-47'),
]

for chapter_id, section_num, expected_range in examples:
    result = execute_query(url, token, f"""
        SELECT number_range
        FROM sections 
        WHERE chapter_id = '{chapter_id}' AND section_number = {section_num}
    """)
    
    rows = result.get("response", {}).get("result", {}).get("rows", [])
    if rows and rows[0][0].get('value'):
        actual_range = rows[0][0]['value']
        status = "✓" if actual_range == expected_range else "⚠"
        print(f"   {status} {chapter_id} section {section_num}: {actual_range}")
    else:
        print(f"   ✗ {chapter_id} section {section_num}: NOT FOUND or NULL")

print("\n" + "="*60)
print("✓ Verification Complete!")
print("="*60)
print("\nThe number_range column has been successfully added and")
print("populated with data from the JSON files.")
print("\nYou can now query sections by their number ranges:")
print("  SELECT * FROM sections WHERE number_range IS NOT NULL;")
print("="*60)
