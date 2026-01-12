"""
Merge sections 73, 73.1, and 73.2 into a single section 73 with line breaks
"""

import json
from pathlib import Path

# Path to the file
file_path = Path("Saṃyuttanikāyo/Nidānavaggo/chapters/sn.2.1-Nidānasaṃyuttaṃ.json")

# Read the file
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Find sections 73, 73.1, and 73.2
section_73 = None
section_73_1 = None
section_73_2 = None
section_73_idx = None

for idx, section in enumerate(data["sections"]):
    if section["number"] == 73:
        section_73 = section
        section_73_idx = idx
    elif section["number"] == 73.1:
        section_73_1 = section
    elif section["number"] == 73.2:
        section_73_2 = section

if not all([section_73, section_73_1, section_73_2]):
    print("❌ Could not find all three sections")
    exit(1)

print("Found all three sections:")
print(f"  Section 73: {len(section_73['pali'])} chars")
print(f"  Section 73.1: {len(section_73_1['pali'])} chars")
print(f"  Section 73.2: {len(section_73_2['pali'])} chars")

# Merge the content with line breaks
merged_section = {
    "number": 73,
    "pali": f"{section_73['pali']}\n\n{section_73_1['pali']}\n\n{section_73_2['pali']}",
    "english": f"{section_73['english']}\n\n{section_73_1['english']}\n\n{section_73_2['english']}",
    "sinhala": f"{section_73['sinhala']}\n\n{section_73_1['sinhala']}\n\n{section_73_2['sinhala']}",
    "paliTitle": section_73["paliTitle"],
    "vagga": section_73["vagga"],
    "englishTitle": section_73["englishTitle"],
    "sinhalaTitle": section_73["sinhalaTitle"],
    "vaggaEnglish": section_73["vaggaEnglish"],
    "vaggaSinhala": section_73["vaggaSinhala"]
}

# Add note about merged sections
merged_section["note"] = "Merged from sections 73, 73.1 (2-11), and 73.2 (2-12)"

# Remove sections 73.1 and 73.2 from the list
new_sections = []
for section in data["sections"]:
    if section["number"] in [73.1, 73.2]:
        continue
    elif section["number"] == 73:
        new_sections.append(merged_section)
    else:
        new_sections.append(section)

data["sections"] = new_sections

print(f"\n✓ Merged section 73:")
print(f"  Total Pali chars: {len(merged_section['pali'])}")
print(f"  Total English chars: {len(merged_section['english'])}")
print(f"  Total Sinhala chars: {len(merged_section['sinhala'])}")
print(f"  Total sections now: {len(new_sections)} (was {len(data['sections']) + 2})")

# Save the file
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ File updated: {file_path}")
print("\nNow run: python delete_and_reimport_sections.py")
