from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("Saṃyuttanikāyo Import - Final Statistics")
print("=" * 60)

importer = TursoImporterSimple(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))

stats = importer.get_stats()
print(f"  Baskets:     {stats['baskets']}")
print(f"  Collections: {stats['collections']}")
print(f"  Books:       {stats['books']}")
print(f"  Chapters:    {stats['chapters']}")
print(f"  Sections:    {stats['sections']}")
print("=" * 60)

print("\n🎉 Saṃyuttanikāyo successfully imported to Turso database!")
print(f"📊 Total content: {stats['sections']} suttas across {stats['chapters']} chapters in {stats['books']} books")