"""
API Key Manager with Automatic Rotation
Manages multiple Google Generative AI API keys and switches when quota is near
"""

import os
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages multiple API keys with automatic rotation based on usage"""
    
    def __init__(self, 
                 max_requests_per_key: int = 220,
                 total_quota_per_key: int = 250,
                 warning_threshold: int = 200,
                 state_file: str = 'api_key_state.json'):
        """
        Initialize API Key Manager
        
        Args:
            max_requests_per_key: Maximum requests before switching keys (default: 220)
            total_quota_per_key: Total quota limit per key (default: 250)
            warning_threshold: When to warn about approaching limit (default: 200)
            state_file: File to persist key usage state
        """
        self.max_requests_per_key = max_requests_per_key
        self.total_quota_per_key = total_quota_per_key
        self.warning_threshold = warning_threshold
        self.state_file = state_file
        
        # Load API keys from environment
        self.api_keys = self._load_api_keys()
        
        if not self.api_keys:
            raise ValueError("No API keys found. Set GOOGLE_API_KEY_1, GOOGLE_API_KEY_2, etc. in .env file")
        
        # Load or initialize state
        self.state = self._load_state()
        
        # Set current key
        self.current_key_index = self.state.get('current_key_index', 0)
        self.request_count = self.state.get('request_count', 0)
        
        logger.info(f"API Key Manager initialized with {len(self.api_keys)} keys")
        logger.info(f"Current key: #{self.current_key_index + 1}, Requests: {self.request_count}/{self.max_requests_per_key}")
    
    def _load_api_keys(self) -> List[str]:
        """Load all API keys from environment variables"""
        keys = []
        index = 1
        
        while True:
            key = os.getenv(f'GOOGLE_API_KEY_{index}', '').strip()
            if not key:
                # Also check for single GOOGLE_API_KEY
                if index == 1:
                    key = os.getenv('GOOGLE_API_KEY', '').strip()
                    if key:
                        keys.append(key)
                break
            keys.append(key)
            index += 1
        
        return keys
    
    def _load_state(self) -> Dict:
        """Load state from file"""
        if not os.path.exists(self.state_file):
            return {
                'current_key_index': 0,
                'request_count': 0,
                'key_usage': {},
                'last_reset': datetime.now().isoformat()
            }
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load state file: {e}. Starting fresh.")
            return {
                'current_key_index': 0,
                'request_count': 0,
                'key_usage': {},
                'last_reset': datetime.now().isoformat()
            }
    
    def _save_state(self):
        """Save current state to file"""
        self.state['current_key_index'] = self.current_key_index
        self.state['request_count'] = self.request_count
        self.state['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get_current_key(self) -> str:
        """Get the current active API key"""
        return self.api_keys[self.current_key_index]
    
    def increment_request_count(self):
        """Increment request count and check if key rotation is needed"""
        self.request_count += 1
        
        # Update key usage stats
        key_id = f"key_{self.current_key_index + 1}"
        if key_id not in self.state.get('key_usage', {}):
            self.state['key_usage'] = self.state.get('key_usage', {})
            self.state['key_usage'][key_id] = 0
        self.state['key_usage'][key_id] += 1
        
        # Save state periodically
        if self.request_count % 10 == 0:
            self._save_state()
        
        # Check thresholds
        if self.request_count >= self.warning_threshold and self.request_count < self.max_requests_per_key:
            remaining = self.max_requests_per_key - self.request_count
            logger.warning(f"⚠️  Approaching quota limit: {self.request_count}/{self.max_requests_per_key} ({remaining} requests remaining)")
            print(f"\n⚠️  Warning: {remaining} requests remaining on current API key")
        
        # Auto-rotate if limit reached
        if self.request_count >= self.max_requests_per_key:
            self.rotate_key()
    
    def rotate_key(self, force: bool = False):
        """
        Rotate to the next API key
        
        Args:
            force: Force rotation even if quota not reached
        """
        if len(self.api_keys) == 1:
            logger.warning("Only one API key available. Cannot rotate.")
            print("\n⚠️  Warning: Only one API key configured. Consider adding more keys.")
            return
        
        old_index = self.current_key_index
        old_count = self.request_count
        
        # Move to next key
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.request_count = 0
        
        self._save_state()
        
        logger.info(f"🔄 Rotated API key: #{old_index + 1} → #{self.current_key_index + 1}")
        logger.info(f"Previous key usage: {old_count} requests")
        
        print(f"\n{'='*60}")
        print(f"🔄 API KEY ROTATED")
        print(f"{'='*60}")
        print(f"Previous Key: #{old_index + 1} ({old_count} requests)")
        print(f"New Key: #{self.current_key_index + 1}")
        print(f"Remaining Keys: {len(self.api_keys) - self.current_key_index - 1}")
        print(f"{'='*60}\n")
    
    def get_status(self) -> Dict:
        """Get current status of all API keys"""
        return {
            'total_keys': len(self.api_keys),
            'current_key': self.current_key_index + 1,
            'current_requests': self.request_count,
            'max_requests': self.max_requests_per_key,
            'remaining_requests': self.max_requests_per_key - self.request_count,
            'remaining_keys': len(self.api_keys) - self.current_key_index - 1,
            'key_usage': self.state.get('key_usage', {}),
            'percentage_used': round((self.request_count / self.max_requests_per_key) * 100, 1)
        }
    
    def print_status(self):
        """Print current status"""
        status = self.get_status()
        
        print(f"\n{'='*60}")
        print(f"API KEY STATUS")
        print(f"{'='*60}")
        print(f"Total Keys: {status['total_keys']}")
        print(f"Current Key: #{status['current_key']}")
        print(f"Requests: {status['current_requests']}/{status['max_requests']} ({status['percentage_used']}%)")
        print(f"Remaining: {status['remaining_requests']} requests")
        print(f"Unused Keys: {status['remaining_keys']}")
        
        if status['key_usage']:
            print(f"\nUsage History:")
            for key_id, count in status['key_usage'].items():
                print(f"  {key_id}: {count} requests")
        
        print(f"{'='*60}\n")
    
    def reset_state(self):
        """Reset state (useful for testing or new day)"""
        self.current_key_index = 0
        self.request_count = 0
        self.state = {
            'current_key_index': 0,
            'request_count': 0,
            'key_usage': {},
            'last_reset': datetime.now().isoformat()
        }
        self._save_state()
        logger.info("API key state reset")
        print("✓ API key state reset to beginning")
    
    def manual_switch(self, key_index: int):
        """
        Manually switch to a specific key
        
        Args:
            key_index: 1-based index of the key to switch to
        """
        if key_index < 1 or key_index > len(self.api_keys):
            raise ValueError(f"Invalid key index. Must be between 1 and {len(self.api_keys)}")
        
        self.current_key_index = key_index - 1
        self.request_count = 0
        self._save_state()
        
        logger.info(f"Manually switched to API key #{key_index}")
        print(f"✓ Switched to API key #{key_index}")


def load_env_file(env_path: str = '.env'):
    """
    Load environment variables from .env file
    
    Args:
        env_path: Path to .env file
    """
    if not os.path.exists(env_path):
        logger.warning(f".env file not found at {env_path}")
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Set environment variable if not already set
                    if key and not os.getenv(key):
                        os.environ[key] = value
        
        logger.info(f"Loaded environment variables from {env_path}")
    except Exception as e:
        logger.error(f"Failed to load .env file: {e}")


# Convenience function for quick setup
def create_key_manager_from_env(env_path: str = '.env') -> APIKeyManager:
    """
    Create APIKeyManager from .env file
    
    Args:
        env_path: Path to .env file
    
    Returns:
        Configured APIKeyManager instance
    """
    # Load .env file
    load_env_file(env_path)
    
    # Get configuration from environment
    max_requests = int(os.getenv('MAX_REQUESTS_PER_KEY', '220'))
    total_quota = int(os.getenv('TOTAL_QUOTA_PER_KEY', '250'))
    warning_threshold = int(os.getenv('QUOTA_WARNING_THRESHOLD', '200'))
    
    return APIKeyManager(
        max_requests_per_key=max_requests,
        total_quota_per_key=total_quota,
        warning_threshold=warning_threshold
    )


if __name__ == "__main__":
    """Test the API Key Manager"""
    print("API Key Manager Test")
    print("=" * 60)
    
    # Load from .env
    load_env_file('.env')
    
    try:
        manager = create_key_manager_from_env()
        manager.print_status()
        
        # Simulate some requests
        print("\nSimulating 5 requests...")
        for i in range(5):
            manager.increment_request_count()
            print(f"  Request {i+1}: Key #{manager.current_key_index + 1}, Count: {manager.request_count}")
        
        manager.print_status()
        
    except Exception as e:
        print(f"Error: {e}")



