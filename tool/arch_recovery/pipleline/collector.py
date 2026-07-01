import subprocess
import os
from arch_recovery.config import Config

class TraceCollector:
    def __init__(self, config: Config):
        self.test_command = config.test_command
        self.project_path = config.instrumented_path
        self.trace_file_path = config.trace_file_path

    def collect(self) -> None:
        """
        Executes the test command so the instrumented code can generate traces.
        """
        
        print(f"Running test suite to collect traces: {self.test_command}")
        
        try:
            # We use shell=True to allow commands like "pytest" or "mvn test"
            subprocess.run(
                self.test_command, 
                shell=True, 
                cwd=self.project_path, 
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.CalledProcessError as e:
            # Tests might fail, which is okay, we still might get traces
            print(f"Test command exited with code {e.returncode}. Traces may still have been collected.")
            print(f"Stderr: {e.stderr}")
