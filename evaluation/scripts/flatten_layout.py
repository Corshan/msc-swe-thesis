import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any

def walk_tree(node: Dict[str, Any], current_path: str, groups: Dict[str, set], strip_prefix: str = ""):
    """Recursively walk the layout tree and group files by their parent directory."""
    name = node.get("name", "")
    node_type = node.get("type", "")
    
    # Construct the path
    path = f"{current_path}/{name}" if current_path else name
    
    if node_type == "file":
        # The group is the parent directory (current_path)
        group_name = current_path
        
        if strip_prefix and group_name.startswith(strip_prefix):
            group_name = group_name[len(strip_prefix):]
            
        # Handle files at the root of the stripped path
        if not group_name:
            # You can name the root group whatever makes sense, e.g., the root directory name or simply 'root'
            group_name = "root"
            
        clean_path = path
        if strip_prefix and clean_path.startswith(strip_prefix):
            clean_path = clean_path[len(strip_prefix):]
            
        groups.setdefault(group_name, set()).add(clean_path)
            
    elif node_type == "directory":
        for child in node.get("children", []):
            walk_tree(child, path, groups, strip_prefix)

def flatten_layout(input_file: Path, output_file: Path, strip_prefix: str = ""):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    groups = {}
    walk_tree(data, "", groups, strip_prefix)
    
    # Convert sets to sorted lists for JSON serialization
    flat_mapping = {k: sorted(list(v)) for k, v in groups.items()}
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flat_mapping, f, indent=2)
        
    print(f"Successfully flattened {len(flat_mapping)} directory groups to {output_file}")
    for group, files in flat_mapping.items():
        print(f"  - {group}: {len(files)} files")

def main():
    parser = argparse.ArgumentParser(description="Flatten layout.json into a flat mapping of directories to files.")
    parser.add_argument("-i", "--input", required=True, help="Path to layout.json")
    parser.add_argument("-o", "--output", required=True, help="Path to output flattened mapping JSON")
    parser.add_argument("--strip-prefix", default="src/", help="Prefix to strip from file paths and group names (default: 'src/')")
    
    args = parser.parse_args()
    
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    
    if not input_path.is_file():
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    flatten_layout(input_path, output_path, args.strip_prefix)

if __name__ == "__main__":
    main()
