"""Quick check for any remaining ZWJ literal issues"""
import glob

total = 0
issues = 0
issue_files = []

for f in glob.glob('*/chapters/*.json', recursive=True):
    total += 1
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    count = (content.count('[ZWJ]') + content.count('#zwj;') + 
             content.count('<ZWJ>') + content.count('&#8205;') + 
             content.count('&zwj;'))
    
    if count > 0:
        issues += 1
        issue_files.append((f, count))

print(f'\n✓ Checked {total} JSON files')
print(f'✓ Files with ZWJ literal issues: {issues}')

if issue_files:
    print('\n⚠️  Files still needing fixes:')
    for f, count in issue_files:
        print(f'  - {f}: {count} issues')
else:
    print('\n✅ All files are clean! No ZWJ literal issues found.')
