from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProjectPaths:
    root: Path
    src: Path
    instrumented: Path
    trace_dir: Path
    trace_file: Path

    @classmethod
    def from_root(self, project_path: str, project_src_path: str) -> 'ProjectPaths':
        root = Path(project_path)
        return self(
            root=root,
            src=Path(project_src_path),
            instrumented=Path(f"{root}_instrumented"),
            trace_dir=root / "tmp",
            trace_file=root / "tmp" / "out.trace"
        )
    