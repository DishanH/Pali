from import_to_turso_simple import TursoImporterSimple
from dotenv import load_dotenv
import os

load_dotenv()

importer = TursoImporterSimple(os.getenv('TURSO_DB_URL'), os.getenv('TURSO_AUTH_TOKEN'))

# Test the stats function
try:
    stats = importer.get_stats()
    print("Stats:", stats)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()