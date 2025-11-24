"""
Real-time progress monitor for translator
Watches the log file and shows current progress
"""

import sys
import os
import time
import re
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def parse_log_file(log_path):
    """Parse the log file to extract progress information"""
    if not os.path.exists(log_path):
        return None
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        return None
    
    if not lines:
        return None
    
    # Get last few lines
    recent_lines = lines[-50:]
    
    info = {
        'current_chapter': None,
        'current_section': None,
        'total_sections': None,
        'current_language': None,
        'last_activity': None,
        'status': 'Unknown'
    }
    
    for line in reversed(recent_lines):
        # Extract timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if timestamp_match and not info['last_activity']:
            info['last_activity'] = timestamp_match.group(1)
        
        # Extract section progress
        if 'Translating section' in line:
            match = re.search(r'Translating section (\d+)/(\d+)', line)
            if match:
                info['current_section'] = int(match.group(1))
                info['total_sections'] = int(match.group(2))
        
        # Extract chapter info
        if 'Processing chapter' in line:
            match = re.search(r'chapter (dn\d+)', line)
            if match:
                info['current_chapter'] = match.group(1)
        
        # Extract language being translated
        if 'Translating' in line and 'characters to' in line:
            if 'English' in line:
                info['current_language'] = 'English'
            elif 'Sinhala' in line:
                info['current_language'] = 'Sinhala'
        
        # Check for completion
        if 'translation completed' in line.lower():
            info['status'] = 'Active'
        
        # Check for errors
        if 'ERROR' in line or 'Error' in line:
            info['status'] = 'Error'
            break
    
    # Calculate time since last activity
    if info['last_activity']:
        try:
            last_time = datetime.strptime(info['last_activity'], '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            delta = (now - last_time).total_seconds()
            info['seconds_since_activity'] = delta
            
            if delta < 60:
                info['status'] = 'Active ✓'
            elif delta < 300:  # 5 minutes
                info['status'] = 'Working...'
            else:
                info['status'] = 'Stalled? (>5 min idle)'
        except:
            pass
    
    return info


def format_progress_bar(current, total, width=30):
    """Create a progress bar"""
    if not total or total == 0:
        return '[' + '?' * width + ']'
    
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    percentage = int(100 * current / total)
    return f'[{bar}] {percentage}%'


def display_progress(info):
    """Display progress information"""
    print('\033[2J\033[H')  # Clear screen and move to top
    
    print("=" * 60)
    print("📊 Translation Progress Monitor")
    print("=" * 60)
    
    if not info:
        print("\n⚠️  No log file found or no activity yet")
        print("\nWaiting for translator to start...")
        return
    
    print(f"\n🕐 Last Activity: {info.get('last_activity', 'Unknown')}")
    
    seconds = info.get('seconds_since_activity', 0)
    if seconds < 60:
        time_str = f"{int(seconds)} seconds ago"
    else:
        time_str = f"{int(seconds / 60)} minutes ago"
    print(f"   ({time_str})")
    
    print(f"\n📈 Status: {info.get('status', 'Unknown')}")
    
    if info.get('current_chapter'):
        print(f"\n📖 Chapter: {info['current_chapter']}")
    
    if info.get('current_section') and info.get('total_sections'):
        current = info['current_section']
        total = info['total_sections']
        print(f"\n📝 Section Progress: {current}/{total}")
        print(f"   {format_progress_bar(current, total)}")
        
        # Estimate remaining time
        if current > 0:
            avg_time_per_section = 60  # Roughly 1 minute per section (2 translations × 30s)
            remaining_sections = total - current
            est_minutes = (remaining_sections * avg_time_per_section) / 60
            print(f"\n⏱️  Estimated time remaining: ~{int(est_minutes)} minutes")
    
    if info.get('current_language'):
        print(f"\n🌐 Currently translating: {info['current_language']}")
    
    print("\n" + "-" * 60)
    print("💡 Tips:")
    print("  - Check translator.log for detailed logs")
    print("  - Each section = 2 translations (English + Sinhala)")
    print("  - Rate limit delay = 2 seconds between API calls")
    print("  - Press Ctrl+C to stop monitoring (won't stop translator)")
    print("=" * 60)
    
    # Warning if stalled
    if seconds and seconds > 300:
        print("\n⚠️  WARNING: No activity for >5 minutes!")
        print("   The translator might be stuck or waiting for API response")
        print("   Check the log file for errors:")
        print("   tail -f translator.log")


def monitor_loop(log_path='translator.log', refresh_seconds=5):
    """Monitor loop that updates progress"""
    print("Starting progress monitor...")
    print(f"Watching: {log_path}")
    print(f"Refresh rate: {refresh_seconds} seconds")
    print("\nPress Ctrl+C to exit\n")
    time.sleep(2)
    
    try:
        while True:
            info = parse_log_file(log_path)
            display_progress(info)
            time.sleep(refresh_seconds)
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        print("  (Translator continues running if started separately)")


def tail_log(log_path='translator.log', num_lines=20):
    """Show last N lines of log file"""
    if not os.path.exists(log_path):
        print(f"Log file not found: {log_path}")
        return
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("=" * 60)
        print(f"Last {num_lines} lines of {log_path}:")
        print("=" * 60)
        
        for line in lines[-num_lines:]:
            print(line.rstrip())
        
        print("=" * 60)
    except Exception as e:
        print(f"Error reading log: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor translation progress')
    parser.add_argument('--log', default='translator.log', help='Path to log file')
    parser.add_argument('--refresh', type=int, default=5, help='Refresh interval in seconds')
    parser.add_argument('--tail', action='store_true', help='Show last 20 lines and exit')
    parser.add_argument('--lines', type=int, default=20, help='Number of lines to show with --tail')
    
    args = parser.parse_args()
    
    if args.tail:
        tail_log(args.log, args.lines)
    else:
        monitor_loop(args.log, args.refresh)


if __name__ == "__main__":
    main()

