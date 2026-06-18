import os
from typing import Dict, List, Tuple

class MermaidGenerator:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def generate(self, 
                 feature_mapping: Dict[str, List[str]], 
                 reflexion_results: Dict[str, List[Tuple[str, str]]]) -> None:
        """
        Generates a styled Mermaid.js graph embedded in a Markdown document.
        """
        md_content = [
            "# Architecture Recovery Report\n",
            "## Feature Architecture Reflexion Model\n",
            "This document contains the automatically recovered software architecture based on dynamic traces and static LSI mappings.\n",
            "```mermaid",
            "graph TD",
            "    %% Styling",
            "    classDef convergence fill:#d4edda,stroke:#28a745,stroke-width:2px;",
            "    classDef divergence fill:#f8d7da,stroke:#dc3545,stroke-width:2px;",
            "    classDef absence fill:#fff3cd,stroke:#ffc107,stroke-width:2px,stroke-dasharray: 5 5;",
            "    classDef feature fill:#e2e3e5,stroke:#6c757d,stroke-width:2px;"
        ]

        # 1. Add Features (Clusters)
        for feature in feature_mapping.keys():
            md_content.append(f"    {feature}[{feature}]:::feature")

        # 2. Add Reflexion Edges (Lifted edges for now, with classes)
        # We use lifted_edges for the high-level architecture diagram.
        convergences = reflexion_results.get("convergences", [])
        divergences = reflexion_results.get("divergences", [])
        absences = reflexion_results.get("absences", [])
        lifted_edges = reflexion_results.get("lifted_edges", [])

        md_content.append("\n    %% Lifted Dependencies")
        for src, dest in lifted_edges:
            md_content.append(f"    {src} --> {dest}")

        # If we had feature-level convergences/divergences, we would style them:
        # For simplicity, we just list the edges. A full implementation would apply 
        # the convergence/divergence class to the links or nodes.
        
        md_content.extend([
            "```",
            "\n## Component Details\n"
        ])

        for feature, components in feature_mapping.items():
            md_content.append(f"### {feature}")
            for comp in components:
                md_content.append(f"- `{comp}`")
            md_content.append("")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_content))
            
        print(f"Mermaid report generated at {self.output_path}")
