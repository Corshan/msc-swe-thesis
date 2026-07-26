import json
import os
from pathlib import Path
from collections import defaultdict
from arch_recovery.pipleline.diagram_renderer import DiagramRenderer

class BaseDiagramGenerator:
    def generate(self, output_file: Path) -> None:
        raise NotImplementedError

    def generate_and_render(self, mmd_output_path: Path, img_output_path: Path) -> None:
        self.generate(mmd_output_path)
        renderer = DiagramRenderer(mmd_output_path)
        renderer.render(img_output_path)

class FeatureDiagramGenerator(BaseDiagramGenerator):
    def __init__(self, feature_sets_path: Path):
        self.feature_sets_path = feature_sets_path

    def generate(self, output_file: Path) -> None:
        if not self.feature_sets_path.exists():
            raise FileNotFoundError(f"{self.feature_sets_path} does not exist. Run compute first.")

        with open(self.feature_sets_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        mermaid_lines = [
            "%%{init: {'flowchart': {'curve': 'linear'}}}%%",
            "graph LR"
        ]
        
        colors = [
            "#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", 
            "#f15bb5", "#00bbf9", "#00f5d4", "#f4a261", "#e76f51"
        ]
        
        shared_colors = [
            "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e",
            "#e6ab02", "#a6761d", "#a6cee3", "#1f78b4", "#b2df8a"
        ]

        feature_nodes = []
        group_nodes = []
        component_nodes = set()
        edges = []
        link_styles = []
        feature_styles = []
        component_styles = []
        
        node_id_map = {}
        def get_node_id(name: str, prefix: str = "N") -> str:
            if name not in node_id_map:
                node_id_map[name] = f"{prefix}{len(node_id_map)}"
            return node_id_map[name]

        link_index = 0

        # 1. Reverse mapping: component -> set of features
        component_to_features = {}
        for feature_name, feature_data in data.items():
            components = set(feature_data.get("involved", []))
            for comp in components:
                parts = comp.split("::")
                if len(parts) >= 2:
                    file_part = parts[0]
                    rest = parts[1]
                    if "." in rest:
                        class_part = rest.split(".")[0]
                        display_comp = f"{file_part}::{class_part}"
                    else:
                        display_comp = file_part
                else:
                    display_comp = comp
                
                if display_comp not in component_to_features:
                    component_to_features[display_comp] = set()
                component_to_features[display_comp].add(feature_name)

        # 2. Group components by their feature sets
        from collections import defaultdict
        group_to_components = defaultdict(list)
        for comp, features in component_to_features.items():
            feature_tuple = tuple(sorted(list(features)))
            group_to_components[feature_tuple].append(comp)

        # 3. Define features and colors
        feature_colors = {}
        for i, feature_name in enumerate(data.keys()):
            color = colors[i % len(colors)]
            feature_colors[feature_name] = color
            
            f_node = get_node_id(feature_name, "F")
            feature_nodes.append(f"{f_node}[\"{feature_name}\"]")
            
            feature_styles.append(f"    classDef style{f_node} fill:{color},stroke:#333,stroke-width:2px,color:#000;")
            feature_styles.append(f"    class {f_node} style{f_node};")

        # 4. Create Group Nodes and Edges
        group_styles = []
        shared_color_index = 0
        
        for feature_tuple, comps in group_to_components.items():
            if len(feature_tuple) == 1:
                group_name = f"Only {feature_tuple[0]}"
                group_color = feature_colors[feature_tuple[0]]
            else:
                if len(feature_tuple) == 2:
                    group_name = f"{feature_tuple[0]} & {feature_tuple[1]}"
                else:
                    group_name = f"{', '.join(feature_tuple)}"
                group_color = shared_colors[shared_color_index % len(shared_colors)]
                shared_color_index += 1
                
            g_node = get_node_id(group_name, "G")
            group_nodes.append(f"{g_node}([\"{group_name}\"])")
            
            group_styles.append(f"    classDef style{g_node} fill:{group_color},stroke:#333,stroke-width:2px,color:#000;")
            group_styles.append(f"    class {g_node} style{g_node};")
            
            # Edges from Features -> Group
            for f_name in feature_tuple:
                f_node = get_node_id(f_name, "F")
                edges.append(f"{f_node} ==> {g_node}")
                link_styles.append(f"    linkStyle {link_index} stroke:{feature_colors[f_name]},stroke-width:3px;")
                link_index += 1
                
            # Edges from Group -> Components
            for comp in comps:
                c_node = get_node_id(comp, "C")
                component_nodes.add(f"{c_node}(\"{comp}\")")
                edges.append(f"{g_node} --> {c_node}")
                link_styles.append(f"    linkStyle {link_index} stroke:{group_color},stroke-width:2px;")
                link_index += 1
                
                # Apply the group's color to the component node
                component_styles.append(f"    classDef style{c_node} fill:{group_color},stroke:#333,stroke-width:2px,color:#000;")
                component_styles.append(f"    class {c_node} style{c_node};")

        mermaid_lines.append("    subgraph Features")
        for node in feature_nodes:
            mermaid_lines.append(f"        {node}")
        mermaid_lines.append("    end")
        
        mermaid_lines.append("    subgraph Groups")
        for node in group_nodes:
            mermaid_lines.append(f"        {node}")
        mermaid_lines.append("    end")
        
        mermaid_lines.append("    subgraph Components")
        for node in component_nodes:
            mermaid_lines.append(f"        {node}")
        mermaid_lines.append("    end")
        
        for edge in edges:
            mermaid_lines.append(f"    {edge}")
            
        for style in feature_styles:
            mermaid_lines.append(style)
            
        for style in group_styles:
            mermaid_lines.append(style)
            
        for style in component_styles:
            mermaid_lines.append(style)
            
        for style in link_styles:
            mermaid_lines.append(style)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(mermaid_lines))

