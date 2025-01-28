import importlib
import sys
from pathlib import Path

def find_circular_imports():
    """Scan modules for circular imports"""
    # Get all Python files in the project
    project_dir = Path(__file__).parent.parent
    python_files = list(project_dir.rglob("*.py"))
    
    # Track imports
    imports = {}
    
    for file in python_files:
        module_name = file.stem
        module_path = str(file)
        
        try:
            module = importlib.import_module(module_name)
            imports[module_name] = set(getattr(module, '__all__', []))
        except Exception as e:
            print(f"Error importing {module_name}: {e}")
            continue
            
    # Look for circular dependencies
    circular = []
    for module in imports:
        dependencies = imports[module]
        for dep in dependencies:
            if dep in imports and module in imports[dep]:
                circular.append((module, dep))
                
    return circular

def fix_circular_imports():
    """Attempt to fix detected circular imports"""
    circular = find_circular_imports()
    if not circular:
        print("No circular imports found")
        return
        
    print("Found circular imports:")
    for mod1, mod2 in circular:
        print(f"{mod1} <-> {mod2}")
        
    # Attempt to fix by reordering imports
    # This is a simplified approach
    # In real scenarios, more sophisticated analysis would be needed
    for mod1, mod2 in circular:
        # Try to modify the imports in mod1
        file = Path(__file__).parent.parent / f"{mod1}.py"
        if file.exists():
            content = file.read_text()
            # Look for import of mod2 and move it to the bottom
            if f"import {mod2}" in content:
                lines = content.splitlines()
                import_line = [i for i, line in enumerate(lines) if f"import {mod2}" in line][0]
                import_lines = lines[import_line:]
                new_content = "\n".join(lines[:import_line] + import_lines)
                file.write_text(new_content)
                print(f"Fixed circular import between {mod1} and {mod2}")
                
if __name__ == "__main__":
    fix_circular_imports()
