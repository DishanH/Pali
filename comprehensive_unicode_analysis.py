#!/usr/bin/env python3
"""
COMPREHENSIVE Unicode Analysis for Production Database
Find ALL special character issues before fixing
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter

def analyze_unicode_issues(file_path):
    """
    Comprehensive analysis of all Unicode issues in a file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = {
            'zwj_placeholders': [],      # #zwj;
            'unicode_escapes': [],       # \u0DCA etc
            'literal_unicode': [],       # {U+200D} etc
            'binary_markers': [],        # <binary data>
            'suspicious_patterns': [],   # Other suspicious patterns
            'malformed_sinhala': []      # Malformed Sinhala sequences
        }
        
        # 1. Find #zwj; placeholders
        zwj_matches = re.findall(r'[^\s]*#zwj;[^\s]*', content)
        issues['zwj_placeholders'] = list(set(zwj_matches))
        
        # 2. Find Unicode escape sequences
        unicode_escapes = re.findall(r'\\u[0-9A-Fa-f]{4}', content)
        issues['unicode_escapes'] = list(set(unicode_escapes))
        
        # 3. Find literal Unicode notation {U+XXXX}
        literal_unicode = re.findall(r'\{U\+[0-9A-Fa-f]+\}', content)
        issues['literal_unicode'] = list(set(literal_unicode))
        
        # 4. Find binary data markers
        binary_markers = re.findall(r'<binary data[^>]*>', content)
        issues['binary_markers'] = list(set(binary_markers))
        
        # 5. Find suspicious patterns
        suspicious_patterns = []
        
        # HTML entities
        html_entities = re.findall(r'&[a-zA-Z0-9#]+;', content)
        suspicious_patterns.extend(html_entities)
        
        # Malformed escape sequences
        malformed_escapes = re.findall(r'\\[^unt"\'\\]', content)
        suspicious_patterns.extend(malformed_escapes)
        
        # Multiple consecutive special chars
        multiple_specials = re.findall(r'[්‍]{3,}', content)
        suspicious_patterns.extend(multiple_specials)
        
        issues['suspicious_patterns'] = list(set(suspicious_patterns))
        
        # 6. Find malformed Sinhala sequences
        # Look for isolated combining marks
        isolated_marks = re.findall(r'(?<![අ-ෆ])්[‍]?(?![අ-ෆ])', content)
        issues['malformed_sinhala'] = list(set(isolated_marks))
        
        return issues
        
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return None

def get_character_info(char):
    """
    Get detailed information about a Unicode character
    """
    try:
        import unicodedata
        return {
            'char': char,
            'name': unicodedata.name(char, 'UNKNOWN'),
            'category': unicodedata.category(char),
            'codepoint': f'U+{ord(char):04X}'
        }
    except:
        return {
            'char': char,
            'name': 'UNKNOWN',
            'category': 'UNKNOWN',
            'codepoint': f'U+{ord(char):04X}' if len(char) == 1 else 'MULTIPLE'
        }

def analyze_specific_characters(content):
    """
    Analyze specific problematic characters in content
    """
    char_analysis = {}
    
    # Common problematic Unicode characters in Sinhala
    problem_chars = [
        '\u0DCA',  # Sinhala Al-lakuna (virama)
        '\u200D',  # Zero Width Joiner
        '\u200C',  # Zero Width Non-Joiner
        '\u00A0',  # Non-breaking space
        '\uFEFF',  # Byte Order Mark
    ]
    
    for char in problem_chars:
        count = content.count(char)
        if count > 0:
            char_analysis[char] = {
                'count': count,
                'info': get_character_info(char)
            }
    
    return char_analysis

