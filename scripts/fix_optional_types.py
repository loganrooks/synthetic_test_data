#!/usr/bin/env python3
"""
Script to fix missing Optional type hints across the codebase.
"""
import os
import re
from typing import List, Tuple

def find_missing_optional_hints(filepath: str) -> List[Tuple[int, str, str]]:
    """Find lines with missing Optional hints in a file."""
    issues = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Check if Optional is imported
    has_optional_import = any('Optional' in line and 'from typing import' in line for line in lines)
    
    for i, line in enumerate(lines):
        # Match function definitions with Type = None pattern
        # Captures: (spaces, param_name, type, rest_of_line)
        match = re.match(r'^(\s*def\s+\w+\(.*?)(\w+):\s*([A-Za-z_][A-Za-z0-9_\[\]]*)\s*=\s*None(.*?\):.*)', line)
        if match:
            indent = match.group(1)
            param = match.group(2)
            type_hint = match.group(3)
            rest = match.group(4)
            
            # Skip if already using Optional
            if 'Optional' not in type_hint:
                issues.append((i, line.strip(), has_optional_import))
    
    return issues

def fix_optional_in_file(filepath: str) -> bool:
    """Fix missing Optional hints in a file. Returns True if changes were made."""
    issues = find_missing_optional_hints(filepath)
    if not issues:
        return False
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Track if we need to add Optional import
    has_optional_import = any('Optional' in line and 'from typing import' in line for line in lines)
    needs_optional_import = any(not issue[2] for issue in issues)
    
    # Fix each issue
    changes_made = False
    for line_num, original_line, _ in issues:
        line = lines[line_num]
        # Replace Type = None with Optional[Type] = None
        new_line = re.sub(
            r'(\w+):\s*([A-Za-z_][A-Za-z0-9_\[\]]*)\s*=\s*None',
            r'\1: Optional[\2] = None',
            line
        )
        if new_line != line:
            lines[line_num] = new_line
            changes_made = True
            print(f"  Line {line_num + 1}: Fixed {original_line}")
    
    # Add Optional import if needed
    if changes_made and needs_optional_import and not has_optional_import:
        # Find the best place to add the import
        import_added = False
        for i, line in enumerate(lines):
            if line.startswith('from typing import'):
                # Add Optional to existing typing import
                if 'Optional' not in line:
                    lines[i] = line.rstrip()
                    if lines[i].endswith(')'):
                        lines[i] = lines[i][:-1] + ', Optional)\n'
                    else:
                        lines[i] = lines[i].rstrip(',\n') + ', Optional\n'
                    import_added = True
                    print(f"  Added Optional to existing typing import on line {i + 1}")
                break
            elif line.startswith('import ') and not import_added:
                # Add new typing import before first import
                lines.insert(i, 'from typing import Optional\n')
                import_added = True
                print(f"  Added new typing import before line {i + 1}")
                break
        
        if not import_added:
            # Add at the beginning after docstring/comments
            insert_pos = 0
            for i, line in enumerate(lines):
                if not line.startswith('#') and not line.startswith('"""') and line.strip():
                    insert_pos = i
                    break
            lines.insert(insert_pos, 'from typing import Optional\n')
            print(f"  Added new typing import at line {insert_pos + 1}")
    
    # Write back to file
    if changes_made:
        with open(filepath, 'w') as f:
            f.writelines(lines)
    
    return changes_made

def main():
    # Find all Python files in the project
    project_root = '/home/loganrooks/Code/synthetic_test_data'
    python_files = []
    
    for root, dirs, files in os.walk(project_root):
        # Skip venv and other non-project directories
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to check")
    
    # Process each file
    files_modified = 0
    total_fixes = 0
    
    for filepath in sorted(python_files):
        issues = find_missing_optional_hints(filepath)
        if issues:
            print(f"\n{filepath}: {len(issues)} missing Optional hints")
            if fix_optional_in_file(filepath):
                files_modified += 1
                total_fixes += len(issues)
    
    print(f"\n=== Summary ===")
    print(f"Files modified: {files_modified}")
    print(f"Total Optional hints added: {total_fixes}")

if __name__ == '__main__':
    main()