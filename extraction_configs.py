"""
Configuration Examples for extract_pali_pdf.py
Shows how to configure the extraction script for different Dīgha Nikāya books
"""

# Example 1: Sīlakkhandhavaggapāḷi (DN 1-13)
SILAKKHANDHAVAGGA_CONFIG = {
    'name': 'Sīlakkhandhavaggapāḷi',
    'pali_title': 'Sīlakkhandhavaggapāḷi',
    'english_title': 'The Division of the Moral Precepts',
    'sinhala_title': '',
    'starting_dn': 1,              # Starts with DN 1
    'chapters': [],                # Auto-detect chapters
    'renumber_sections': True      # Renumber sections from 1 per chapter
}

# Example 2: Mahāvaggapāḷi (DN 14-23)
MAHAVAGGA_CONFIG = {
    'name': 'Mahāvaggapāḷi',
    'pali_title': 'Mahāvaggapāḷi',
    'english_title': 'The Great Division',
    'sinhala_title': '',
    'starting_dn': 14,             # Starts with DN 14
    'chapters': [],                # Auto-detect (DN 14, 15, 16)
    'renumber_sections': False     # Keep original continuous numbering
}

# Example 3: Pāthikavaggapāḷi (DN 24-34)
PATHIKAVAGGA_CONFIG = {
    'name': 'Pāthikavaggapāḷi',
    'pali_title': 'Pāthikavaggapāḷi',
    'english_title': 'The Pāthika Division',
    'sinhala_title': '',
    'starting_dn': 24,             # Starts with DN 24
    'chapters': [],                # Auto-detect
    'renumber_sections': True
}

# Example 4: Custom chapter configuration (if auto-detection doesn't work)
CUSTOM_CONFIG = {
    'name': 'CustomBook',
    'pali_title': 'CustomBook',
    'english_title': 'Custom Book Title',
    'sinhala_title': '',
    'starting_dn': 1,
    'chapters': [                  # Manually specify chapters
        {
            'id': 'dn1',
            'number': 1,
            'title': 'Brahmajālasuttaṃ',
            'dn_number': 1
        },
        {
            'id': 'dn2',
            'number': 2,
            'title': 'Sāmaññaphalasuttaṃ',
            'dn_number': 2
        },
        # ... more chapters
    ],
    'renumber_sections': True
}


def extract_with_config(pdf_path: str, output_dir: str, config: dict):
    """
    Helper function to run extraction with a specific configuration
    
    Usage:
        extract_with_config(
            "pdfs/Sīlakkhandhavaggapāḷi.pdf",
            "Sīlakkhandhavaggapāḷi",
            SILAKKHANDHAVAGGA_CONFIG
        )
    """
    import os
    import sys
    
    # Add parent directory to path to import the extractor
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from extract_pali_pdf import PaliPDFExtractor
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return
    
    # Create extractor and process
    extractor = PaliPDFExtractor(pdf_path, output_dir, config)
    extractor.process()


# Example usage in a script:
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python extraction_configs.py <config_name>")
        print("\nAvailable configs:")
        print("  silakkhandha - Sīlakkhandhavaggapāḷi (DN 1-13)")
        print("  mahavagga    - Mahāvaggapāḷi (DN 14-23)")
        print("  pathika      - Pāthikavaggapāḷi (DN 24-34)")
        sys.exit(1)
    
    config_name = sys.argv[1].lower()
    
    configs = {
        'silakkhandha': (SILAKKHANDHAVAGGA_CONFIG, 'pdfs/Sīlakkhandhavaggapāḷi.pdf', 'Sīlakkhandhavaggapāḷi'),
        'mahavagga': (MAHAVAGGA_CONFIG, 'pdfs/Mahāvaggapāḷi.pdf', 'Mahāvaggapāḷi'),
        'pathika': (PATHIKAVAGGA_CONFIG, 'pdfs/Pāthikavaggapāḷi.pdf', 'Pāthikavaggapāḷi'),
    }
    
    if config_name not in configs:
        print(f"❌ Unknown config: {config_name}")
        print("Available configs: silakkhandha, mahavagga, pathika")
        sys.exit(1)
    
    config, pdf_path, output_dir = configs[config_name]
    extract_with_config(pdf_path, output_dir, config)