def main():
    """
    Comprehensive Unicode analysis for production safety
    """
    print("=" * 80)
    print("COMPREHENSIVE UNICODE ANALYSIS FOR PRODUCTION DATABASE")
    print("=" * 80)
    print("🔍 Scanning ALL files for Unicode issues...")
    
    # Find all JSON files
    json_files = []
    for directory in ["Aṅguttaranikāyo", "Dīghanikāyo", "Majjhimanikāye", "Saṃyuttanikāyo"]:
        dir_path = Path(directory)
        if dir_path.exists():
            json_files.extend(dir_path.rglob("*.json"))
    
    if not json_files:
        print("❌ No JSON files found")
        return
    
    print(f"📁 Analyzing {len(json_files)} files...")
    
    # Collect all issues
    all_issues = defaultdict(list)
    files_with_issues = []
    char_stats = Counter()
    
    for i, json_file in enumerate(json_files, 1):
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(json_files)} files...")
        
        issues = analyze_unicode_issues(json_file)
        
        if issues:
            has_issues = False
            
            for issue_type, issue_list in issues.items():
                if issue_list:
                    has_issues = True
                    all_issues[issue_type].extend(issue_list)
            
            if has_issues:
                files_with_issues.append((json_file, issues))
            
            # Analyze character usage
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                char_analysis = analyze_specific_characters(content)
                for char, data in char_analysis.items():
                    char_stats[char] += data['count']
            except:
                pass
    
    # Report comprehensive results
    print(f"\n" + "=" * 80)
    print("📊 COMPREHENSIVE ANALYSIS RESULTS")
    print("=" * 80)
    
    print(f"📁 Files analyzed: {len(json_files)}")
    print(f"⚠️  Files with issues: {len(files_with_issues)}")
    
    # Issue type summary
    print(f"\n🔍 Issue Types Found:")
    for issue_type, issue_list in all_issues.items():
        unique_issues = list(set(issue_list))
        if unique_issues:
            print(f"   {issue_type}: {len(unique_issues)} unique patterns")
    
    # Detailed breakdown
    print(f"\n📝 DETAILED ISSUE BREAKDOWN:")
    print("-" * 80)
    
    # 1. ZWJ Placeholders
    if all_issues['zwj_placeholders']:
        zwj_patterns = list(set(all_issues['zwj_placeholders']))
        print(f"\n1️⃣  ZWJ PLACEHOLDERS (#zwj;): {len(zwj_patterns)} patterns")
        for i, pattern in enumerate(zwj_patterns[:10], 1):
            print(f"   {i}. {pattern}")
        if len(zwj_patterns) > 10:
            print(f"   ... and {len(zwj_patterns) - 10} more")
    
    # 2. Unicode Escapes
    if all_issues['unicode_escapes']:
        escape_patterns = list(set(all_issues['unicode_escapes']))
        print(f"\n2️⃣  UNICODE ESCAPES (\\uXXXX): {len(escape_patterns)} patterns")
        for i, pattern in enumerate(escape_patterns, 1):
            try:
                char = bytes(pattern, 'utf-8').decode('unicode_escape')
                char_info = get_character_info(char)
                print(f"   {i}. {pattern} → {char_info['name']} ({char_info['codepoint']})")
            except:
                print(f"   {i}. {pattern} → INVALID")
    
    # 3. Literal Unicode
    if all_issues['literal_unicode']:
        literal_patterns = list(set(all_issues['literal_unicode']))
        print(f"\n3️⃣  LITERAL UNICODE ({{U+XXXX}}): {len(literal_patterns)} patterns")
        for i, pattern in enumerate(literal_patterns, 1):
            print(f"   {i}. {pattern}")
    
    # 4. Binary Markers
    if all_issues['binary_markers']:
        binary_patterns = list(set(all_issues['binary_markers']))
        print(f"\n4️⃣  BINARY MARKERS: {len(binary_patterns)} patterns")
        for i, pattern in enumerate(binary_patterns, 1):
            print(f"   {i}. {pattern}")
    
    # 5. Suspicious Patterns
    if all_issues['suspicious_patterns']:
        suspicious_patterns = list(set(all_issues['suspicious_patterns']))
        print(f"\n5️⃣  SUSPICIOUS PATTERNS: {len(suspicious_patterns)} patterns")
        for i, pattern in enumerate(suspicious_patterns[:10], 1):
            print(f"   {i}. {pattern}")
        if len(suspicious_patterns) > 10:
            print(f"   ... and {len(suspicious_patterns) - 10} more")
    
    # 6. Character Statistics
    if char_stats:
        print(f"\n6️⃣  SPECIAL CHARACTER USAGE:")
        for char, count in char_stats.most_common():
            char_info = get_character_info(char)
            print(f"   {char_info['codepoint']} ({char_info['name']}): {count} occurrences")
    
    # Most affected files
    if files_with_issues:
        print(f"\n🔥 TOP 10 MOST AFFECTED FILES:")
        
        # Calculate issue score for each file
        file_scores = []
        for file_path, issues in files_with_issues:
            score = sum(len(issue_list) for issue_list in issues.values())
            file_scores.append((file_path, score, issues))
        
        file_scores.sort(key=lambda x: x[1], reverse=True)
        
        for i, (file_path, score, issues) in enumerate(file_scores[:10], 1):
            print(f"   {i}. {file_path.name}: {score} total issues")
            for issue_type, issue_list in issues.items():
                if issue_list:
                    print(f"      - {issue_type}: {len(issue_list)}")
    
    # Recommendations
    print(f"\n" + "=" * 80)
    print("💡 PRODUCTION-SAFE RECOMMENDATIONS")
    print("=" * 80)
    
    print("🔧 FIXES NEEDED:")
    
    if all_issues['zwj_placeholders']:
        print("   1. Replace #zwj; with actual ZWJ character (\\u200D)")
    
    if all_issues['unicode_escapes']:
        print("   2. Convert Unicode escapes to actual characters")
    
    if all_issues['literal_unicode']:
        print("   3. Replace {U+XXXX} notation with actual characters")
    
    if all_issues['binary_markers']:
        print("   4. Fix binary data markers")
    
    print(f"\n🛡️  PRODUCTION SAFETY MEASURES:")
    print("   ✅ Create full database backup before any changes")
    print("   ✅ Test fixes on sample files first")
    print("   ✅ Verify text rendering in target applications")
    print("   ✅ Use transaction-based database updates")
    print("   ✅ Implement rollback capability")
    
    print(f"\n📋 NEXT STEPS:")
    print("   1. Review this analysis carefully")
    print("   2. Create comprehensive fix script")
    print("   3. Test on development copy first")
    print("   4. Apply fixes with full safety measures")

if __name__ == "__main__":
    main()