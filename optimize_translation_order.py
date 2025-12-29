#!/usr/bin/env python3
"""
Translation Order Optimizer
Analyzes missing translations and suggests optimal translation order
to maximize efficiency and consistency.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict
import re

class TranslationOptimizer:
    def __init__(self, translation_dir="missing_translations"):
        self.translation_dir = Path(translation_dir)
        self.patterns = {
            'vagga': r'vaggo$|vagga$',
            'sutta': r'suttaṃ$|sutta$',
            'samyutta': r'saṃyuttaṃ$|samyutta$',
            'nipata': r'nipāto$|nipata$',
            'pannasa': r'paṇṇāsapāḷi$|pannasa$',
            'numbers': r'^(paṭhama|dutiya|tatiya|catuttha|pañcama|chaṭṭha|sattama|aṭṭhama|navama|dasama)',
            'compounds': r'(ādisutta|peyyāla|dasaka)'
        }
    
    def analyze_terms(self, language):
        """Analyze terms and group by patterns"""
        csv_file = self.translation_dir / f"missing_{language}_translations.csv"
        
        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            return None
        
        # Read terms
        terms = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                terms.append({
                    'pali': row['Pali Text'].strip(),
                    'translation': row[f'{language.title()} Translation'].strip(),
                    'contexts': row['Contexts'],
                    'usage_count': int(row['Usage Count'])
                })
        
        # Group by patterns
        groups = defaultdict(list)
        ungrouped = []
        
        for term in terms:
            pali = term['pali'].lower()
            grouped = False
            
            for pattern_name, pattern in self.patterns.items():
                if re.search(pattern, pali):
                    groups[pattern_name].append(term)
                    grouped = True
                    break
            
            if not grouped:
                ungrouped.append(term)
        
        return {
            'total_terms': len(terms),
            'translated': len([t for t in terms if t['translation']]),
            'groups': dict(groups),
            'ungrouped': ungrouped
        }
    
    def generate_optimized_batches(self, language, batch_size=20):
        """Generate optimized translation batches"""
        analysis = self.analyze_terms(language)
        if not analysis:
            return
        
        print(f"\n📊 Analysis for {language.title()} translations:")
        print(f"   Total terms: {analysis['total_terms']}")
        print(f"   Already translated: {analysis['translated']}")
        print(f"   Remaining: {analysis['total_terms'] - analysis['translated']}")
        
        # Show group statistics
        print(f"\n📋 Term groups found:")
        for group_name, terms in analysis['groups'].items():
            untranslated = [t for t in terms if not t['translation']]
            if untranslated:
                print(f"   {group_name}: {len(untranslated)} terms")
        
        print(f"   ungrouped: {len([t for t in analysis['ungrouped'] if not t['translation']])} terms")
        
        # Generate optimized batches
        batches = []
        current_batch = []
        
        # Priority 1: High-frequency terms (usage_count >= 5)
        high_freq_terms = []
        for group_terms in analysis['groups'].values():
            high_freq_terms.extend([t for t in group_terms if not t['translation'] and t['usage_count'] >= 5])
        high_freq_terms.extend([t for t in analysis['ungrouped'] if not t['translation'] and t['usage_count'] >= 5])
        high_freq_terms.sort(key=lambda x: -x['usage_count'])
        
        # Priority 2: Group similar terms together
        remaining_groups = {}
        for group_name, terms in analysis['groups'].items():
            untranslated = [t for t in terms if not t['translation'] and t['usage_count'] < 5]
            if untranslated:
                remaining_groups[group_name] = sorted(untranslated, key=lambda x: -x['usage_count'])
        
        # Priority 3: Ungrouped terms
        remaining_ungrouped = [t for t in analysis['ungrouped'] 
                             if not t['translation'] and t['usage_count'] < 5]
        remaining_ungrouped.sort(key=lambda x: -x['usage_count'])
        
        # Build batches
        all_remaining = high_freq_terms.copy()
        
        # Add grouped terms
        for group_name, terms in remaining_groups.items():
            all_remaining.extend(terms)
        
        # Add ungrouped terms
        all_remaining.extend(remaining_ungrouped)
        
        # Create batches
        for i in range(0, len(all_remaining), batch_size):
            batch = all_remaining[i:i + batch_size]
            batches.append(batch)
        
        # Save optimized batches
        output_file = self.translation_dir / f"optimized_{language}_batches.json"
        batch_data = {
            'language': language,
            'batch_size': batch_size,
            'total_batches': len(batches),
            'total_terms': len(all_remaining),
            'batches': []
        }
        
        for i, batch in enumerate(batches):
            batch_info = {
                'batch_number': i + 1,
                'terms': batch,
                'priority_breakdown': {
                    'high_frequency': len([t for t in batch if t['usage_count'] >= 5]),
                    'grouped_terms': len([t for t in batch if any(
                        re.search(pattern, t['pali'].lower()) 
                        for pattern in self.patterns.values()
                    ) and t['usage_count'] < 5]),
                    'ungrouped_terms': len([t for t in batch if not any(
                        re.search(pattern, t['pali'].lower()) 
                        for pattern in self.patterns.values()
                    ) and t['usage_count'] < 5])
                }
            }
            batch_data['batches'].append(batch_info)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        # Generate human-readable batch files
        for i, batch in enumerate(batches[:5]):  # First 5 batches
            batch_file = self.translation_dir / f"optimized_{language}_batch_{i+1:02d}.txt"
            with open(batch_file, 'w', encoding='utf-8') as f:
                f.write(f"# Optimized {language.title()} Translation Batch {i+1}\n")
                f.write(f"# Terms: {len(batch)}\n")
                f.write(f"# Priority breakdown: {batch_data['batches'][i]['priority_breakdown']}\n\n")
                
                for j, term in enumerate(batch):
                    f.write(f"{j+1:2d}. {term['pali']}\n")
                    f.write(f"    Usage: {term['usage_count']} times\n")
                    f.write(f"    Context: {term['contexts'].split(' | ')[0]}\n")
                    f.write(f"    Translation: _______________\n\n")
        
        print(f"\n✅ Generated {len(batches)} optimized batches")
        print(f"📁 Files created:")
        print(f"   - optimized_{language}_batches.json (complete data)")
        for i in range(min(5, len(batches))):
            print(f"   - optimized_{language}_batch_{i+1:02d}.txt (human-readable)")
        
        return batch_data
    
    def suggest_translation_strategy(self):
        """Suggest optimal translation strategy"""
        print("\n🎯 Recommended Translation Strategy:")
        print("=" * 50)
        
        for language in ['english', 'sinhala']:
            analysis = self.analyze_terms(language)
            if not analysis:
                continue
            
            remaining = analysis['total_terms'] - analysis['translated']
            if remaining == 0:
                print(f"\n✅ {language.title()}: All translations complete!")
                continue
            
            print(f"\n📚 {language.title()} ({remaining} terms remaining):")
            
            # High-frequency terms
            high_freq = []
            for group_terms in analysis['groups'].values():
                high_freq.extend([t for t in group_terms if not t['translation'] and t['usage_count'] >= 5])
            high_freq.extend([t for t in analysis['ungrouped'] if not t['translation'] and t['usage_count'] >= 5])
            
            if high_freq:
                days_high_freq = (len(high_freq) + 19) // 20
                print(f"   1. High-frequency terms: {len(high_freq)} terms ({days_high_freq} days)")
                print(f"      These appear in multiple contexts - maximum impact!")
            
            # Group-based translation
            group_terms = 0
            for group_name, terms in analysis['groups'].items():
                untranslated = [t for t in terms if not t['translation'] and t['usage_count'] < 5]
                if untranslated:
                    group_terms += len(untranslated)
            
            if group_terms > 0:
                days_groups = (group_terms + 19) // 20
                print(f"   2. Grouped terms: {group_terms} terms ({days_groups} days)")
                print(f"      Similar patterns - easier to maintain consistency")
            
            # Remaining terms
            remaining_ungrouped = len([t for t in analysis['ungrouped'] 
                                    if not t['translation'] and t['usage_count'] < 5])
            if remaining_ungrouped > 0:
                days_ungrouped = (remaining_ungrouped + 19) // 20
                print(f"   3. Other terms: {remaining_ungrouped} terms ({days_ungrouped} days)")
            
            total_days = (remaining + 19) // 20
            print(f"   📅 Total time: {total_days} days at 20 terms/day")
        
        print(f"\n💡 Tips:")
        print(f"   - Start with high-frequency terms for maximum impact")
        print(f"   - Translate similar terms together for consistency")
        print(f"   - Use context information to choose better translations")
        print(f"   - Review auto-translations before applying")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimize translation order')
    parser.add_argument('--language', choices=['english', 'sinhala', 'both'], 
                       default='both', help='Language to optimize')
    parser.add_argument('--batch-size', type=int, default=20, 
                       help='Batch size for optimization')
    parser.add_argument('--translation-dir', default='missing_translations',
                       help='Directory containing translation files')
    
    args = parser.parse_args()
    
    optimizer = TranslationOptimizer(args.translation_dir)
    
    print("=" * 60)
    print("Translation Order Optimizer")
    print("=" * 60)
    
    if args.language in ['english', 'both']:
        optimizer.generate_optimized_batches('english', args.batch_size)
    
    if args.language in ['sinhala', 'both']:
        optimizer.generate_optimized_batches('sinhala', args.batch_size)
    
    optimizer.suggest_translation_strategy()


if __name__ == "__main__":
    main()