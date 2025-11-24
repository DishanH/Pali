"""
Verify translations using alternative AI models (OpenAI, Anthropic, Cohere, etc.)
Compares Pali source with English/Sinhala translations to check accuracy
"""

import sys
import os
import json
import time
from typing import Dict, List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


# ============================================================================
# Configuration for different AI providers
# ============================================================================

PROVIDERS = {
    'openai': {
        'name': 'OpenAI (ChatGPT)',
        'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        'api_key_env': 'OPENAI_API_KEY',
        'install': 'pip install openai'
    },
    'anthropic': {
        'name': 'Anthropic (Claude)',
        'models': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
        'api_key_env': 'ANTHROPIC_API_KEY',
        'install': 'pip install anthropic'
    },
    'cohere': {
        'name': 'Cohere',
        'models': ['command-r-plus', 'command-r', 'command'],
        'api_key_env': 'COHERE_API_KEY',
        'install': 'pip install cohere'
    },
    'mistral': {
        'name': 'Mistral AI',
        'models': ['mistral-large-latest', 'mistral-medium-latest'],
        'api_key_env': 'MISTRAL_API_KEY',
        'install': 'pip install mistralai'
    }
}


class TranslationVerifier:
    """Verify translations using different AI providers"""
    
    def __init__(self, provider='openai', model=None, api_key=None):
        """
        Initialize verifier with specified provider
        
        Args:
            provider: 'openai', 'anthropic', 'cohere', or 'mistral'
            model: Specific model name (uses default if None)
            api_key: API key (reads from env if None)
        """
        self.provider = provider
        
        if provider not in PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}. Choose from: {list(PROVIDERS.keys())}")
        
        self.provider_info = PROVIDERS[provider]
        self.model = model or self.provider_info['models'][0]
        
        # Get API key
        if not api_key:
            api_key = os.getenv(self.provider_info['api_key_env'])
        
        if not api_key:
            raise ValueError(
                f"No API key provided. Set {self.provider_info['api_key_env']} environment variable "
                f"or pass api_key parameter"
            )
        
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the API client based on provider"""
        try:
            if self.provider == 'openai':
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            
            elif self.provider == 'anthropic':
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            
            elif self.provider == 'cohere':
                import cohere
                self.client = cohere.Client(api_key=self.api_key)
            
            elif self.provider == 'mistral':
                from mistralai.client import MistralClient
                self.client = MistralClient(api_key=self.api_key)
            
            print(f"✓ Initialized {self.provider_info['name']} with model: {self.model}")
            
        except ImportError as e:
            print(f"\n❌ Error: {self.provider_info['name']} package not installed")
            print(f"   Install with: {self.provider_info['install']}")
            raise
    
    def verify_translation(self, pali_text: str, translation: str, target_language: str) -> Dict:
        """
        Verify a translation against the original Pali text
        
        Args:
            pali_text: Original Pali text
            translation: Translation to verify
            target_language: 'English' or 'Sinhala'
        
        Returns:
            Dict with verification results
        """
        prompt = f"""You are an expert in Pali Buddhist texts and translation verification.

Task: Verify the accuracy of a {target_language} translation of a Pali Buddhist text.

Original Pali Text:
{pali_text}

{target_language} Translation:
{translation}

Please analyze and provide:
1. **Accuracy Score** (1-10): How accurately does the translation convey the original meaning?
2. **Issues Found**: List any mistranslations, omissions, or additions
3. **Terminology Check**: Are Buddhist terms (dhamma, karma, nibbana, etc.) translated correctly?
4. **Completeness**: Is the translation complete? Any missing parts?
5. **Recommendation**: PASS, REVIEW, or FAIL

