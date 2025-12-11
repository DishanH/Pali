"""
Example queries for the Turso Pali Tipitaka database
Demonstrates various ways to query the imported data
"""

import os
import libsql_experimental as libsql

# Configuration
TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")


def connect_db():
    """Connect to Turso database"""
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        raise ValueError("TURSO_DB_URL and TURSO_AUTH_TOKEN must be set")
    return libsql.connect(database=TURSO_DB_URL, auth_token=TURSO_AUTH_TOKEN)


def example_1_list_nikayas():
    """Example 1: List all Nikayas"""
    print("\n" + "="*60)
    print("Example 1: List All Nikayas")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name_pali, name_english, name_sinhala 
        FROM nikayas
        ORDER BY id
    """)
    
    for row in cursor.fetchall():
        print(f"\nID: {row[0]}")
        print(f"  Pali:    {row[1]}")
        print(f"  English: {row[2]}")
        print(f"  Sinhala: {row[3]}")
    
    conn.close()


def example_2_books_in_nikaya(nikaya_id="samyutta"):
    """Example 2: List all books in a specific Nikaya"""
    print("\n" + "="*60)
    print(f"Example 2: Books in {nikaya_id} Nikaya")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, title_pali, title_english, total_chapters
        FROM books
        WHERE nikaya_id = ?
        ORDER BY name
    """, (nikaya_id,))
    
    for row in cursor.fetchall():
        print(f"\n{row[1]} ({row[0]})")
        print(f"  Pali:     {row[2]}")
        print(f"  English:  {row[3]}")
        print(f"  Chapters: {row[4]}")
    
    conn.close()


def example_3_chapters_in_book(book_id="Mahāvaggo"):
    """Example 3: List chapters in a specific book"""
    print("\n" + "="*60)
    print(f"Example 3: Chapters in {book_id}")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, chapter_number, title_pali, title_english
        FROM chapters
        WHERE book_id = ?
        ORDER BY chapter_number
    """, (book_id,))
    
    for row in cursor.fetchall():
        print(f"\n{row[0]} - Chapter {row[1]}")
        print(f"  Pali:    {row[2]}")
        print(f"  English: {row[3]}")
    
    conn.close()


def example_4_sections_in_chapter(chapter_id="sn.5.1", limit=3):
    """Example 4: Get sections from a specific chapter"""
    print("\n" + "="*60)
    print(f"Example 4: First {limit} Sections in {chapter_id}")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            section_number,
            pali_title,
            english_title,
            vagga,
            vagga_english,
            SUBSTR(pali, 1, 100) as pali_excerpt,
            SUBSTR(english, 1, 150) as english_excerpt
        FROM sections
        WHERE chapter_id = ?
        ORDER BY section_number
        LIMIT ?
    """, (chapter_id, limit))
    
    for row in cursor.fetchall():
        print(f"\n--- Section {row[0]} ---")
        if row[1]:
            print(f"Title (Pali):    {row[1]}")
        if row[2]:
            print(f"Title (English): {row[2]}")
        if row[3]:
            print(f"Vagga:           {row[3]} ({row[4]})")
        print(f"\nPali excerpt:    {row[5]}...")
        print(f"English excerpt: {row[6]}...")
    
    conn.close()


def example_5_search_pali_text(search_term="bhagavā", limit=5):
    """Example 5: Full-text search in Pali text"""
    print("\n" + "="*60)
    print(f"Example 5: Search for '{search_term}' in Pali text")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.chapter_id,
            s.section_number,
            c.title_pali as chapter_title,
            s.pali_title,
            SUBSTR(s.pali, 1, 200) as excerpt
        FROM sections_fts 
        JOIN sections s ON sections_fts.rowid = s.id
        JOIN chapters c ON s.chapter_id = c.id
        WHERE sections_fts.pali MATCH ?
        LIMIT ?
    """, (search_term, limit))
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} results (showing first {limit}):\n")
    
    for i, row in enumerate(results, 1):
        print(f"{i}. {row[0]} - Section {row[1]}")
        print(f"   Chapter: {row[2]}")
        if row[3]:
            print(f"   Title:   {row[3]}")
        print(f"   Excerpt: {row[4]}...\n")
    
    conn.close()


def example_6_search_english_text(search_term="meditation", limit=5):
    """Example 6: Full-text search in English translations"""
    print("\n" + "="*60)
    print(f"Example 6: Search for '{search_term}' in English text")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.chapter_id,
            s.section_number,
            c.title_english as chapter_title,
            s.english_title,
            SUBSTR(s.english, 1, 200) as excerpt
        FROM sections_fts 
        JOIN sections s ON sections_fts.rowid = s.id
        JOIN chapters c ON s.chapter_id = c.id
        WHERE sections_fts.english MATCH ?
        LIMIT ?
    """, (search_term, limit))
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} results (showing first {limit}):\n")
    
    for i, row in enumerate(results, 1):
        print(f"{i}. {row[0]} - Section {row[1]}")
        print(f"   Chapter: {row[2]}")
        if row[3]:
            print(f"   Title:   {row[3]}")
        print(f"   Excerpt: {row[4]}...\n")
    
    conn.close()


