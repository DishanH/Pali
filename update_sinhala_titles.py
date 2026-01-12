#!/usr/bin/env python3
"""
Script to update Sinhala titles in the Turso database for specific suttas.
Updates:
1. Section 121: ආත්‍මාරෝපණ සූත්‍රය → අත්තානුවාද සූත්‍රය
2. Section 122: උ‍ර්මිභය සූත‍්‍රය → ඌමිභය සූත්‍රය
"""

import sys

# Import database connection utilities
try:
    from config import get_turso_connection
except ImportError:
    print("Error: config.py not found. Please ensure database configuration is available.")
    sys.exit(1)

def update_sinhala_titles():
    """Update the Sinhala titles in the Turso database."""
    try:
        # Get Turso connection
        client = get_turso_connection()
        print("Connected to Turso database successfully")
        
        # Update section 121 - Attānuvādasuttaṃ
        result_121 = client.execute_query("""
            UPDATE sections 
            SET sinhala_title = ? 
            WHERE section_number = 121 AND chapter_id = 'an4.13'
        """, ["අත්තානුවාද සූත්‍රය"])
        
        print(f"Updated section 121")
        
        # Update section 122 - Ūmibhayasuttaṃ  
        result_122 = client.execute_query("""
            UPDATE sections 
            SET sinhala_title = ? 
            WHERE section_number = 122 AND chapter_id = 'an4.13'
        """, ["ඌමිභය සූත්‍රය"])
        
        print(f"Updated section 122")
        
        # Verify the updates
        verification_result = client.execute_query("""
            SELECT section_number, sinhala_title 
            FROM sections 
            WHERE chapter_id = 'an4.13' AND section_number IN (121, 122)
            ORDER BY section_number
        """)
        
        if verification_result.get('results'):
            rows = verification_result['results'][0]['response']['result']['rows']
            print("\nVerification - Updated titles:")
            for row in rows:
                print(f"Section {row[0]}: {row[1]}")
        
        print(f"\n✓ Successfully updated Sinhala titles in Turso database")
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to Turso database: {e}")
        return False

if __name__ == "__main__":
    print("Updating Sinhala titles in database...")
    success = update_sinhala_titles()
    if success:
        print("Update completed successfully!")
    else:
        print("Update failed!")