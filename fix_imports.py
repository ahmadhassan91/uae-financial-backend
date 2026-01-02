#!/usr/bin/env python3
"""Fix Python 3.8 compatibility issues by adding proper typing imports."""

import os
import re
from pathlib import Path

def fix_imports(file_path):
    """Add List and Dict imports to files that use them."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file uses List or Dict
        uses_list = 'List[' in content
        uses_dict = 'Dict[' in content
        
        if not (uses_list or uses_dict):
            return False
        
        # Check if List is already imported
        has_list_import = re.search(r'from typing\s+import.*List', content)
        has_dict_import = re.search(r'from typing\s+import.*Dict', content)
        
        # Find the typing import line
        typing_import_match = re.search(r'from typing\s+import\s+([^\n]+)', content)
        
        if typing_import_match:
            # Update existing typing import
            current_imports = typing_import_match.group(1).strip()
            imports_list = [imp.strip() for imp in current_imports.split(',')]
            
            if uses_list and 'List' not in current_imports:
                imports_list.append('List')
            if uses_dict and 'Dict' not in current_imports:
                imports_list.append('Dict')
            
            new_imports = ', '.join(imports_list)
            new_line = f"from typing import {new_imports}", List, Dict
            content = content.replace(typing_import_match.group(0), new_line)
        else:
            # Add new typing import after other imports
            import_line = "from typing import"
            if uses_list and uses_dict:
                import_line += " List, Dict"
            elif uses_list:
                import_line += " List"
            elif uses_dict:
                import_line += " Dict"
            
            # Find a good place to insert the import
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    insert_idx = i + 1
                elif line.strip() == '' and insert_idx > 0:
                    break
            
            lines.insert(insert_idx, import_line)
            content = '\n'.join(lines)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in the backend."""
    backend_dir = Path("/home/clustox/Desktop/UAE-FC/financialclinic-backend")
    fixed_count = 0
    
    for py_file in backend_dir.rglob("*.py"):
        if fix_imports(py_file):
            fixed_count += 1
            print(f"Fixed: {py_file}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
