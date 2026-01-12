"""
Update section 73 to include all three titles from the merged sections
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

print("Current titles:")
print(f"  Pali: {section_73.get('paliTitle', 'N/A')}")
print(f"  English: {section_73.get('englishTitle', 'N/A')}")
print(f"  Sinhala: {section_73.get('sinhalaTitle', 'N/A')}")

# The three titles that should be included
titles = {
    "pali": [
        "Satthusuttaṃ",
        "Dutiyasatthusuttādidasakaṃ",
        "Sikkhāsuttādipeyyālaekādasakaṃ"
    ],
    "english": [
        "The Discourse on the Teacher",
        "Second Group of Ten Beginning with the Teacher",
        "The Eleven Repetitions Beginning with the Discourse on Training"
    ],
    "sinhala": [
        "සත්ථු සූත්‍රය",
        "දුතිය සත්ථු සූත්‍රාදි දසකය",
        "සික්ඛාසූත්තාදිපෙය්‍යාල ඒකාදසකය"
    ]
}

# Update the titles with line breaks
section_73["paliTitle"] = "\n".join(titles["pali"])
section_73["englishTitle"] = "\n".join(titles["english"])
section_73["sinhalaTitle"] = "\n".join(titles["sinhala"])

# Update the section in the data
data["sections"][section_73_idx] = section_73

print("\n✓ Updated titles:")
print(f"  Pali:\n    {section_73['paliTitle'].replace(chr(10), chr(10) + '    ')}")
print(f"  English:\n    {section_73['englishTitle'].replace(chr(10), chr(10) + '    ')}")
print(f"  Sinhala:\n    {section_73['sinhalaTitle'].replace(chr(10), chr(10) + '    ')}")

# Save the file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ File updated: {file_path}")
print("\nNow reimporting to database...")

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
    SET pali_title = ?,
        english_title = ?,
        sinhala_title = ?
    WHERE chapter_id = 'sn.2.1' AND section_number = 73
""", [
    section_73["paliTitle"],
    section_73["englishTitle"],
    section_73["sinhalaTitle"]
])

print("✅ Database updated!")

# Verify
result = client.execute_query("""
    SELECT pali_title, english_title, sinhala_title
    FROM sections 
    WHERE chapter_id = 'sn.2.1' AND section_number = 73
""", [])

rows = result['results'][0]['response']['result']['rows']
if rows:
    row = rows[0]
    print("\n📋 Verification from database:")
    print(f"  Pali Title:\n    {row[0]['value'].replace(chr(10), chr(10) + '    ')}")
    print(f"  English Title:\n    {row[1]['value'].replace(chr(10), chr(10) + '    ')}")
    print(f"  Sinhala Title:\n    {row[2]['value'].replace(chr(10), chr(10) + '    ')}")
    print("\n✅ All titles successfully added!")
