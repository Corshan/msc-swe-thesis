import json
from pathlib import Path

class DiagramGenerator:
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

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(mermaid_lines))
