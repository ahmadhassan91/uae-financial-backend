#!/usr/bin/env python3
"""
Script to update CORS configuration for Netlify deployment
This script adds the specific Netlify domain to the allowed origins
"""

import os
import sys

def update_cors_config():
    """Update the CORS configuration to include the Netlify domain."""
    
    # The specific Netlify domain that needs to be added
    netlify_domain = "https://national-bonds-ae.netlify.app"
    
    print(f"Adding {netlify_domain} to CORS allowed origins...")
    
    # Read the current config file
    config_file = "app/config.py"
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Find the ALLOWED_ORIGINS section and add the Netlify domain
        if netlify_domain not in content:
            # Find the ALLOWED_ORIGINS list
            start_marker = 'ALLOWED_ORIGINS: List[str] = ['
            end_marker = ']'
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                print("Error: Could not find ALLOWED_ORIGINS in config file")
                return False
            
            # Find the end of the list
            start_idx += len(start_marker)
            bracket_count = 1
            end_idx = start_idx
            
            while bracket_count > 0 and end_idx < len(content):
                if content[end_idx] == '[':
                    bracket_count += 1
                elif content[end_idx] == ']':
                    bracket_count -= 1
                end_idx += 1
            
            # Insert the new domain before the closing bracket
            insert_pos = end_idx - 1
            new_entry = f'        "{netlify_domain}",  # Netlify production deployment\n    '
            
            new_content = content[:insert_pos] + new_entry + content[insert_pos:]
            
            # Write the updated content back
            with open(config_file, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Successfully added {netlify_domain} to ALLOWED_ORIGINS")
            return True
        else:
            print(f"✅ {netlify_domain} is already in ALLOWED_ORIGINS")
            return True
            
    except Exception as e:
        print(f"❌ Error updating config file: {e}")
        return False

def deploy_to_heroku():
    """Deploy the updated configuration to Heroku."""
    print("\n🚀 Deploying updated configuration to Heroku...")
    
    try:
        # Add and commit changes
        os.system("git add app/config.py")
        os.system('git commit -m "Update CORS configuration for Netlify deployment"')
        
        # Push to Heroku
        result = os.system("git push heroku main")
        
        if result == 0:
            print("✅ Successfully deployed to Heroku!")
            print("🔄 Heroku is restarting the application with new CORS settings...")
            return True
        else:
            print("❌ Failed to deploy to Heroku")
            return False
            
    except Exception as e:
        print(f"❌ Error deploying to Heroku: {e}")
        return False

def main():
    """Main function to update CORS and deploy."""
    print("🔧 Updating CORS configuration for Netlify deployment")
    print("=" * 60)
    
    # Update the configuration
    if not update_cors_config():
        sys.exit(1)
    
    # Ask user if they want to deploy
    deploy = input("\n🤔 Do you want to deploy this change to Heroku now? (y/N): ").lower().strip()
    
    if deploy in ['y', 'yes']:
        if deploy_to_heroku():
            print("\n🎉 CORS configuration updated and deployed successfully!")
            print(f"Your Netlify site should now be able to connect to the Heroku backend.")
        else:
            print("\n⚠️  Configuration updated locally but deployment failed.")
            print("You can manually deploy later with: git push heroku main")
    else:
        print("\n📝 Configuration updated locally.")
        print("To deploy later, run: git push heroku main")

if __name__ == "__main__":
    main()