"""
Fix section 73 to add titles from 73.1 and 73.2 into the content, not the title fields
"""

import json
from pathlib import Path

# Path to the file
file_path = Path("Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json")

# Read the file
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find section 73
section_73 = None
section_73_idx = None

for idx, section in enumerate(data["sections"]):
    if section["number"] == 73:
        section_73 = section
        section_73_idx = idx
        break

if not section_73:
    print("❌ Could not find section 73")
    exit(1)

print("Current structure:")
print(f"  Title (paliTitle): {section_73.get('paliTitle', 'N/A')}")
print(f"  Content length: Pali={len(section_73['pali'])}, English={len(section_73['english'])}, Sinhala={len(section_73['sinhala'])}")

# The titles from 73.1 and 73.2 that should be added to content
title_73_1 = {
    "pali": "Dutiyasatthusuttādidasakaṃ",
    "english": "Second Group of Ten Beginning with the Teacher",
    "sinhala": "දුතිය සත්ථු සූත්‍රාදි දසකය"
}

title_73_2 = {
    "pali": "Sikkhāsuttādipeyyālaekādasakaṃ",
    "english": "The Eleven Repetitions Beginning with the Discourse on Training",
    "sinhala": "සික්ඛාසූත්තාදිපෙය්‍යාල ඒකාදසකය"
}

# Split the current content by double newlines (sections are separated by \n\n)
pali_parts = section_73["pali"].split("\n\n")
english_parts = section_73["english"].split("\n\n")
sinhala_parts = section_73["sinhala"].split("\n\n")

# Reconstruct with titles before 73.1 and 73.2 content
# Part 0 is section 73, Part 1 is section 73.1, Part 2 is section 73.2
new_pali = pali_parts[0]
if len(pali_parts) > 1:
    new_pali += f"\n\n{title_73_1['pali']}\n\n{pali_parts[1]}"
if len(pali_parts) > 2:
    new_pali += f"\n\n{title_73_2['pali']}\n\n{pali_parts[2]}"

new_english = english_parts[0]
if len(english_parts) > 1:
    new_english += f"\n\n{title_73_1['english']}\n\n{english_parts[1]}"
if len(english_parts) > 2:
    new_english += f"\n\n{title_73_2['english']}\n\n{english_parts[2]}"

new_sinhala = sinhala_parts[0]
if len(sinhala_parts) > 1:
    new_sinhala += f"\n\n{title_73_1['sinhala']}\n\n{sinhala_parts[1]}"
if len(sinhala_parts) > 2:
    new_sinhala += f"\n\n{title_73_2['sinhala']}\n\n{sinhala_parts[2]}"

# Restore the original title (just section 73's title)
section_73["paliTitle"] = "Satthusuttaṃ"
section_73["englishTitle"] = "The Discourse on the Teacher"
section_73["sinhalaTitle"] = "සත්ථු සූත්‍රය"

# Update the content
section_73["pali"] = new_pali
section_73["english"] = new_english
section_73["sinhala"] = new_sinhala

# Update the section in the data
data["sections"][section_73_idx] = section_73

print("\n✓ Updated structure:")
print(f"  Title (paliTitle): {section_73['paliTitle']}")
print(f"  Content now includes titles from 73.1 and 73.2")
print(f"  New content length: Pali={len(new_pali)}, English={len(new_english)}, Sinhala={len(new_sinhala)}")

# Save the file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ File updated: {file_path}")
print("\nNow updating database...")

# Now update the database
import os
from dotenv import load_dotenv
from turso_python import TursoClient

load_dotenv()

client = TursoClient(
    database_url=os.getenv("TURSO_DB_URL"),
    auth_token=os.getenv("TURSO_AUTH_TOKEN")
)

# Update section 73 in the database
client.execute_query("""
    UPDATE sections 
    SET pali = ?,
        english = ?,
        sinhala = ?,
        pali_title = ?,
        english_title = ?,
        sinhala_title = ?
    WHERE chapter_id = 'sn.2.1' AND section_number = 73
""", [
    section_73["pali"],
    section_73["english"],
    section_73["sinhala"],
    section_73["paliTitle"],
    section_73["englishTitle"],
    section_73["sinhalaTitle"]
])

print("✅ Database updated!")

# Verify
result = client.execute_query("""
    SELECT pali_title, english_title, sinhala_title,
           LENGTH(pali) as pali_len,
           LENGTH(english) as english_len,
           LENGTH(sinhala) as sinhala_len
    FROM sections 
    WHERE chapter_id = 'sn.2.1' AND section_number = 73
""", [])

rows = result['results'][0]['response']['result']['rows']
if rows:
    row = rows[0]
    print("\n📋 Verification from database:")
    print(f"  Pali Title: {row[0]['value']}")
    print(f"  English Title: {row[1]['value']}")
    print(f"  Sinhala Title: {row[2]['value']}")
    print(f"  Content lengths: Pali={row[3]['value']}, English={row[4]['value']}, Sinhala={row[5]['value']}")
    
    # Check if titles are in content
    result2 = client.execute_query("""
        SELECT pali, english, sinhala
        FROM sections 
        WHERE chapter_id = 'sn.2.1' AND section_number = 73
    """, [])
    
    content = result2['results'][0]['response']['result']['rows'][0]
    pali_content = content[0]['value']
    english_content = content[1]['value']
    sinhala_content = content[2]['value']
    
    has_title_1_pali = "Dutiyasatthusuttādidasakaṃ" in pali_content
    has_title_2_pali = "Sikkhāsuttādipeyyālaekādasakaṃ" in pali_content
    has_title_1_english = "Second Group of Ten Beginning with the Teacher" in english_content
    has_title_2_english = "The Eleven Repetitions Beginning with the Discourse on Training" in english_content
    
    print(f"\n  ✓ Content includes 73.1 title: {'✓' if has_title_1_pali and has_title_1_english else '✗'}")
    print(f"  ✓ Content includes 73.2 title: {'✓' if has_title_2_pali and has_title_2_english else '✗'}")
    
    if all([has_title_1_pali, has_title_2_pali, has_title_1_english, has_title_2_english]):
        print("\n✅ All titles successfully added to content!")
    else:
        print("\n⚠️  Some titles may be missing from content")
