"""NFS storage service for PDF reports (on-prem deployment)."""
import os
import logging
import shutil
from typing import Optional
from datetime import datetime

from app.config import settings


logger = logging.getLogger(__name__)


class NFSStorageService:
    """Service for storing and retrieving PDF reports from NFS mounted storage."""
    
    def __init__(self):
        """Initialize NFS storage paths."""
        self.use_nfs = settings.USE_NFS_STORAGE
        self.mount_path = settings.NFS_MOUNT_PATH
        self.reports_dir = os.path.join(self.mount_path, settings.NFS_REPORTS_SUBDIR)
        self.icons_dir = os.path.join(self.mount_path, settings.NFS_ICONS_SUBDIR)
        self.public_url_base = settings.NFS_PUBLIC_URL_BASE
        
        if self.use_nfs:
            self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure NFS directories exist."""
        try:
            # Check if mount path exists
            if not os.path.exists(self.mount_path):
                logger.warning(f"⚠️ NFS mount path does not exist: {self.mount_path}")
                logger.warning("   Make sure NFS share is mounted: mount -t nfs 192.168.125.35:/financialclinic /mnt/financialclinic")
                self.use_nfs = False
                return
            
            # Create subdirectories if they don't exist
            os.makedirs(self.reports_dir, exist_ok=True)
            os.makedirs(self.icons_dir, exist_ok=True)
            
            logger.info(f"✅ NFS storage initialized")
            logger.info(f"   Mount path: {self.mount_path}")
            logger.info(f"   Reports directory: {self.reports_dir}")
            logger.info(f"   Icons directory: {self.icons_dir}")
            
        except PermissionError as e:
            logger.error(f"❌ Permission denied accessing NFS path: {e}")
            self.use_nfs = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize NFS storage: {e}")
            self.use_nfs = False
    
    def is_available(self) -> bool:
        """Check if NFS storage is available and writable."""
        if not self.use_nfs:
            return False
        
        try:
            # Try to write a test file
            test_file = os.path.join(self.reports_dir, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except Exception as e:
            logger.warning(f"⚠️ NFS storage not writable: {e}")
            return False
    
    def upload_pdf(
        self,
        pdf_content: bytes,
        filename: str,
        metadata: Optional[dict] = None
    ) -> Optional[str]:
        """
        Save PDF to NFS storage and return the public URL.
        
        Args:
            pdf_content: PDF file content as bytes
            filename: Filename for the PDF
            metadata: Optional metadata (stored as .meta file)
            
        Returns:
            Public URL of the file, or None if save fails
        """
        if not self.use_nfs:
            logger.warning("NFS storage not enabled, skipping upload")
            return None
        
        try:
            # Full file path
            file_path = os.path.join(self.reports_dir, filename)
            
            # Write PDF file
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            
            # Write metadata if provided
            if metadata:
                meta_path = f"{file_path}.meta"
                with open(meta_path, 'w') as f:
                    import json
                    json.dump(metadata, f, indent=2, default=str)
            
            # Generate public URL
            if self.public_url_base:
                public_url = f"{self.public_url_base.rstrip('/')}/{settings.NFS_REPORTS_SUBDIR}/{filename}"
            else:
                # Fallback to API endpoint for serving files
                public_url = f"{settings.api_base_url}/api/v1/reports/download-nfs/{filename}"
            
            logger.info(f"✅ PDF saved to NFS: {file_path}")
            logger.info(f"   Public URL: {public_url}")
            
            return public_url
            
        except PermissionError as e:
            logger.error(f"❌ Permission denied writing to NFS: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to save PDF to NFS: {e}")
            return None
    
    def get_pdf(self, filename: str) -> Optional[bytes]:
        """
        Retrieve PDF content from NFS storage.
        
        Args:
            filename: Filename of the PDF
            
        Returns:
            PDF content as bytes, or None if not found
        """
        if not self.use_nfs:
            return None
        
        try:
            file_path = os.path.join(self.reports_dir, filename)
            
            if not os.path.exists(file_path):
                logger.warning(f"⚠️ PDF not found: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"❌ Failed to read PDF from NFS: {e}")
            return None
    
    def delete_pdf(self, filename: str) -> bool:
        """
        Delete PDF from NFS storage.
        
        Args:
            filename: Filename of the PDF to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.use_nfs:
            return False
        
        try:
            file_path = os.path.join(self.reports_dir, filename)
            meta_path = f"{file_path}.meta"
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if os.path.exists(meta_path):
                os.remove(meta_path)
            
            logger.info(f"✅ PDF deleted from NFS: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete PDF from NFS: {e}")
            return False
    
    def list_reports(self, prefix: str = "") -> list:
        """
        List PDF reports in NFS storage.
        
        Args:
            prefix: Optional filename prefix filter
            
        Returns:
            List of filenames
        """
        if not self.use_nfs:
            return []
        
        try:
            files = []
            for f in os.listdir(self.reports_dir):
                if f.endswith('.pdf') and f.startswith(prefix):
                    files.append(f)
            return sorted(files)
            
        except Exception as e:
            logger.error(f"❌ Failed to list NFS reports: {e}")
            return []
    
    def get_icon_url(self, icon_name: str) -> str:
        """
        Get the URL for a static icon from NFS storage.
        
        Args:
            icon_name: Name of the icon file (e.g., 'logo.png')
            
        Returns:
            Public URL for the icon
        """
        if self.public_url_base:
            return f"{self.public_url_base.rstrip('/')}/{settings.NFS_ICONS_SUBDIR}/{icon_name}"
        else:
            # Fallback to API endpoint
            return f"{settings.api_base_url}/api/v1/static/icons/{icon_name}"
    
    def cleanup_old_reports(self, days_old: int = 30) -> int:
        """
        Delete PDF reports older than specified days.
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        if not self.use_nfs:
            return 0
        
        try:
            import time
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for filename in os.listdir(self.reports_dir):
                file_path = os.path.join(self.reports_dir, filename)
                
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted old report: {filename}")
            
            logger.info(f"✅ Cleanup complete: {deleted_count} old reports deleted")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old reports: {e}")
            return 0


# Global instance
nfs_storage = NFSStorageService()
