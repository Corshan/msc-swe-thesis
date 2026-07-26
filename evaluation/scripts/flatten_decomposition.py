import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any

def walk_tree(node: Dict[str, Any], current_path: str, groups: Dict[str, set], strip_prefix: str = ""):
    """Recursively walk the decomposition tree and group files by their feature combinations."""
    name = node.get("name", "")
    node_type = node.get("type", "")
    
    # Construct the path
    path = f"{current_path}/{name}" if current_path else name
    
    if node_type == "file":
        features = node.get("features", {})
        if features:
            feature_names = sorted(list(features.keys()))
            
            # Create the group name based on the combination of features
            if len(feature_names) == 1:
                group_name = f"Only {feature_names[0]}"
            elif len(feature_names) == 2:
                group_name = f"{feature_names[0]} & {feature_names[1]}"
            else:
                group_name = ", ".join(feature_names)
                
            clean_path = path
            if strip_prefix and clean_path.startswith(strip_prefix):
                clean_path = clean_path[len(strip_prefix):]
                
            groups.setdefault(group_name, set()).add(clean_path)
            
    elif node_type == "directory":
        for child in node.get("children", []):
            walk_tree(child, path, groups, strip_prefix)

def flatten_decomposition(input_file: Path, output_file: Path, strip_prefix: str = ""):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    groups = {}
    walk_tree(data, "", groups, strip_prefix)
    
    # Convert sets to sorted lists for JSON serialization
    flat_mapping = {k: sorted(list(v)) for k, v in groups.items()}
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(flat_mapping, f, indent=2)
        
    print(f"Successfully flattened {len(flat_mapping)} groups to {output_file}")
    for group, files in flat_mapping.items():
        print(f"  - {group}: {len(files)} files")

def main():
    parser = argparse.ArgumentParser(description="Flatten decomposition.json into a flat mapping of feature combinations to files.")
    parser.add_argument("-i", "--input", required=True, help="Path to decomposition.json")
    parser.add_argument("-o", "--output", required=True, help="Path to output flattened mapping JSON")
    parser.add_argument("--strip-prefix", default="src/", help="Prefix to strip from file paths (default: 'src/')")
    
    args = parser.parse_args()
    
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    
    if not input_path.is_file():
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    flatten_decomposition(input_path, output_path, args.strip_prefix)

if __name__ == "__main__":
    main()
