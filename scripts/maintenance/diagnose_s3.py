"""Diagnostic script for S3 access issues."""
import sys
import os
import boto3
from botocore.exceptions import ClientError

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import settings


def test_credentials():
    """Test if AWS credentials are valid."""
    print("=" * 60)
    print("Testing AWS Credentials")
    print("=" * 60)
    
    try:
        sts = boto3.client(
            'sts',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        identity = sts.get_caller_identity()
        print(f"✅ Credentials are valid!")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        print(f"   User ID: {identity['UserId']}")
        return True
        
    except ClientError as e:
        print(f"❌ Invalid credentials: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_bucket_exists():
    """Test if the S3 bucket exists and is accessible."""
    print("\n" + "=" * 60)
    print("Testing Bucket Existence")
    print("=" * 60)
    
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Try to get bucket location
        response = s3.get_bucket_location(Bucket=settings.AWS_S3_BUCKET)
        location = response['LocationConstraint'] or 'us-east-1'
        
        print(f"✅ Bucket exists: {settings.AWS_S3_BUCKET}")
        print(f"   Region: {location}")
        
        if location != settings.AWS_REGION:
            print(f"⚠️  WARNING: Bucket is in {location} but config says {settings.AWS_REGION}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket does not exist: {settings.AWS_S3_BUCKET}")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to bucket: {settings.AWS_S3_BUCKET}")
            print("   The bucket might exist but you don't have permission to access it")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_bucket_permissions():
    """Test what permissions the user has on the bucket."""
    print("\n" + "=" * 60)
    print("Testing Bucket Permissions")
    print("=" * 60)
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    permissions = {
        'ListBucket': False,
        'GetObject': False,
        'PutObject': False,
        'DeleteObject': False
    }
    
    # Test ListBucket
    try:
        s3.list_objects_v2(Bucket=settings.AWS_S3_BUCKET, MaxKeys=1)
        permissions['ListBucket'] = True
        print("✅ ListBucket: Allowed")
    except ClientError as e:
        print(f"❌ ListBucket: Denied - {e.response['Error']['Code']}")
    
    # Test PutObject
    try:
        test_key = "test/permission_test.txt"
        s3.put_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=test_key,
            Body=b"test"
            # ACL removed - bucket uses bucket policy for public access
        )
        permissions['PutObject'] = True
        print("✅ PutObject: Allowed")
        
        # Clean up test file
        try:
            s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=test_key)
            permissions['DeleteObject'] = True
            print("✅ DeleteObject: Allowed")
        except:
            print("⚠️  DeleteObject: Unable to test")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ PutObject: Denied - {error_code}")
        if error_code == 'AccessDenied':
            print("   This is the main issue! User needs PutObject permission")
    
    return permissions


def list_user_policies():
    """List IAM policies attached to the user."""
    print("\n" + "=" * 60)
    print("Checking IAM User Policies")
    print("=" * 60)
    
    try:
        iam = boto3.client(
            'iam',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Get user name from credentials
        sts = boto3.client(
            'sts',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        identity = sts.get_caller_identity()
        user_name = identity['Arn'].split('/')[-1]
        
        print(f"User: {user_name}")
        
        # List attached policies
        response = iam.list_attached_user_policies(UserName=user_name)
        if response['AttachedPolicies']:
            print("\n✅ Attached Policies:")
            for policy in response['AttachedPolicies']:
                print(f"   - {policy['PolicyName']}")
        else:
            print("\n⚠️  No policies attached to user")
        
        # List inline policies
        response = iam.list_user_policies(UserName=user_name)
        if response['PolicyNames']:
            print("\n✅ Inline Policies:")
            for policy_name in response['PolicyNames']:
                print(f"   - {policy_name}")
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied':
            print("⚠️  Cannot check IAM policies (no IAM permissions)")
            print("   This is OK - IAM permissions are not required for S3 access")
        else:
            print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def suggest_fixes():
    """Suggest fixes based on the test results."""
    print("\n" + "=" * 60)
    print("Suggested Fixes")
    print("=" * 60)
    
    print("""
To fix the Access Denied error, you need to:

1. Go to AWS IAM Console
2. Find your IAM user (the one with these credentials)
3. Attach a policy with these permissions:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::financial-clinic",
                "arn:aws:s3:::financial-clinic/*"
            ]
        }
    ]
}

OR

4. Attach the AWS managed policy: AmazonS3FullAccess
   (Less secure but easier for testing)

5. Also check the bucket policy allows public read:
   - Go to S3 Console → financial-clinic bucket
   - Click Permissions tab
   - Edit Bucket Policy and add:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::financial-clinic/*"
        }
    ]
}

6. Uncheck "Block all public access" in bucket settings
""")


def main():
    """Run all diagnostic tests."""
    print("\n🔍 AWS S3 Diagnostic Tool\n")
    
    print(f"Configuration:")
    print(f"  Bucket: {settings.AWS_S3_BUCKET}")
    print(f"  Region: {settings.AWS_REGION}")
    print(f"  Access Key: {settings.AWS_ACCESS_KEY_ID[:10]}...")
    print()
    
    # Run tests
    creds_valid = test_credentials()
    
    if not creds_valid:
        print("\n❌ Cannot proceed - credentials are invalid")
        return
    
    bucket_exists = test_bucket_exists()
    
    if bucket_exists:
        test_bucket_permissions()
    
    list_user_policies()
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
