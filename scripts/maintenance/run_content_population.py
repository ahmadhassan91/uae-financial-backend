#!/usr/bin/env python3
"""
Simple runner script to populate all frontend content to database.
"""
import subprocess
import sys
import os

def main():
    """Run the content population script."""
    print("🚀 Starting Frontend Content Population...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    populate_script = os.path.join(script_dir, "populate_all_content_to_database.py")
    
    try:
        # Run the population script
        result = subprocess.run([sys.executable, populate_script], 
                              cwd=script_dir, 
                              check=True)
        
        print("\n✅ Content population completed successfully!")
        print("You can now access the admin interface to manage translations.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running population script: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n❌ Population script not found: {populate_script}")
        sys.exit(1)

if __name__ == "__main__":
    main()