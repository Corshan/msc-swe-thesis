import os
import tempfile
import xml.etree.ElementTree as ET
import shutil

try:
    import pylibsrcml
except Exception as e:
    # Catch both ImportError and pylibsrcml.exceptions.srcMLNotFoundError
    pylibsrcml = None

from arch_recovery.config import Config

class Instrumentor:
    def __init__(self, config: Config):
        self.config = config

    def instrument(self) -> None:
        """
        Instruments all valid source files in the project to log function entries and exits.
        """
        if pylibsrcml is None:
            raise RuntimeError("pylibsrcml could not be imported. Ensure srcML is installed on the system.")
        
        if os.path.exists(self.config.instrumented_path):
            shutil.rmtree(self.config.instrumented_path)
            
        def ignore_func(dir_path, filenames):
            ignored = []
            for name in filenames:
                full_path = os.path.join(dir_path, name)
                if name.startswith('.') and os.path.isdir(full_path):
                    ignored.append(name)
                elif self._is_ignored(full_path):
                    ignored.append(name)
            return ignored
            
        shutil.copytree(self.config.project_path, self.config.instrumented_path, ignore=ignore_func)

        source_root = os.path.join(self.config.instrumented_path, os.path.basename(self.config.project_src_path))
        if not os.path.isdir(source_root):
            source_root = self.config.instrumented_path

        for root, dirs, files in os.walk(source_root):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_target_language(file_path):
                    self._instrument_file(file_path)
         

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

    def _instrument_file(self, file_path: str) -> None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
                out_path = tmp.name
                
            pylibsrcml.srcml(file_path, out_path)
            
            with open(out_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
                
            if xml_content.strip():
                ET.register_namespace('', 'http://www.srcML.org/srcML/src')
                root = ET.fromstring(xml_content)
                self._inject_trace_code(root, file_path)
                
                modified_xml = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(modified_xml)
                    
                pylibsrcml.srcml(out_path, file_path)
                
            os.remove(out_path)
        except Exception as e:
            print(f"Warning: Failed to instrument {file_path}: {e}")

    def _inject_trace_code(self, root: ET.Element, file_path: str) -> None:
        ns = {'src': 'http://www.srcML.org/srcML/src'}
        file_name = os.path.basename(file_path)
        
        parent_map = {c: p for p in root.iter() for c in p}
        
        for func in root.findall('.//src:function', ns):
            name_elem = func.find('src:name', ns)
            if name_elem is not None and name_elem.text:
                func_name = name_elem.text
                
                class_name = None
                curr = func
                while curr in parent_map:
                    parent = parent_map[curr]
                    if parent.tag == '{http://www.srcML.org/srcML/src}class':
                        cname = parent.find('src:name', ns)
                        if cname is not None and cname.text:
                            class_name = cname.text
                        break
                    curr = parent
                    
                display_name = f"{class_name}.{func_name}" if class_name else func_name
                
                block_content = func.find('src:block/src:block_content', ns)
                if block_content is not None:
                    new_stmt = ET.Element('{http://www.srcML.org/srcML/src}expr_stmt')
                    expr = ET.SubElement(new_stmt, '{http://www.srcML.org/srcML/src}expr')
                    
                    if self.config.language == "python":
                        code = f'with open(r"{self.config.trace_file_path}", "a") as __f: __f.write("ENTER: {file_name}::{display_name}\\n")'
                    elif self.config.language == "java":
                        code = f'try (java.io.FileWriter __fw = new java.io.FileWriter("{self.config.trace_file_path}", true)) {{ __fw.write("ENTER: {file_name}::{display_name}\\n"); }} catch (java.io.IOException e) {{}}'
                    elif self.config.language == "cpp":
                        code = f'{{ std::ofstream __ofs("{self.config.trace_file_path}", std::ios_base::app); __ofs << "ENTER: {file_name}::{display_name}\\n"; }}'
                    else:
                        code = ""
                        
                    expr.text = code
                    
                    # Fix indentation by duplicating the leading whitespace of the block_content
                    # and appending it after our newly inserted statement.
                    if block_content.text:
                        new_stmt.tail = block_content.text
                        
                    block_content.insert(0, new_stmt)
