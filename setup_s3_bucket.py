"""Automated S3 bucket configuration script."""
import sys
import os
import json
import boto3
from botocore.exceptions import ClientError

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings


def configure_bucket_policy():
    """Configure bucket policy to allow public read access."""
    print("=" * 60)
    print("Configuring Bucket Policy")
    print("=" * 60)
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    # Bucket policy for public read access
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{settings.AWS_S3_BUCKET}/*"
            }
        ]
    }
    
    try:
        s3.put_bucket_policy(
            Bucket=settings.AWS_S3_BUCKET,
            Policy=json.dumps(bucket_policy)
        )
        print(f"✅ Bucket policy configured successfully!")
        print(f"   Public read access enabled for: {settings.AWS_S3_BUCKET}")
        return True
    except ClientError as e:
        print(f"❌ Failed to set bucket policy: {e}")
        return False


def disable_public_access_block():
    """Disable public access block settings."""
    print("\n" + "=" * 60)
    print("Disabling Public Access Block")
    print("=" * 60)
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    try:
        s3.delete_public_access_block(Bucket=settings.AWS_S3_BUCKET)
        print("✅ Public access block disabled!")
        print("   Bucket can now serve public files")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchPublicAccessBlockConfiguration':
            print("✅ Public access block already disabled")
            return True
        else:
            print(f"❌ Failed to disable public access block: {e}")
            return False


def enable_bucket_versioning():
    """Enable versioning for backup (optional but recommended)."""
    print("\n" + "=" * 60)
    print("Enabling Bucket Versioning (Optional)")
    print("=" * 60)
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    try:
        s3.put_bucket_versioning(
            Bucket=settings.AWS_S3_BUCKET,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print("✅ Bucket versioning enabled!")
        print("   Old versions of files will be kept for recovery")
        return True
    except ClientError as e:
        print(f"⚠️  Could not enable versioning: {e}")
        print("   This is optional - bucket will still work")
        return False


def test_upload():
    """Test uploading a file to verify configuration."""
    print("\n" + "=" * 60)
    print("Testing Upload")
    print("=" * 60)
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    test_key = "test/setup_test.txt"
    test_content = b"S3 bucket setup successful!"
    
    try:
        # Upload test file
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print(f"✅ Test file uploaded successfully!")
        
        # Generate public URL
        public_url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{test_key}"
        print(f"   Public URL: {public_url}")
        
        # Test if file is publicly accessible
        import requests
        response = requests.get(public_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ File is publicly accessible!")
            print(f"   Content: {response.text}")
        else:
            print(f"⚠️  File uploaded but not publicly accessible (status: {response.status_code})")
            print(f"   You may need to manually configure bucket permissions")
        
        # Clean up test file
        s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=test_key)
        print(f"✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False


def main():
    """Run automated S3 bucket setup."""
    print("\n🚀 AWS S3 Bucket Automated Setup\n")
    
    print(f"Configuration:")
    print(f"  Bucket: {settings.AWS_S3_BUCKET}")
    print(f"  Region: {settings.AWS_REGION}")
    print(f"  Account: Using root credentials")
    print()
    
    # Step 1: Disable public access block
    step1 = disable_public_access_block()
    
    # Step 2: Configure bucket policy
    step2 = configure_bucket_policy()
    
    # Step 3: Enable versioning (optional)
    step3 = enable_bucket_versioning()
    
    # Step 4: Test upload
    step4 = test_upload()
    
    # Summary
    print("\n" + "=" * 60)
    print("Setup Summary")
    print("=" * 60)
    
    results = {
        "Public Access Block Disabled": step1,
        "Bucket Policy Configured": step2,
        "Versioning Enabled": step3,
        "Upload Test": step4
    }
    
    for task, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {task}")
    
    if step1 and step2 and step4:
        print("\n🎉 SUCCESS! Your S3 bucket is ready to use!")
        print("\nNext steps:")
        print("  1. Run: python3 test_s3_integration.py")
        print("  2. Your PDFs will now automatically upload to S3")
        print(f"  3. Public URL format: https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/reports/...")
    else:
        print("\n⚠️  Some steps failed. Please check the errors above.")
        print("\nYou may need to:")
        print("  1. Check your AWS credentials have sufficient permissions")
        print("  2. Manually configure bucket settings in AWS Console")
        print("  3. See docs/AWS_S3_SETUP.md for manual setup instructions")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
