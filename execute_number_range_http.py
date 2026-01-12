#!/usr/bin/env python3
"""
Execute numberRange migration using Turso HTTP API.
This script doesn't require libsql-experimental.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_turso_config():
    """Get Turso configuration from environment."""
    url = os.getenv("TURSO_DATABASE_URL") or os.getenv("TURSO_DB_URL")
    token = os.getenv("TURSO_AUTH_TOKEN")
    
    if not url or not token:
        raise ValueError("TURSO_DATABASE_URL (or TURSO_DB_URL) and TURSO_AUTH_TOKEN must be set in .env file")
    
    # Convert libsql:// URL to https://
    if url.startswith("libsql://"):
        url = url.replace("libsql://", "https://")
    
    return url, token

def execute_sql(url, token, sql):
    """Execute SQL using Turso HTTP API."""
    api_url = f"{url}/v2/pipeline"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql}}
        ]
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    return response.json()

def execute_query(url, token, sql):
    """Execute a query and return results."""
    api_url = f"{url}/v2/pipeline"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [
            {"type": "execute", "stmt": {"sql": sql}}
        ]
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    result = response.json()
    return result.get("results", [{}])[0]

def add_column(url, token):
    """Add number_range column to sections table."""
    print("Step 1: Adding number_range column...")
    
    try:
        execute_sql(url, token, "ALTER TABLE sections ADD COLUMN number_range TEXT")
        print("✓ Column added successfully")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("✓ Column already exists")
        else:
            raise e

def create_index(url, token):
    """Create index on number_range column."""
    print("\nStep 2: Creating index...")
    
    try:
        execute_sql(url, token, "CREATE INDEX IF NOT EXISTS idx_sections_number_range ON sections(number_range)")
        print("✓ Index created successfully")
    except Exception as e:
        print(f"⚠ Index creation: {e}")

def update_sections(url, token):
    """Update sections with numberRange values."""
    print("\nStep 3: Updating sections with numberRange values...")
    
    # Read the SQL file
    with open('number_range_updates.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Extract UPDATE statements
    statements = [line.strip() for line in sql_content.split('\n') 
                  if line.strip().startswith('UPDATE')]
    
    print(f"Found {len(statements)} UPDATE statements to execute...")
    
    updated_count = 0
    failed_count = 0
    
    # Execute in batches
    batch_size = 10
    for i in range(0, len(statements), batch_size):
        batch = statements[i:i+batch_size]
        
        try:
            # Create a batch request
            api_url = f"{url}/v2/pipeline"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            requests_list = [
                {"type": "execute", "stmt": {"sql": stmt}}
                for stmt in batch
            ]
            
            payload = {"requests": requests_list}
            
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                # Count successful updates
                for res in result.get("results", []):
                    if res.get("response", {}).get("type") == "ok":
                        rows_affected = res.get("response", {}).get("result", {}).get("rows_affected", 0)
                        if rows_affected > 0:
                            updated_count += 1
            else:
                failed_count += len(batch)
                print(f"  ✗ Batch {i//batch_size + 1} failed: {response.status_code}")
            
            if (i + batch_size) % 50 == 0:
                print(f"  Progress: {min(i + batch_size, len(statements))}/{len(statements)} statements executed...")
        
        except Exception as e:
            failed_count += len(batch)
            print(f"  ✗ Error in batch {i//batch_size + 1}: {e}")
    
    print(f"\n✓ Completed: {updated_count} sections updated, {failed_count} failed")
    return updated_count

def verify_migration(url, token):
    """Verify the migration was successful."""
    print("\nStep 4: Verifying migration...")
    
    # Count sections with number_range
    result = execute_query(url, token, "SELECT COUNT(*) as count FROM sections WHERE number_range IS NOT NULL")
    
    rows = result.get("response", {}).get("result", {}).get("rows", [])
    if rows:
        count = rows[0][0]["value"]
        print(f"✓ Found {count} sections with number_range values")
        
        if count == 180:
            print("✓ Expected count matches (180 sections)")
        else:
            print(f"⚠ Expected 180 sections, found {count}")
    
    # Show some examples
    result = execute_query(url, token, """
        SELECT chapter_id, section_number, number_range 
        FROM sections 
        WHERE number_range IS NOT NULL
        LIMIT 5
    """)
    
    rows = result.get("response", {}).get("result", {}).get("rows", [])
    if rows:
        print("\nSample entries:")
        print(f"{'Chapter ID':<15} {'Section':<10} {'Number Range':<15}")
        print("-" * 40)
        for row in rows:
            chapter_id = row[0]["value"]
            section_number = row[1]["value"]
            number_range = row[2]["value"]
            print(f"{chapter_id:<15} {section_number:<10} {number_range:<15}")

def main():
    """Main execution function."""
    print("="*60)
    print("Executing numberRange Migration (HTTP API)")
    print("="*60)
    print()
    
    try:
        # Check if requests is installed
        import requests
    except ImportError:
        print("Error: 'requests' library is not installed.")
        print("\nPlease install it:")
        print("  pip install requests python-dotenv")
        return
    
    try:
        # Get configuration
        print("Connecting to Turso database...")
        url, token = get_turso_config()
        print("✓ Configuration loaded\n")
        
        # Execute migration
        add_column(url, token)
        create_index(url, token)
        updated_count = update_sections(url, token)
        verify_migration(url, token)
        
        print("\n" + "="*60)
        print("✓ Migration completed!")
        print(f"  Total sections updated: {updated_count}")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
