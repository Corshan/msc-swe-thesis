import json
from pathlib import Path

class DecompositionGenerator:
    def __init__(self, layout_json_path: Path, feature_sets_path: Path):
        self.layout_json_path = Path(layout_json_path)
        self.feature_sets_path = Path(feature_sets_path)

    def generate(self, output_file: Path) -> None:
        if not self.layout_json_path.exists():
            raise FileNotFoundError(f"{self.layout_json_path} does not exist. Run 'layout' command first.")
        if not self.feature_sets_path.exists():
            raise FileNotFoundError(f"{self.feature_sets_path} does not exist. Run 'compute' command first.")

        with open(self.layout_json_path, "r", encoding="utf-8") as f:
            layout_tree = json.load(f)

        with open(self.feature_sets_path, "r", encoding="utf-8") as f:
            feature_sets = json.load(f)

        def get_file_features(filename: str):
            result = {}
            for feature_name, sets in feature_sets.items():
                feature_dict = {}
                for set_name, components in sets.items():
                    matching_comps = []
                    for comp in components:
                        if comp == filename or comp.startswith(f"{filename}::"):
                            matching_comps.append(comp)
                    if matching_comps:
                        feature_dict[set_name] = matching_comps
                
                if feature_dict:
                    result[feature_name] = feature_dict
            return result
        
        def annotate_node(node):
            node_features = {}
            if node["type"] == "file":
                features = get_file_features(node["name"])
                if features:
                    node["features"] = features
                    for fname, sets in features.items():
                        if fname not in node_features:
                            node_features[fname] = set()
                        for s in sets.keys():
                            node_features[fname].add(s)
            else:
                for child in node.get("children", []):
                    child_features = annotate_node(child)
                    for fname, sets in child_features.items():
                        if fname not in node_features:
                            node_features[fname] = set()
                        node_features[fname].update(sets)
                
                if node_features:
                    node["features"] = {fname: list(sets) for fname, sets in node_features.items()}
            
            return node_features
            
        annotate_node(layout_tree)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(layout_tree, f, indent=2)