def example_7_sections_with_vagga():
    """Example 7: Get sections that have vagga information"""
    print("\n" + "="*60)
    print("Example 7: Sections with Vagga Information")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            chapter_id,
            section_number,
            vagga,
            vagga_english,
            pali_title,
            english_title
        FROM sections 
        WHERE vagga != '' AND vagga IS NOT NULL
        ORDER BY chapter_id, section_number
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"\n{row[0]} - Section {row[1]}")
        print(f"  Vagga:   {row[2]} ({row[3]})")
        if row[4]:
            print(f"  Title:   {row[4]}")
        if row[5]:
            print(f"           {row[5]}")
    
    conn.close()


def example_8_statistics():
    """Example 8: Get database statistics"""
    print("\n" + "="*60)
    print("Example 8: Database Statistics")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Count by table
    cursor.execute("SELECT COUNT(*) FROM nikayas")
    nikayas_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books")
    books_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chapters")
    chapters_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sections")
    sections_count = cursor.fetchone()[0]
    
    print(f"\nTotal Counts:")
    print(f"  Nikayas:  {nikayas_count}")
    print(f"  Books:    {books_count}")
    print(f"  Chapters: {chapters_count}")
    print(f"  Sections: {sections_count}")
    
    # Sections per nikaya
    cursor.execute("""
        SELECT 
            n.name_english,
            COUNT(s.id) as section_count
        FROM nikayas n
        JOIN books b ON n.id = b.nikaya_id
        JOIN chapters c ON b.id = c.book_id
        JOIN sections s ON c.id = s.chapter_id
        GROUP BY n.id, n.name_english
        ORDER BY section_count DESC
    """)
    
    print(f"\nSections per Nikaya:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} sections")
    
    conn.close()


def example_9_complete_sutta(chapter_id="sn.5.1", section_number=1):
    """Example 9: Get complete sutta in all languages"""
    print("\n" + "="*60)
    print(f"Example 9: Complete Sutta - {chapter_id} Section {section_number}")
    print("="*60)
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            s.pali_title,
            s.english_title,
            s.sinhala_title,
            s.vagga,
            s.vagga_english,
            s.vagga_sinhala,
            s.pali,
            s.english,
            s.sinhala
        FROM sections s
        WHERE s.chapter_id = ? AND s.section_number = ?
    """, (chapter_id, section_number))
    
    row = cursor.fetchone()
    if row:
        print(f"\n--- Titles ---")
        if row[0]:
            print(f"Pali:    {row[0]}")
        if row[1]:
            print(f"English: {row[1]}")
        if row[2]:
            print(f"Sinhala: {row[2]}")
        
        if row[3]:
            print(f"\n--- Vagga ---")
            print(f"Pali:    {row[3]}")
            if row[4]:
                print(f"English: {row[4]}")
            if row[5]:
                print(f"Sinhala: {row[5]}")
        
        print(f"\n--- Pali Text ---")
        print(row[6][:500] + "..." if len(row[6]) > 500 else row[6])
        
        print(f"\n--- English Translation ---")
        print(row[7][:500] + "..." if len(row[7]) > 500 else row[7])
        
        print(f"\n--- Sinhala Translation ---")
        print(row[8][:500] + "..." if len(row[8]) > 500 else row[8])
    else:
        print(f"\nNo sutta found for {chapter_id} section {section_number}")
    
    conn.close()


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Turso Pali Tipitaka Database - Query Examples")
    print("="*60)
    
    if not TURSO_DB_URL or not TURSO_AUTH_TOKEN:
        print("\n❌ Error: Environment variables not set!")
        print("\nPlease set:")
        print("  TURSO_DB_URL=your_database_url")
        print("  TURSO_AUTH_TOKEN=your_auth_token")
        return
    
    try:
        # Run examples
        example_1_list_nikayas()
        example_2_books_in_nikaya("samyutta")
        example_3_chapters_in_book("Mahāvaggo")
        example_4_sections_in_chapter("sn.5.1", limit=2)
        example_5_search_pali_text("bhagavā", limit=3)
        example_6_search_english_text("meditation", limit=3)
        example_7_sections_with_vagga()
        example_8_statistics()
        example_9_complete_sutta("sn.5.1", 1)
        
        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