class StructuralDiagramGenerator(BaseDiagramGenerator):
    def __init__(self, layout_json_path: Path):
        self.layout_json_path = Path(layout_json_path)

    def generate(self, output_file: Path) -> None:
        if not self.layout_json_path.exists():
            raise FileNotFoundError(f"{self.layout_json_path} does not exist. Run layout command first.")

        with open(self.layout_json_path, "r", encoding="utf-8") as f:
            root_node = json.load(f)

        mermaid_lines = [
            "%%{init: {'flowchart': {'curve': 'linear'}}}%%",
            "graph LR"
        ]

        node_id_map = {}
        def get_node_id(name: str) -> str:
            if name not in node_id_map:
                node_id_map[name] = f"N{len(node_id_map)}"
            return node_id_map[name]
        
        edges = set()
        nodes_defined = set()

        def process_node(node, current_path=""):
            node_path = f"{current_path}/{node['name']}" if current_path else node["name"]
            node_id = get_node_id(node_path)
            
            is_dir = node["type"] == "directory"
            if is_dir:
                display = f"📁 {node['name']}"
                mermaid_lines.append(f"    {node_id}[\"{display}\"]")
            else:
                display = f"📄 {node['name']}"
                mermaid_lines.append(f"    {node_id}(\"{display}\")")
                
            nodes_defined.add(node_id)
            
            if "children" in node:
                for child in node["children"]:
                    child_id = process_node(child, node_path)
                    edges.add(f"    {node_id} --> {child_id}")
                    
            return node_id

        process_node(root_node)

        for edge in edges:
            mermaid_lines.append(edge)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(mermaid_lines))

