"""
Verify that ZWJ fix is working correctly
Shows before/after comparison
"""

import json

def check_file(json_path: str):
    """Check a specific file for ZWJ issues"""
    print(f"\n{'='*70}")
    print(f"File: {json_path}")
    print(f"{'='*70}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
    except FileNotFoundError:
        print(f"❌ File not found: {json_path}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return
    
    # Check for all ZWJ literal variations in the entire file
    zwj_issues = {
        '<ZWJ>': content.count('<ZWJ>'),
        '[ZWJ]': content.count('[ZWJ]'),
        '#zwj;': content.count('#zwj;'),
        '&#8205;': content.count('&#8205;'),
        '&zwj;': content.count('&zwj;')
    }
    
    has_proper_zwj = '\u200D' in content
    total_issues = sum(zwj_issues.values())
    
    print(f"\n📊 Analysis:")
    print(f"  • Contains proper ZWJ (U+200D): {'✓ YES' if has_proper_zwj else '❌ NO'}")
    print(f"  • Total ZWJ literal issues: {total_issues}")
    
    if total_issues > 0:
        print(f"\n⚠️  Found literal ZWJ text:")
        for variant, count in zwj_issues.items():
            if count > 0:
                print(f"    - {variant}: {count} occurrences")
    
    # Show examples from sections
    sections = data.get('sections', [])
    if sections:
        print(f"\n📝 Checking sections ({len(sections)} total):")
        issues_found = []
        
        for section in sections[:5]:  # Check first 5 sections
            section_num = section.get('number', '?')
            sinhala = section.get('sinhala', '')
            
            # Check for any literal ZWJ in this section
            section_issues = []
            for variant in zwj_issues.keys():
                if variant in sinhala:
                    section_issues.append(variant)
            
            if section_issues:
                issues_found.append((section_num, section_issues, sinhala[:100]))
        
        if issues_found:
            print(f"\n  ⚠️  Sections with literal ZWJ:")
            for num, variants, sample in issues_found:
                print(f"    Section {num}: {', '.join(variants)}")
                print(f"      Sample: {sample}...")
        else:
            print(f"  ✓ No literal ZWJ found in checked sections")
    
    print(f"\n{'='*70}")
    if has_proper_zwj and total_issues == 0:
        print("✅ FILE IS CORRECT - ZWJ properly implemented")
    elif total_issues > 0:
        print("❌ FILE HAS ISSUES - Contains literal ZWJ text")
    else:
        print("⚠️  FILE MAY NEED REVIEW - No ZWJ found")
    print(f"{'='*70}")

def main():
    """Check files mentioned in the issue"""
    print("\n" + "="*70)
    print("ZWJ (Zero-Width Joiner) Verification")
    print("="*70)
    print("\nChecking files mentioned in the issue...")
    
    # Files mentioned by user
    files_to_check = [
        'Pāthikavaggapāḷi/chapters/dn1-Pāthikasuttaṃ.json',
        'Pāthikavaggapāḷi/chapters/dn2-Udumbarikasuttaṃ.json',
        'Sīlakkhandhavaggapāḷi/chapters/dn1-Brahmajālasuttaṃ.json',
        'Pāthikavaggapāḷi/chapters/dn9-Poṭṭhapādasuttaṃ.json',
        'Pāthikavaggapāḷi/chapters/dn10-Subhasuttaṃ.json',
        'Pāthikavaggapāḷi/chapters/dn12-Lohiccasuttaṃ.json',
        'Pāthikavaggapāḷi/chapters/dn13-Tevijjasuttaṃ.json',
    ]
    
    for file_path in files_to_check:
        check_file(file_path)
    
    print("\n\n📚 EXPLANATION:")
    print("="*70)
    print("Zero-Width Joiner (U+200D) is essential for Sinhala conjuncts.")
    print("\nCommon literal formats that need fixing:")
    print("  • <ZWJ>   - XML-like format")
    print("  • [ZWJ]   - Bracket format")
    print("  • #zwj;   - Hash format")
    print("  • &#8205; - HTML numeric entity")
    print("  • &zwj;   - HTML named entity")
    print("\nAll should be replaced with actual U+200D character.")
    print("\nExample:")
    print("  WRONG: ශ්‍ර[ZWJ]මණ or ශ්‍ර#zwj;මණ")
    print("  RIGHT: ශ්‍රමණ (with invisible U+200D ZWJ)")
    print("="*70)

if __name__ == '__main__':
    main()
