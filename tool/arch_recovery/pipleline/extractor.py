import ast
import os
import re
from typing import Dict, List, Tuple

class StaticExtractor:
    def __init__(self, project_path: str, language: str):
        self.project_path = project_path
        self.language = language

    def extract(self) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
        """
        Extracts static components and dependencies.
        Returns:
            function_texts: Dict mapping function identifier to its source code text.
            dependencies: Dict mapping function identifier to a list of function identifiers it calls.
        """
        function_texts = {}
        dependencies = {}

        for root, _, files in os.walk(self.project_path):
            for file in files:
                if not file.endswith(('.py', '.java', '.cpp', '.c')):
                    continue
                
                file_path = os.path.join(root, file)
                
                if self.language == 'python' and file.endswith('.py'):
                    self._extract_python(file_path, function_texts, dependencies)
                else:
                    self._extract_generic(file_path, function_texts, dependencies)
                    
        return function_texts, dependencies

    def _extract_python(self, file_path: str, function_texts: Dict[str, str], dependencies: Dict[str, List[str]]):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Simplified identifier: file_name::function_name
                    identifier = f"{os.path.basename(file_path)}::{node.name}"
                    function_texts[identifier] = ast.unparse(node)
                    
                    # Extract calls within this function
                    calls = []
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                calls.append(child.func.id)
                            elif isinstance(child.func, ast.Attribute):
                                calls.append(child.func.attr)
                    dependencies[identifier] = calls
        except Exception as e:
            print(f"Failed to parse python file {file_path}: {e}")

    def _extract_generic(self, file_path: str, function_texts: Dict[str, str], dependencies: Dict[str, List[str]]):
        # A rudimentary fallback regex-based extractor for non-Python languages
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Very simplistic regex for finding functions in Java/C++
            pattern = re.compile(r'(\w+)\s+(\w+)\s*\([^)]*\)\s*\{')
            matches = pattern.finditer(content)
            for match in matches:
                return_type, func_name = match.groups()
                identifier = f"{os.path.basename(file_path)}::{func_name}"
                # Just mock the text and calls for now
                function_texts[identifier] = f"{return_type} {func_name}() {{ ... }}"
                dependencies[identifier] = []
        except Exception:
            pass
