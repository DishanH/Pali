"""
Import Majjhimanikāye to Turso database
"""

from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print("=" * 60)
    print("Majjhimanikāye Import to Turso Database")
    print("=" * 60)
    
    try:
        # Initialize importer
        importer = TursoImporterSimple(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))
        
        # Import Majjhimanikāye collection
        print("\n🚀 Starting Majjhimanikāye import...")
        success = importer.import_collection("Majjhimanikāye")
        
        if success:
            print("\n🎉 Import completed successfully!")
        else:
            print("\n⚠️  Import completed with some issues")
        
        # Show final statistics
        stats = importer.get_stats()
        print("\n" + "=" * 60)
        print("Updated Database Statistics:")
        print("=" * 60)
        print(f"  Baskets:     {stats['baskets']}")
        print(f"  Collections: {stats['collections']}")
        print(f"  Books:       {stats['books']}")
        print(f"  Chapters:    {stats['chapters']}")
        print(f"  Sections:    {stats['sections']}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()