class DecompositionDiagramGenerator(BaseDiagramGenerator):
    def __init__(self, decomposition_json_path: Path):
        self.decomposition_json_path = Path(decomposition_json_path)

    def generate(self, output_file: Path) -> None:
        if not self.decomposition_json_path.exists():
            raise FileNotFoundError(f"{self.decomposition_json_path} does not exist. Run decompose command first.")

        with open(self.decomposition_json_path, "r", encoding="utf-8") as f:
            root_node = json.load(f)

        mermaid_lines = [
            "%%{init: {'flowchart': {'curve': 'linear'}}}%%",
            "graph LR"
        ]

        all_features = set()
        def extract_features(node):
            if "features" in node:
                all_features.update(node["features"].keys())
            for child in node.get("children", []):
                extract_features(child)
        extract_features(root_node)
        
        all_features = sorted(list(all_features))
        
        colors = [
            "#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93", 
            "#f15bb5", "#00bbf9", "#00f5d4", "#f4a261", "#e76f51"
        ]
        shared_colors = [
            "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e",
            "#e6ab02", "#a6761d", "#a6cee3", "#1f78b4", "#b2df8a"
        ]
        
        feature_colors = {}
        for i, f_name in enumerate(all_features):
            feature_colors[f_name] = colors[i % len(colors)]
            
        group_colors = {}
        shared_color_index = 0
        def get_color_for_features(features_set):
            if not features_set:
                return None
            f_tuple = tuple(sorted(list(features_set)))
            if len(f_tuple) == 1:
                return feature_colors[f_tuple[0]]
            if f_tuple not in group_colors:
                nonlocal shared_color_index
                group_colors[f_tuple] = shared_colors[shared_color_index % len(shared_colors)]
                shared_color_index += 1
            return group_colors[f_tuple]

        node_id_map = {}
        def get_node_id(name: str) -> str:
            if name not in node_id_map:
                node_id_map[name] = f"N{len(node_id_map)}"
            return node_id_map[name]
        
        styles = []
        
        groups = {}
        def collect_files(node, current_path=""):
            node_path = f"{current_path}/{node['name']}" if current_path else node["name"]
            
            if node["type"] == "directory":
                for child in node.get("children", []):
                    collect_files(child, node_path)
            else:
                features = tuple(sorted(list(node.get("features", {}).keys())))
                if features not in groups:
                    groups[features] = []
                groups[features].append((node_path, node["name"]))

        collect_files(root_node)

        for f_tuple, files in groups.items():
            if not f_tuple:
                group_name = "Unassigned"
                group_color = "#ffffff"
            else:
                group_name = " & ".join(f_tuple)
                group_color = get_color_for_features(set(f_tuple))
            
            sg_id = get_node_id(f"group_{group_name}")
            mermaid_lines.append(f"    subgraph {sg_id} [\"{group_name}\"]")
            
            for node_path, name in files:
                node_id = get_node_id(node_path)
                display = f"📄 {name}"
                mermaid_lines.append(f"        {node_id}(\"{display}\")")
                if group_color != "#ffffff":
                    styles.append(f"    style {node_id} fill:{group_color},stroke:#333,stroke-width:2px,color:#000;")
            
            mermaid_lines.append("    end")
            if group_color != "#ffffff":
                styles.append(f"    style {sg_id} fill:{group_color}33,stroke:{group_color},stroke-width:2px,color:#000;")

        for style in styles:
            mermaid_lines.append(style)

        if all_features:
            mermaid_lines.append("    subgraph Legend")
            for f_name, color in feature_colors.items():
                l_id = get_node_id(f"legend_{f_name}")
                mermaid_lines.append(f"        {l_id}[\"{f_name}\"]")
                mermaid_lines.append(f"        style {l_id} fill:{color},stroke:#333,stroke-width:2px,color:#000;")
                
            for f_tuple, color in group_colors.items():
                l_id = get_node_id(f"legend_{'-'.join(f_tuple)}")
                mermaid_lines.append(f"        {l_id}[\"{' & '.join(f_tuple)}\"]")
                mermaid_lines.append(f"        style {l_id} fill:{color},stroke:#333,stroke-width:2px,color:#000;")
            mermaid_lines.append("    end")

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(mermaid_lines))
