import click
import shutil
from arch_recovery.paths import ProjectPaths
import os
import subprocess
import sys
from pathlib import Path


class TraceCollector:
    def __init__(self, project_paths: ProjectPaths, test_command: str, test_name: str):
        self.test_command = test_command
        self.test_name = test_name
        self.project_path = project_paths.instrumented
        self.project_root = project_paths.root
        self.trace_file_input_path = project_paths.trace_file
        self.trace_file_output_path = project_paths.trace_dir / f"{test_name}.trace"
        self.venv_path = Path(self.project_root) / ".venv"
        self.venv_bin = self.venv_path / ("Scripts" if os.name == "nt" else "bin")
        self.venv_python = self.venv_bin / ("python.exe" if os.name == "nt" else "python")

    def collect(self) -> None:
        """
        Create a local virtual environment inside the instrumented project, install its requirements,
        and run the requested test command inside that environment to collect traces.
        """

        print(f"Preparing test environment for trace collection in {self.project_path}")

        env = os.environ.copy()
        env["PATH"] = f"{self.venv_bin}{os.pathsep}{env.get('PATH', '')}"
        env["VIRTUAL_ENV"] = str(self.venv_path)
        env["PYTEST_ADDOPTS"] = ""

        commands = [
            (f'"{sys.executable}" -m venv "{self.venv_path}"', str(self.project_root)),
            (f'"{self.venv_python}" -m pip install --upgrade pip', str(self.project_path)),
        ]

        commands.extend(self._build_install_commands())
        commands.append((self._build_test_command(), self.project_path))

        if self.trace_file_input_path.exists():
            os.remove(self.trace_file_input_path)

        try:
            for command, cwd in commands:
                subprocess.run(
                    command,
                    shell=True,
                    cwd=cwd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                )
        except subprocess.CalledProcessError as e:
            print(f"Command exited with code {e.returncode}. Traces may still have been collected.")
            # print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
        
        # create the trace ouput file than copy the input tace file to output
        self.trace_file_output_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.trace_file_output_path.exists():
            self.trace_file_output_path.touch()
        shutil.copy2(self.trace_file_input_path, self.trace_file_output_path)
        click.echo(f"Saved trace to {self.trace_file_output_path}")

    def _build_install_commands(self) -> list[tuple[str, str]]:
        project_path = Path(self.project_path)
        commands: list[tuple[str, str]] = []

        requirement_files = [
            project_path / "requirements.txt",
            project_path / "requirements-dev.txt",
            project_path / "requirements-test.txt",
            project_path / "dev-requirements.txt",
            project_path / "test-requirements.txt",
        ]

        for requirement_file in requirement_files:
            if requirement_file.exists():
                commands.append((f'"{self.venv_python}" -m pip install -r "{requirement_file}"', str(project_path)))

        if not commands:
            commands.append((f'"{self.venv_python}" -m pip install -e ".[all,test,dev,full]"', str(project_path)))

        commands.append((f'"{self.venv_python}" -m pip install pytest pytest-xdist hypothesis', str(project_path)))
        return commands

    def _build_test_command(self) -> str:
        command = self.test_command.strip()
        if not command:
            return f'"{self.venv_python}" -m pytest -o addopts=""'

        normalized = command.lower()
        if normalized.startswith("pytest"):
            args = command[6:].lstrip()
            if args:
                return f'"{self.venv_python}" -m pytest -o addopts="" {args}'.rstrip()
            return f'"{self.venv_python}" -m pytest -o addopts=""'
        if normalized.startswith("python -m"):
            remainder = command[7:].lstrip()
            if remainder.startswith("pytest"):
                args = remainder[6:].lstrip()
                if args:
                    return f'"{self.venv_python}" -m pytest -o addopts="" {args}'.rstrip()
                return f'"{self.venv_python}" -m pytest -o addopts=""'
            return f'"{self.venv_python}" {remainder}'

        return command
