#!/usr/bin/env python3
"""
Test FTS Search Script
Helper to test full-text search queries
"""

import os
from libsql_experimental import connect

def test_fts_search(search_term):
    """Test FTS search with various query patterns"""
    
    turso_url = os.getenv('TURSO_DATABASE_URL')
    turso_token = os.getenv('TURSO_AUTH_TOKEN')
    
    if not turso_url or not turso_token:
        print("❌ Error: TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set")
        return
    
    conn = connect(database=turso_url, auth_token=turso_token)
    cursor = conn.cursor()
    
    queries = [
        ("Search in sinhala_title", f"SELECT chapter_id, section_number, sinhala_title, vagga_sinhala FROM sections_fts WHERE sinhala_title MATCH '{search_term}'"),
        ("Search in vagga_sinhala", f"SELECT chapter_id, section_number, sinhala_title, vagga_sinhala FROM sections_fts WHERE vagga_sinhala MATCH '{search_term}'"),
        ("Search in sinhala content", f"SELECT chapter_id, section_number, sinhala_title, vagga_sinhala FROM sections_fts WHERE sinhala MATCH '{search_term}'"),
        ("Search across all fields", f"SELECT chapter_id, section_number, sinhala_title, vagga_sinhala FROM sections_fts WHERE sections_fts MATCH '{search_term}'"),
    ]
    
    print(f"🔍 Testing FTS search for: '{search_term}'")
    print("=" * 80)
    
    for query_name, query in queries:
        print(f"\n📝 {query_name}:")
        print(f"   Query: {query}")
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"   ✅ Found {len(results)} results")
            
            if results:
                for i, row in enumerate(results[:5], 1):  # Show first 5 results
                    print(f"      {i}. Chapter: {row[0]}, Section: {row[1]}")
                    print(f"         Title: {row[2]}")
                    print(f"         Vagga: {row[3]}")
                if len(results) > 5:
                    print(f"      ... and {len(results) - 5} more results")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Also check the actual sections table
    print(f"\n📊 Checking sections table directly:")
    try:
        cursor.execute(f"""
            SELECT chapter_id, section_number, sinhala_title, vagga_sinhala 
            FROM sections 
            WHERE sinhala_title LIKE '%{search_term}%' 
               OR vagga_sinhala LIKE '%{search_term}%'
            LIMIT 5
        """)
        results = cursor.fetchall()
        print(f"   ✅ Found {len(results)} results with LIKE search")
        for i, row in enumerate(results, 1):
            print(f"      {i}. Chapter: {row[0]}, Section: {row[1]}")
            print(f"         Title: {row[2]}")
            print(f"         Vagga: {row[3]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_fts_search.py <search_term>")
        print("Example: python test_fts_search.py 'පුරිස'")
        sys.exit(1)
    
    search_term = ' '.join(sys.argv[1:])
    test_fts_search(search_term)
