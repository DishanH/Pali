#!/usr/bin/env python3
"""
Check what sections actually exist in the database.
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

url, token = get_turso_config()

# Check a specific section
print("Checking an1.10 section 102...")
result = execute_query(url, token, """
    SELECT id, chapter_id, section_number, number_range, 
           SUBSTR(pali, 1, 50) as pali_preview
    FROM sections 
    WHERE chapter_id = 'an1.10' AND section_number = 102
""")

rows = result.get("response", {}).get("result", {}).get("rows", [])
if rows:
    print("✓ Section found in database:")
    for row in rows:
        print(f"  ID: {row[0]['value']}")
        print(f"  Chapter: {row[1]['value']}")
        print(f"  Section: {row[2]['value']}")
        print(f"  Number Range: {row[3]['value'] if row[3]['value'] else 'NULL'}")
        print(f"  Pali: {row[4]['value']}...")
else:
    print("✗ Section NOT found in database")

print("\n" + "="*60)
print("Checking all an1.10 sections...")
result = execute_query(url, token, """
    SELECT section_number, number_range
    FROM sections 
    WHERE chapter_id = 'an1.10'
    ORDER BY section_number
""")

rows = result.get("response", {}).get("result", {}).get("rows", [])
print(f"Found {len(rows)} sections in an1.10:")
for row in rows:
    section_num = row[0]['value']
    num_range = row[1].get('value') if row[1] else None
    num_range_str = num_range if num_range else 'NULL'
    print(f"  Section {section_num}: {num_range_str}")
