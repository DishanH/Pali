#!/usr/bin/env python3
"""
Script to analyze the #zwj issue in JSON files
"""

import json
import re
from pathlib import Path

def analyze_zwj_in_file(file_path):
    """
    Analyze ZWJ issues in a single JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count #zwj occurrences
        zwj_count = content.count('#zwj')
        
        if zwj_count > 0:
            # Load JSON to analyze structure
            data = json.loads(content)
            
            # Check where #zwj appears
            locations = {
                'title': False,
                'sections': 0,
                'footer': False
            }
            
            # Check title
            if 'title' in data:
                title_str = json.dumps(data['title'], ensure_ascii=False)
                if '#zwj' in title_str:
                    locations['title'] = True
            
            # Check sections
            if 'sections' in data:
                for section in data['sections']:
                    section_str = json.dumps(section, ensure_ascii=False)
                    if '#zwj' in section_str:
                        locations['sections'] += 1
            
            # Check footer
            if 'footer' in data:
                footer_str = json.dumps(data['footer'], ensure_ascii=False)
                if '#zwj' in footer_str:
                    locations['footer'] = True
            
            return zwj_count, locations
        
        return 0, None
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return 0, None

def analyze_zwj_context(text_sample):
    """
    Analyze the context around #zwj to understand what it should be
    """
    # Find patterns around #zwj
    patterns = re.findall(r'\S*#zwj;\S*', text_sample)
    return patterns[:10]  # Return first 10 patterns

def main():
    """
    Main analysis function
    """
    print("=" * 70)
    print("ZWJ Issue Analysis")
    print("=" * 70)
    
    # Find all JSON files
    json_files = []
    
    # Search in all collection directories
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    if not json_files:
        print("No JSON files found to analyze")
        return
    
    print(f"📁 Analyzing {len(json_files)} JSON files...")
    
    # Analyze files
    files_with_zwj = []
    total_zwj_count = 0
    location_stats = {
        'title': 0,
        'sections': 0,
        'footer': 0
    }
    
    all_patterns = []
    
    for json_file in json_files:
        zwj_count, locations = analyze_zwj_in_file(json_file)
        
        if zwj_count > 0:
            files_with_zwj.append((json_file, zwj_count, locations))
            total_zwj_count += zwj_count
            
            if locations:
                if locations['title']:
                    location_stats['title'] += 1
                if locations['sections'] > 0:
                    location_stats['sections'] += locations['sections']
                if locations['footer']:
                    location_stats['footer'] += 1
            
            # Get sample patterns from first few files
            if len(all_patterns) < 50:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    patterns = analyze_zwj_context(content)
                    all_patterns.extend(patterns)
                except:
                    pass
    
    # Report results
    print(f"\n📊 Analysis Results:")
    print(f"   Files with #zwj issues: {len(files_with_zwj)}")
    print(f"   Total #zwj occurrences: {total_zwj_count}")
    print(f"   Titles affected: {location_stats['title']}")
    print(f"   Sections affected: {location_stats['sections']}")
    print(f"   Footers affected: {location_stats['footer']}")
    
    # Show top affected files
    if files_with_zwj:
        print(f"\n🔍 Top 10 most affected files:")
        sorted_files = sorted(files_with_zwj, key=lambda x: x[1], reverse=True)
        for i, (file_path, count, locations) in enumerate(sorted_files[:10], 1):
            print(f"   {i}. {file_path.name}: {count} occurrences")
    
    # Show common patterns
    if all_patterns:
        print(f"\n📝 Common #zwj patterns (first 20):")
        unique_patterns = list(set(all_patterns))[:20]
        for i, pattern in enumerate(unique_patterns, 1):
            print(f"   {i}. {pattern}")
    
    # Analysis of what #zwj should be
    print(f"\n🔍 Analysis:")
    print(f"   #zwj appears to be a placeholder for Zero Width Joiner (ZWJ)")
    print(f"   In Sinhala text, ZWJ is used to form conjunct consonants")
    print(f"   Common pattern: සත්#zwj;ත්වයෝ should be සත්‍ත්වයෝ")
    print(f"   The #zwj; should be replaced with the actual ZWJ character (\\u200D)")
    
    print(f"\n💡 Recommendations:")
    print(f"   1. Replace #zwj; with actual ZWJ character (\\u200D)")
    print(f"   2. This is safer than removing it or replacing with space")
    print(f"   3. ZWJ is essential for proper Sinhala rendering")
    print(f"   4. Consider doing this replacement at display time rather than in database")
    print(f"   5. Test rendering in target applications before mass replacement")

if __name__ == "__main__":
    main()