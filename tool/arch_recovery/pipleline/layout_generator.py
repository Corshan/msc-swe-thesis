import json
import os
from pathlib import Path

class LayoutGenerator:
    def __init__(self, project_src_path: Path, allowed_extensions: tuple[str, ...] | None = None):
        self.project_src_path = Path(project_src_path)
        self.ignore_dirs = {".git", "__pycache__", "venv", ".venv", "node_modules"}
        self.allowed_extensions = allowed_extensions

    def generate(self, output_file: Path) -> None:
        if not self.project_src_path.exists() or not self.project_src_path.is_dir():
            raise FileNotFoundError(f"Source directory {self.project_src_path} does not exist.")

        valid_files_paths = []
        for root, dirs, files in os.walk(self.project_src_path):
            # Skip ignored directories and hidden directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
            for f in files:
                # Skip hidden files and common compiled extensions
                if f.startswith('.') or f.endswith(('.pyc', '.o', '.class', '.pyo')):
                    continue
                # Apply allowed extensions filter if provided
                if self.allowed_extensions and not f.endswith(self.allowed_extensions):
                    continue
                valid_files_paths.append(Path(root) / f)

        # Helper to create a tree node
        def create_node(name: str, is_dir: bool = True):
            node = {"name": name, "type": "directory" if is_dir else "file"}
            if is_dir:
                node["children"] = []
            return node

        root_node = create_node(self.project_src_path.name, is_dir=True)

        for f_path in valid_files_paths:
            rel_path = f_path.relative_to(self.project_src_path)
            parts = rel_path.parts
            
            current_node = root_node
            for i, part in enumerate(parts):
                is_file = (i == len(parts) - 1)
                
                # Check if child already exists in current directory
                child = next((c for c in current_node["children"] if c["name"] == part), None)
                if not child:
                    child = create_node(part, is_dir=not is_file)
                    current_node["children"].append(child)
                
                current_node = child

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(root_node, f, indent=2)
