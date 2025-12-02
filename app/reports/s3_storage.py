"""AWS S3 storage service for PDF reports."""
import boto3
import logging
from typing import Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

from app.config import settings


logger = logging.getLogger(__name__)


class S3StorageService:
    """Service for storing and retrieving PDF reports from AWS S3."""
    
    def __init__(self):
        """Initialize S3 client."""
        self.use_s3 = settings.USE_S3_STORAGE
        
        if self.use_s3:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                self.bucket_name = settings.AWS_S3_BUCKET
                logger.info(f"✅ S3 client initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize S3 client: {e}")
                self.use_s3 = False
                self.s3_client = None
        else:
            self.s3_client = None
            logger.info("📁 Using local file storage (S3 disabled)")
    
    def upload_pdf(
        self,
        pdf_content: bytes,
        file_key: str,
        metadata: Optional[dict] = None
    ) -> Optional[str]:
        """
        Upload PDF to S3 and return the public URL.
        
        Args:
            pdf_content: PDF file content as bytes
            file_key: S3 object key (filename with path)
            metadata: Optional metadata to attach to the file
            
        Returns:
            Public URL of the uploaded file, or None if upload fails
        """
        if not self.use_s3 or not self.s3_client:
            logger.warning("S3 storage not enabled, skipping upload")
            return None
        
        try:
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': file_key,
                'Body': pdf_content,
                'ContentType': 'application/pdf'
                # Note: ACL removed - bucket uses bucket policy for public access
            }
            
            # Add metadata if provided
            if metadata:
                upload_params['Metadata'] = {
                    k: str(v) for k, v in metadata.items()
                }
            
            # Upload to S3
            self.s3_client.put_object(**upload_params)
            
            # Generate public URL
            public_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
            
            logger.info(f"✅ PDF uploaded to S3: {file_key}")
            return public_url
            
        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error during S3 upload: {e}")
            return None
    
    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate a presigned URL for temporary access to a private file.
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL or None if generation fails
        """
        if not self.use_s3 or not self.s3_client:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"✅ Generated presigned URL for: {file_key}")
            return url
            
        except ClientError as e:
            logger.error(f"❌ Failed to generate presigned URL: {e}")
            return None
    
    def delete_pdf(self, file_key: str) -> bool:
        """
        Delete a PDF from S3.
        
        Args:
            file_key: S3 object key to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.use_s3 or not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"✅ Deleted PDF from S3: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Failed to delete from S3: {e}")
            return False
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            file_key: S3 object key to check
            
        Returns:
            True if file exists, False otherwise
        """
        if not self.use_s3 or not self.s3_client:
            return False
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError:
            return False
    
    def list_pdfs(self, prefix: str = "reports/", max_keys: int = 100) -> list:
        """
        List PDFs in S3 bucket with given prefix.
        
        Args:
            prefix: S3 key prefix to filter results
            max_keys: Maximum number of keys to return
            
        Returns:
            List of file keys
        """
        if not self.use_s3 or not self.s3_client:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except ClientError as e:
            logger.error(f"❌ Failed to list S3 objects: {e}")
            return []
    
    def cleanup_old_files(self, prefix: str = "reports/", days_old: int = 90) -> int:
        """
        Delete files older than specified days.
        
        Args:
            prefix: S3 key prefix to filter results
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        if not self.use_s3 or not self.s3_client:
            return 0
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.delete_pdf(obj['Key'])
                        deleted_count += 1
            
            logger.info(f"✅ Cleaned up {deleted_count} old files from S3")
            return deleted_count
            
        except ClientError as e:
            logger.error(f"❌ Failed to cleanup S3 files: {e}")
            return 0


# Global instance
s3_storage = S3StorageService()
