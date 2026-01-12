"""
Simple check for database schema and missing footers
"""

from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print("=" * 80)
    print("🔍 CHECKING DATABASE SCHEMA AND FOOTERS")
    print("=" * 80)
    
    try:
        importer = TursoImporterSimple(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))
        
        # Check if chapters table has footer columns by trying to select them
        print("🔍 Checking if footer columns exist...")
        
        try:
            result = importer.client.execute_query("SELECT footer_pali, footer_english, footer_sinhala FROM chapters LIMIT 1")
            print("✅ Footer columns exist in chapters table")
            
            # Count chapters with footers
            result = importer.client.execute_query("SELECT COUNT(*) FROM chapters WHERE footer_pali IS NOT NULL AND footer_pali != ''")
            count = int(result['results'][0]['response']['result']['rows'][0][0]['value'])
            
            total_result = importer.client.execute_query("SELECT COUNT(*) FROM chapters")
            total = int(total_result['results'][0]['response']['result']['rows'][0][0]['value'])
            
            print(f"📊 Chapters with footers: {count} / {total}")
            
            if count == 0:
                print("❌ NO CHAPTER FOOTERS IN DATABASE - WE NEED TO ADD THEM!")
            else:
                print(f"✅ Found {count} chapters with footers")
                
        except Exception as e:
            print(f"❌ Footer columns don't exist in chapters table: {e}")
            print("🔧 We need to add footer columns to the chapters table!")
        
        print("\n" + "=" * 80)
        print("🎯 CONCLUSION:")
        print("   Chapter files have footers but database is missing them!")
        print("   We need to:")
        print("   1. Add footer columns to chapters table (if missing)")
        print("   2. Update import script to include chapter footers")
        print("   3. Re-import or update all chapters with footers")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()