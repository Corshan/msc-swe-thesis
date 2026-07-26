import ast
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

def get_python_files(source_dir: Path) -> List[Path]:
    """Returns all .py files in the source directory."""
    return list(source_dir.rglob("*.py"))

def resolve_module_path(module_name: str, source_dir: Path) -> Path:
    """Attempts to resolve a module name (e.g. 'foo.bar') to a file path."""
    if not module_name:
        return None
    
    parts = module_name.split('.')
    
    # Try directory with __init__.py
    dir_path = source_dir.joinpath(*parts)
    if dir_path.is_dir():
        init_file = dir_path / "__init__.py"
        if init_file.is_file():
            return init_file
            
    # Try as a file
    file_path = source_dir.joinpath(*parts[:-1]) / f"{parts[-1]}.py"
    if file_path.is_file():
        return file_path
        
    return None

class DependencyExtractor(ast.NodeVisitor):
    def __init__(self, current_file: Path, source_dir: Path):
        self.current_file = current_file
        self.source_dir = source_dir
        self.dependencies: Set[Path] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            resolved = resolve_module_path(alias.name, self.source_dir)
            if resolved:
                self.dependencies.add(resolved)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # We need to handle relative imports properly.
        # node.level > 0 means it's a relative import.
        # e.g. from . import X, from ..Y import Z
        if node.level > 0:
            # Reconstruct the module name based on current_file and node.level
            current_parts = list(self.current_file.relative_to(self.source_dir).parts)
            # Remove the current file name
            current_parts.pop()
            
            # Remove (level - 1) parts for relative imports
            for _ in range(node.level - 1):
                if current_parts:
                    current_parts.pop()
                    
            base_module = ".".join(current_parts)
            if node.module:
                module = f"{base_module}.{node.module}" if base_module else node.module
            else:
                module = base_module
        else:
            module = node.module

        if module:
            resolved = resolve_module_path(module, self.source_dir)
            if resolved:
                self.dependencies.add(resolved)
            
            # Also try to resolve individual imported names (e.g., from foo import bar -> foo/bar.py)
            for alias in node.names:
                resolved_sub = resolve_module_path(f"{module}.{alias.name}", self.source_dir)
                if resolved_sub:
                    self.dependencies.add(resolved_sub)
        self.generic_visit(node)

def extract_dependencies(source_dir: Path) -> Dict[str, List[str]]:
    """Extracts a dependency graph from a source directory."""
    py_files = get_python_files(source_dir)
    deps = {}
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(py_file))
            
            extractor = DependencyExtractor(py_file, source_dir)
            extractor.visit(tree)
            
            # Convert to strings relative to source_dir for cleaner output
            rel_source = str(py_file.relative_to(source_dir).as_posix())
            rel_deps = [str(d.relative_to(source_dir).as_posix()) for d in extractor.dependencies]
            
            deps[rel_source] = rel_deps
        except SyntaxError:
            print(f"Warning: SyntaxError in {py_file}, skipping.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error parsing {py_file}: {e}", file=sys.stderr)
            
    return deps

def calculate_metrics(deps: Dict[str, List[str]], module_mapping: Dict[str, List[str]]) -> Dict:
    """
    Calculates coupling and cohesion metrics.
    module_mapping: Dict mapping module_name -> list of file paths
    """
    # Create reverse mapping: file -> module
    file_to_module = {}
    for module_name, files in module_mapping.items():
        for file in files:
            file_to_module[file] = module_name

    metrics = {
        "cohesion": {},
        "coupling": {},
        "coupling_matrix": {}
    }

    # Initialize metric structures
    for module in module_mapping.keys():
        metrics["cohesion"][module] = 0
        metrics["coupling"][module] = 0
        metrics["coupling_matrix"][module] = {other: 0 for other in module_mapping.keys() if other != module}

    for source_file, target_files in deps.items():
        source_module = file_to_module.get(source_file)
        if not source_module:
            continue
            
        for target_file in target_files:
            target_module = file_to_module.get(target_file)
            
            # Skip if target file is not in any module (e.g. standard library, 3rd party, or ignored file)
            if not target_module:
                continue

            if source_module == target_module:
                # Internal dependency -> Cohesion
                metrics["cohesion"][source_module] += 1
            else:
                # External dependency -> Coupling
                metrics["coupling"][source_module] += 1
                metrics["coupling_matrix"][source_module][target_module] += 1

    num_modules = len(module_mapping)
    if num_modules > 0:
        metrics["average_cohesion"] = sum(metrics["cohesion"].values()) / num_modules
        metrics["average_coupling"] = sum(metrics["coupling"].values()) / num_modules
    else:
        metrics["average_cohesion"] = 0
        metrics["average_coupling"] = 0

    return metrics

def main():
    parser = argparse.ArgumentParser(description="Extract dependencies and calculate coupling/cohesion metrics.")
    parser.add_argument("-s", "--source", required=True, help="Path to the Python project source directory.")
    parser.add_argument("-m", "--mapping", required=True, help="Path to the flat JSON mapping file (module -> list of files).")
    parser.add_argument("-o", "--output", required=True, help="Path to the output JSON file for the metrics.")
    
    args = parser.parse_args()
    
    source_dir = Path(args.source).resolve()
    mapping_file = Path(args.mapping).resolve()
    output_file = Path(args.output).resolve()
    
    if not source_dir.is_dir():
        print(f"Error: Source directory {source_dir} not found or is not a directory.")
        sys.exit(1)
        
    if not mapping_file.is_file():
        print(f"Error: Mapping file {mapping_file} not found.")
        sys.exit(1)
        
    with open(mapping_file, 'r', encoding='utf-8') as f:
        module_mapping = json.load(f)
        
    print(f"Extracting dependencies from {source_dir}...")
    deps = extract_dependencies(source_dir)
    print(f"Extracted dependencies for {len(deps)} files.")
    
    print("Calculating metrics...")
    metrics = calculate_metrics(deps, module_mapping)
    
    # Bundle results
    results = {
        # "dependencies": deps,
        "metrics": metrics
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    print(f"Metrics successfully written to {output_file}")
    
    # Print summary
    print("\n--- Summary ---")
    for module in module_mapping.keys():
        print(f"Module: {module}")
        print(f"  Cohesion (internal deps): {metrics['cohesion'].get(module, 0)}")
        print(f"  Coupling (external deps): {metrics['coupling'].get(module, 0)}")

    print("\n--- Averages ---")
    print(f"Average Cohesion: {metrics.get('average_cohesion', 0):.2f}")
    print(f"Average Coupling: {metrics.get('average_coupling', 0):.2f}")

if __name__ == "__main__":
    main()
