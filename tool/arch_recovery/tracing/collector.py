import subprocess
import os

class TraceCollector:
    def __init__(self, test_command: str, project_path: str):
        self.test_command = test_command
        self.project_path = project_path

    def collect(self, trace_file: str) -> None:
        """
        Executes the test command so the instrumented code can generate traces.
        """
        env = os.environ.copy()
        # Ensure the test process knows where to log traces
        env["ARCH_RECOVERY_TRACE_FILE"] = trace_file

        print(f"Running test suite to collect traces: {self.test_command}")
        
        try:
            # We use shell=True to allow commands like "pytest" or "mvn test"
            subprocess.run(
                self.test_command, 
                shell=True, 
                cwd=self.project_path, 
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.CalledProcessError as e:
            # Tests might fail, which is okay, we still might get traces
            print(f"Test command exited with code {e.returncode}. Traces may still have been collected.")
            print(f"Stderr: {e.stderr}")
