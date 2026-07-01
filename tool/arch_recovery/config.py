import tempfile
from typing import Self
import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class Config:
    project_path: Path
    language: str
    ignore_paths: List[str] = field(default_factory=list)
    trace_file_path: str = None
    instrumented_path: str = None

    def __init__(self, project_path: str, language: str, test_command: str) -> None:
        self.project_path = Path(project_path).resolve()
        self.instrumented_path = self.project_path.with_name(self.project_path.name + "_instrumented")
        self.test_command = test_command
        self.language = language
        self.ignore_paths = []
        self.trace_file_path = None
        self._load_ignore_paths()
        self._create_temp_trace_file()

    def _detect_language(self) -> str:
        # Simplistic language detection based on file extensions
        ext_counts = {".py": 0, ".java": 0, ".cpp": 0, ".c": 0}
        for root, _, files in os.walk(self.project_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in ext_counts:
                    ext_counts[ext] += 1
        
        # Determine max count
        best_ext = max(ext_counts, key=ext_counts.get) # type: ignore
        if ext_counts[best_ext] > 0:
            if best_ext == ".py": return "python"
            if best_ext == ".java": return "java"
            if best_ext in [".cpp", ".c"]: return "cpp"
        
        # Default fallback
        return "python"

    def _load_ignore_paths(self) -> None:
        gitignore_path = self.project_path / ".gitignore"
        if gitignore_path.exists():
            with gitignore_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ignore_paths.append(line)
        else:
            # Predefined list for current language
            if self.language == "python":
                self.ignore_paths.extend(["venv", ".venv", "__pycache__", "site-packages"])
            elif self.language == "java":
                self.ignore_paths.extend(["target", "build", ".gradle", ".m2"])
            elif self.language == "cpp":
                self.ignore_paths.extend(["build", "out", "bin"])

    def _create_temp_trace_file(self) -> None:
        with tempfile.NamedTemporaryFile(dir=self.project_path, delete=False, mode='w', suffix='.trace') as temp_trace_file:
            self.trace_file_path = temp_trace_file.name
