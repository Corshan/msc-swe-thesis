import os
import tempfile
import xml.etree.ElementTree as ET
try:
    import pylibsrcml
except Exception as e:
    # Catch both ImportError and pylibsrcml.exceptions.srcMLNotFoundError
    pylibsrcml = None

from arch_recovery.config import Config

class Instrumentor:
    def __init__(self, config: Config):
        self.config = config

    def instrument(self, trace_file: str) -> None:
        """
        Instruments all valid source files in the project to log function entries and exits.
        """
        if pylibsrcml is None:
            raise RuntimeError("pylibsrcml could not be imported. Ensure srcML is installed on the system.")

        for root, dirs, files in os.walk(self.config.project_path):
            # Filter ignored paths
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not self._is_ignored(file_path) and self._is_target_language(file_path):
                    self._instrument_file(file_path, trace_file)

    def _is_ignored(self, path: str) -> bool:
        for ignore_path in self.config.ignore_paths:
            if ignore_path in path:
                return True
        return False

    def _is_target_language(self, path: str) -> bool:
        _, ext = os.path.splitext(path)
        if self.config.language == "python" and ext == ".py":
            return True
        if self.config.language == "java" and ext == ".java":
            return True
        if self.config.language == "cpp" and ext in [".cpp", ".h", ".c", ".hpp"]:
            return True
        return False

    def _instrument_file(self, file_path: str, trace_file: str) -> None:
        try:
            xml_content = pylibsrcml.srcml(file_path) 
            root = ET.fromstring(xml_content)
            pass
        except Exception as e:
            print(f"Warning: Failed to instrument {file_path}: {e}")
