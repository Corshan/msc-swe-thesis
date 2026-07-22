from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProjectPaths:
    root: Path
    src: Path
    instrumented: Path
    output_dir: Path
    trace_dir: Path
    diagrams_dir: Path
    trace_file: Path

    @classmethod
    def from_root(self, project_path: str, project_src_path: str) -> 'ProjectPaths':
        root = Path(project_path)
        output_dir = root / "recon_data"
        return self(
            root=root,
            src=Path(project_src_path),
            instrumented=Path(f"{root}_instrumented"),
            output_dir=output_dir,
            trace_dir=output_dir / "traces",
            diagrams_dir=output_dir / "diagrams",
            trace_file=output_dir / "traces" / "out.trace"
        )
    