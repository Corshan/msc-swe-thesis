from click import shell_completion
import os
import tempfile
import xml.etree.ElementTree as ET
import shutil

try:
    import pylibsrcml
except Exception as e:
    # Catch both ImportError and pylibsrcml.exceptions.srcMLNotFoundError
    pylibsrcml = None

from arch_recovery.paths import ProjectPaths

class Instrumentor:
    def __init__(self, project_paths: ProjectPaths, language: str):
        self.project_path = project_paths.root
        self.project_path_src = project_paths.src
        self.instrumented_path = project_paths.instrumented
        self.trace_file_path = project_paths.trace_file
        self.language = language
        self.ignore_paths = []

    def instrument(self) -> None:
        """
        Instruments all valid source files in the project to log function entries and exits.
        """
        if pylibsrcml is None:
            raise RuntimeError("pylibsrcml could not be imported. Ensure srcML is installed on the system.")
        
        if os.path.exists(self.instrumented_path):
            shutil.rmtree(self.instrumented_path)
            
        def ignore_func(dir_path, filenames):
            ignored = []
            for name in filenames:
                full_path = os.path.join(dir_path, name)
                if name.startswith('.') and os.path.isdir(full_path):
                    ignored.append(name)
                elif self._is_ignored(full_path):
                    ignored.append(name)
            return ignored
            
        shutil.copytree(self.project_path, self.instrumented_path, ignore=ignore_func)

        source_root = os.path.join(self.instrumented_path, os.path.basename(self.project_path_src))
        if not os.path.isdir(source_root):
            source_root = self.instrumented_path

        for root, dirs, files in os.walk(source_root):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_target_language(file_path):
                    self._instrument_file(file_path)
         

    def _is_ignored(self, path: str) -> bool:
        for ignore_path in self.ignore_paths:
            if ignore_path in path:
                return True
        return False

    def _is_target_language(self, path: str) -> bool:
        _, ext = os.path.splitext(path)
        if self.language == "python" and ext == ".py":
            return True
        if self.language == "java" and ext == ".java":
            return True
        if self.language == "cpp" and ext in [".cpp", ".h", ".c", ".hpp"]:
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
                    
                    if self.language == "python":
                        code = f'with open(r"{self.trace_file_path}", "a") as __f: __f.write("ENTER: {file_name}::{display_name}\\n")'
                    elif self.language == "java":
                        code = f'try (java.io.FileWriter __fw = new java.io.FileWriter("{self.trace_file_path}", true)) {{ __fw.write("ENTER: {file_name}::{display_name}\\n"); }} catch (java.io.IOException e) {{}}'
                    elif self.language == "cpp":
                        code = f'{{ std::ofstream __ofs("{self.trace_file_path}", std::ios_base::app); __ofs << "ENTER: {file_name}::{display_name}\\n"; }}'
                    else:
                        code = ""
                        
                    expr.text = code
                    
                    indentation = "\n    "
                    parent = parent_map.get(func)
                    if parent is not None:
                        idx = list(parent).index(func)
                        prev_text = list(parent)[idx-1].tail if idx > 0 else parent.text
                        if prev_text is not None and '\n' in prev_text:
                            base_indent = prev_text.split('\n')[-1]
                            if not base_indent.strip():
                                indentation = "\n" + base_indent + "    "
                    
                    has_newline = block_content.text is not None and '\n' in block_content.text
                    if has_newline:
                        new_stmt.tail = block_content.text
                    else:
                        block_content.text = indentation
                        new_stmt.tail = indentation
                        
                    block_content.insert(0, new_stmt)
