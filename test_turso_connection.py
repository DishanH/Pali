"""
Test Turso database connection
"""

import os
import asyncio
from libsql_client import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

async def test_connection():
    """Test connection to Turso database"""
    print("=" * 60)
    print("Testing Turso Database Connection")
    print("=" * 60)
    
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("❌ Error: Environment variables not set!")
        print(f"TURSO_DB_URL: {'✓' if TURSO_DB_URL else '❌'}")
        print(f"TURSO_AUTH_TOKEN: {'✓' if TURSO_AUTH_TOKEN else '❌'}")
        return False
    
    print(f"Database URL: {TURSO_DB_URL}")
    print(f"Auth Token: {TURSO_AUTH_TOKEN[:20]}...")
    
    try:
        # Try to create client
        print("\n🔄 Creating client...")
        client = create_client(url=TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)
        print("✓ Client created successfully")
        
        # Try a simple query
        print("\n🔄 Testing simple query...")
        result = await client.execute("SELECT 1 as test")
        print(f"✓ Query successful: {result.rows}")
        
        # Close connection
        await client.close()
        print("✓ Connection closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())