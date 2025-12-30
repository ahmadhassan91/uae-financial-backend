"""
Asset Helper Utility
Functions to handle asset URLs and sync S3 assets to local static folder
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional
from app.config import settings

class AssetHelper:
    """Helper class for managing assets (local and S3)"""
    
    def __init__(self):
        self.static_dir = Path(__file__).parent.parent / "static"
        self.base_url = getattr(settings, 'BASE_URL', 'https://uae-financial-health-filters-68ab0c8434cb.herokuapp.com')
        self.use_local_assets = getattr(settings, 'USE_LOCAL_ASSETS', True)
    
    def get_asset_url(self, asset_path: str) -> str:
        """Get URL for an asset, preferring local static if available"""
        if self.use_local_assets:
            # Check if asset exists locally
            local_path = self.static_dir / asset_path
            if local_path.exists():
                return f"{self.base_url}/static/{asset_path}"
        
        # Fallback to S3 URL
        return f"https://financial-clinic.s3.amazonaws.com/{asset_path}"
    
    def replace_s3_urls_with_local(self, content: str) -> str:
        """Replace all S3 URLs with local static URLs in content"""
        if not self.use_local_assets:
            return content
        
        # Pattern to match S3 URLs
        s3_pattern = r'https://financial-clinic\.s3\.amazonaws\.com/([^"\'\s]+)'
        
        def replace_url(match):
            asset_path = match.group(1)
            return self.get_asset_url(asset_path)
        
        # Replace all S3 URLs
        content = re.sub(s3_pattern, replace_url, content)
        
        return content
    
    def get_available_assets(self) -> Dict[str, str]:
        """Get list of available local assets and their URLs"""
        assets = {}
        
        if not self.static_dir.exists():
            return assets
        
        for root, dirs, files in os.walk(self.static_dir):
            for file in files:
                # Skip hidden files and manifest
                if file.startswith('.') or file == 'asset_manifest.json':
                    continue
                
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.static_dir)
                asset_path = str(relative_path).replace('\\', '/')  # Ensure forward slashes
                
                assets[asset_path] = self.get_asset_url(asset_path)
        
        return assets
    
    def sync_s3_to_local(self) -> bool:
        """Sync S3 assets to local static folder"""
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append(str(Path(__file__).parent.parent.parent / "scripts" / "maintenance"))
            from sync_assets import AssetSyncer
            
            syncer = AssetSyncer()
            return syncer.sync_assets()
        except Exception as e:
            print(f"Error syncing assets: {e}")
            return False

# Global instance
asset_helper = AssetHelper()

def get_asset_url(asset_path: str) -> str:
    """Get URL for an asset"""
    return asset_helper.get_asset_url(asset_path)

def replace_s3_urls_with_local(content: str) -> str:
    """Replace all S3 URLs with local static URLs"""
    return asset_helper.replace_s3_urls_with_local(content)
