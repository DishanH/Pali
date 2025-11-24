"""
Quick status checker - shows current translation status
"""

import sys
import os
import re
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def check_status():
    """Check current translation status"""
    log_file = 'translator.log'
    
    print("=" * 60)
    print("🔍 Translation Status Check")
    print("=" * 60)
    
    # Check if log file exists
    if not os.path.exists(log_file):
        print("\n❌ No log file found (translator.log)")
        print("   The translator hasn't been run yet or no activity.")
        return
    
    # Read last 100 lines
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if not lines:
            print("\n⚠️  Log file is empty")
            return
        
        recent_lines = lines[-100:]
        
        # Extract information
        last_timestamp = None
        current_section = None
        total_sections = None
        current_chapter = None
        last_activity = None
        errors = []
        
        for line in reversed(recent_lines):
            # Get timestamp
            ts_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if ts_match and not last_timestamp:
                last_timestamp = ts_match.group(1)
            
            # Section progress
            if 'Translating section' in line and not current_section:
                match = re.search(r'Translating section (\d+)/(\d+)', line)
                if match:
                    current_section = int(match.group(1))
                    total_sections = int(match.group(2))
            
            # Chapter
            if 'Processing chapter' in line and not current_chapter:
                match = re.search(r'chapter (\d+)/(\d+)', line)
                if match:
                    current_chapter = match.group(1)
            
            if 'ID: dn' in line and not current_chapter:
                match = re.search(r'ID: (dn\d+)', line)
                if match:
                    current_chapter = match.group(1)
            
            # Last meaningful activity
            if ('Translation completed' in line or 'Translating' in line) and not last_activity:
                last_activity = line.strip()
            
            # Check for errors
            if 'ERROR' in line or 'Error:' in line:
                errors.append(line.strip())
        
        # Display status
        print(f"\n📅 Last Log Entry: {last_timestamp or 'Unknown'}")
        
        if last_timestamp:
            try:
                last_time = datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                delta = (now - last_time).total_seconds()
                
                if delta < 30:
                    status = "✅ ACTIVE (last activity <30s ago)"
                elif delta < 120:
                    status = f"🟢 WORKING (last activity {int(delta)}s ago)"
                elif delta < 300:
                    status = f"🟡 RUNNING (last activity {int(delta/60)}m ago)"
                else:
                    status = f"⚠️ POSSIBLY STUCK (last activity {int(delta/60)}m ago)"
                
                print(f"🔄 Status: {status}")
                
            except:
                print("🔄 Status: Unknown")
        
        if current_chapter:
            print(f"\n📖 Current Chapter: {current_chapter}")
        
        if current_section and total_sections:
            percentage = int(100 * current_section / total_sections)
            print(f"📝 Progress: Section {current_section}/{total_sections} ({percentage}%)")
            
            # Progress bar
            filled = int(30 * current_section / total_sections)
            bar = '█' * filled + '░' * (30 - filled)
            print(f"    [{bar}]")
            
            remaining = total_sections - current_section
            est_minutes = remaining  # Rough estimate: 1 min per section
            print(f"⏱️  Est. remaining: ~{est_minutes} minutes ({remaining} sections)")
        
        if last_activity:
            print(f"\n📋 Last Activity:")
            print(f"    {last_activity[-80:]}")
        
        # Check for errors
        if errors:
            print(f"\n❌ Recent Errors Found: {len(errors)}")
            print("   Last error:")
            print(f"   {errors[0][-100:]}")
            print("\n   Run this to see all errors:")
            print("   python monitor_progress.py --tail --lines 50 | grep ERROR")
        else:
            print(f"\n✅ No errors detected")
        
        # Check output files
        print(f"\n📁 Output Files:")
        chapters_dir = os.path.join("Pāthikavaggapāḷi", "chapters")
        if os.path.exists(chapters_dir):
            json_files = [f for f in os.listdir(chapters_dir) if f.endswith('.json')]
            print(f"   Found {len(json_files)} translated chapter(s)")
            for f in sorted(json_files)[-3:]:  # Show last 3
                file_path = os.path.join(chapters_dir, f)
                size = os.path.getsize(file_path)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"   - {f} ({size:,} bytes, modified {mod_time.strftime('%H:%M:%S')})")
        else:
            print("   No output directory found")
        
        print("\n" + "=" * 60)
        print("💡 Commands:")
        print("   python monitor_progress.py      # Live monitoring")
        print("   python monitor_progress.py --tail  # Show last 20 log lines")
        print("   python check_status.py          # This script (quick status)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error reading log: {e}")


if __name__ == "__main__":
    check_status()

