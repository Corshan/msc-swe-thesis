import subprocess
import shutil
import os
from pathlib import Path

class DiagramRenderer:
    def __init__(self, mmd_file_path: Path):
        self.mmd_file_path = mmd_file_path

    def render(self, output_file: Path) -> None:
        if not self.mmd_file_path.exists():
            raise FileNotFoundError(f"{self.mmd_file_path} does not exist. Please generate the diagram first.")

        mmdc_path = shutil.which("mmdc")
        npx_path = shutil.which("npx")
        
        if mmdc_path:
            cmd = [mmdc_path, "-i", str(self.mmd_file_path), "-o", str(output_file)]
        elif npx_path:
            cmd = [npx_path, "-y", "-p", "@mermaid-js/mermaid-cli", "mmdc", "-i", str(self.mmd_file_path), "-o", str(output_file)]
        else:
            raise RuntimeError("Mermaid CLI (mmdc) or npx is not installed. Please install Node.js and run 'npm install -g @mermaid-js/mermaid-cli'.")

        try:
            # On Windows, npm/npx are .cmd files, which require shell=True if not invoked precisely, 
            # but using the absolute path from which() often works. We'll add shell=True to be safe.
            is_windows = os.name == 'nt'
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_windows)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode("utf-8", errors="replace") if e.stderr else str(e)
            raise RuntimeError(f"Failed to render diagram: {error_message}")