Respond in this exact format:
SCORE: [1-10]
ISSUES: [list of issues, or "None"]
TERMINOLOGY: [correct/incorrect with details]
COMPLETENESS: [complete/incomplete with details]
RECOMMENDATION: [PASS/REVIEW/FAIL]
EXPLANATION: [brief explanation]
"""
        
        try:
            response_text = self._call_api(prompt)
            result = self._parse_verification_response(response_text)
            result['raw_response'] = response_text
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'score': 0,
                'recommendation': 'ERROR'
            }
    
    def _call_api(self, prompt: str) -> str:
        """Call the appropriate API based on provider"""
        
        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        
        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif self.provider == 'cohere':
            response = self.client.chat(
                model=self.model,
                message=prompt,
                temperature=0.3
            )
            return response.text
        
        elif self.provider == 'mistral':
            from mistralai.models.chat_completion import ChatMessage
            response = self.client.chat(
                model=self.model,
                messages=[ChatMessage(role="user", content=prompt)]
            )
            return response.choices[0].message.content
    
    def _parse_verification_response(self, response: str) -> Dict:
        """Parse the verification response"""
        result = {
            'score': 0,
            'issues': [],
            'terminology': 'Unknown',
            'completeness': 'Unknown',
            'recommendation': 'UNKNOWN',
            'explanation': ''
        }
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('SCORE:'):
                try:
                    result['score'] = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            
            elif line.startswith('ISSUES:'):
                issues_text = line.split(':', 1)[1].strip()
                if issues_text.lower() != 'none':
                    result['issues'] = [issues_text]
            
            elif line.startswith('TERMINOLOGY:'):
                result['terminology'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('COMPLETENESS:'):
                result['completeness'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('RECOMMENDATION:'):
                result['recommendation'] = line.split(':')[1].strip().upper()
            
            elif line.startswith('EXPLANATION:'):
                result['explanation'] = line.split(':', 1)[1].strip()
        
        return result


def verify_chapter_json(json_file: str, provider='openai', model=None, api_key=None):
    """
    Verify all translations in a chapter JSON file
    
    Args:
        json_file: Path to chapter JSON file
        provider: AI provider to use
        model: Specific model (optional)
        api_key: API key (optional, reads from env)
    """
    print(f"\n📖 Verifying: {json_file}")
    print("=" * 60)
    
    # Initialize verifier
    try:
        verifier = TranslationVerifier(provider, model, api_key)
    except Exception as e:
        print(f"❌ Failed to initialize verifier: {e}")
        return
    
    # Load JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Verify each section
    sections = data.get('sections', [])
    print(f"\n📊 Verifying {len(sections)} sections...\n")
    
    results = []
    
    for i, section in enumerate(sections, 1):
        section_num = section.get('number', i)
        pali_text = section.get('pali', '')
        
        if not pali_text:
            continue
        
        print(f"\n[{i}/{len(sections)}] Section {section_num}")
        print("-" * 60)
        
        # Verify English
        english_text = section.get('english', '')
        if english_text:
            print("  🇬🇧 Verifying English...", end='', flush=True)
            english_result = verifier.verify_translation(pali_text, english_text, 'English')
            print(f" Score: {english_result['score']}/10 - {english_result['recommendation']}")
            
            if english_result['issues']:
                print(f"     Issues: {english_result['issues'][0][:80]}...")
            
            results.append({
                'section': section_num,
                'language': 'English',
                **english_result
            })
            
            time.sleep(1)  # Rate limiting
        
        # Verify Sinhala
        sinhala_text = section.get('sinhala', '')
        if sinhala_text:
            print("  🇱🇰 Verifying Sinhala...", end='', flush=True)
            sinhala_result = verifier.verify_translation(pali_text, sinhala_text, 'Sinhala')
            print(f" Score: {sinhala_result['score']}/10 - {sinhala_result['recommendation']}")
            
            if sinhala_result['issues']:
                print(f"     Issues: {sinhala_result['issues'][0][:80]}...")
            
            results.append({
                'section': section_num,
                'language': 'Sinhala',
                **sinhala_result
            })
            
            time.sleep(1)  # Rate limiting
    
    # Generate report
    generate_report(results, json_file)


def generate_report(results: List[Dict], json_file: str):
    """Generate verification report"""
    print("\n" + "=" * 60)
    print("📊 VERIFICATION REPORT")
    print("=" * 60)
    
    if not results:
        print("No results to report")
        return
    
    # Calculate statistics
    total = len(results)
    english_results = [r for r in results if r['language'] == 'English']
    sinhala_results = [r for r in results if r['language'] == 'Sinhala']
    
    avg_score = sum(r['score'] for r in results) / total if total > 0 else 0
    
    pass_count = sum(1 for r in results if r['recommendation'] == 'PASS')
    review_count = sum(1 for r in results if r['recommendation'] == 'REVIEW')
    fail_count = sum(1 for r in results if r['recommendation'] == 'FAIL')
    
    print(f"\n📈 Overall Statistics:")
    print(f"   Total sections verified: {total // 2}")  # Divide by 2 (English + Sinhala)
    print(f"   Average score: {avg_score:.1f}/10")
    print(f"   ✅ PASS: {pass_count}")
    print(f"   ⚠️  REVIEW: {review_count}")
    print(f"   ❌ FAIL: {fail_count}")
    
    if english_results:
        eng_avg = sum(r['score'] for r in english_results) / len(english_results)
        print(f"\n🇬🇧 English average: {eng_avg:.1f}/10")
    
    if sinhala_results:
        sin_avg = sum(r['score'] for r in sinhala_results) / len(sinhala_results)
        print(f"🇱🇰 Sinhala average: {sin_avg:.1f}/10")
    
    # List sections needing review
    need_review = [r for r in results if r['recommendation'] in ['REVIEW', 'FAIL']]
    if need_review:
        print(f"\n⚠️  Sections needing review:")
        for r in need_review:
            print(f"   - Section {r['section']} ({r['language']}): Score {r['score']}/10")
            if r['issues']:
                print(f"     Issue: {r['issues'][0][:60]}...")
    
    # Save detailed report
    report_file = json_file.replace('.json', '_verification_report.json')
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'file': json_file,
                'total_sections': total // 2,
                'average_score': avg_score,
                'pass_count': pass_count,
                'review_count': review_count,
                'fail_count': fail_count,
                'details': results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Verify translations using alternative AI models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Available Providers:
{chr(10).join(f"  - {k}: {v['name']}" for k, v in PROVIDERS.items())}

Examples:
  # Verify with OpenAI GPT-4
  python verify_translations.py Pāthikavaggapāḷi/chapters/dn3-Cakkavattisuttaṃ.json --provider openai
  
  # Verify with Claude
  python verify_translations.py input.json --provider anthropic --model claude-3-opus-20240229
  
  # Verify with Cohere
  python verify_translations.py input.json --provider cohere

Environment Variables (set your API key):
{chr(10).join(f"  {v['api_key_env']}" for v in PROVIDERS.values())}
        '''
    )
    
    parser.add_argument('file', help='Chapter JSON file to verify')
    parser.add_argument('--provider', default='openai', choices=list(PROVIDERS.keys()),
                       help='AI provider to use (default: openai)')
    parser.add_argument('--model', help='Specific model name (optional)')
    parser.add_argument('--api-key', help='API key (reads from env if not provided)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 Translation Verification Tool")
    print("=" * 60)
    
    if not os.path.exists(args.file):
        print(f"\n❌ File not found: {args.file}")
        return 1
    
    verify_chapter_json(args.file, args.provider, args.model, args.api_key)
    
    print("\n" + "=" * 60)
    print("✅ Verification complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

