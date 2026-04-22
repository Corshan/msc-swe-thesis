import gradio as gr
import os
import pandas as pd
from core.parser import load_profile
from core.recon_calc import ReconAnalyzer
from core.reporter import generate_html_report

# Global state to keep track of features and test cases
# In a real app, this would be per-session
state = {
    "test_cases": {}, # filename -> set(procedures)
    "features": [],   # list of {name: str, test_cases: list[str]}
}

def add_test_case(files):
    if not files:
        return gr.update(), "No files uploaded."
    
    new_names = []
    for file in files:
        name = os.path.basename(file.name)
        state["test_cases"][name] = load_profile(file.name)
        new_names.append(name)
    
    tc_list = list(state["test_cases"].keys())
    return gr.update(choices=tc_list), f"Added {len(new_names)} test cases: {', '.join(new_names)}"

def add_feature(name, selected_test_cases):
    if not name or name == "Enter Feature Name":
        return gr.update(), "Please enter a valid feature name."
    
    state["features"].append({
        "name": name,
        "test_cases": selected_test_cases
    })
    
    feature_names = [f["name"] for f in state["features"]]
    return gr.update(choices=feature_names), f"Added feature: {name}"

def run_analysis():
    if not state["test_cases"]:
        return "Error: No test cases loaded."
    if not state["features"]:
        return "Error: No features defined."
    
    features = [f["name"] for f in state["features"]]
    testcases = list(state["test_cases"].keys())
    mapping = [f["test_cases"] for f in state["features"]]
    
    def profile_loader(name):
        return state["test_cases"].get(name, set())

    analyzer = ReconAnalyzer(features, testcases, mapping, profile_loader)
    results = analyzer.analyze_all()
    
    html = generate_html_report(results)
    return html

def reset_state():
    state["test_cases"] = {}
    state["features"] = []
    return gr.update(choices=[]), gr.update(choices=[]), "State reset."

with gr.Blocks(title="ReconCalc Python Pro") as demo:
    gr.Markdown("# 🚀 ReconCalc Python Pro")
    gr.Markdown("Map software features to code elements using Software Reconnaissance.")
    
    with gr.Tab("1. Load Profiles"):
        file_input = gr.File(label="Upload Execution Profiles (.pro, .txt)", file_count="multiple")
        load_btn = gr.Button("Load Profiles")
        tc_msg = gr.Markdown()
        
    with gr.Tab("2. Define Features"):
        with gr.Row():
            with gr.Column():
                feat_name = gr.Textbox(label="Feature Name", placeholder="e.g., Rotate House")
                tc_select = gr.CheckboxGroup(label="Exhibited by Test Cases", choices=[])
                add_feat_btn = gr.Button("Add Feature")
            with gr.Column():
                feat_list = gr.Dropdown(label="Current Features", choices=[])
                feat_msg = gr.Markdown()
                
    with gr.Tab("3. Results"):
        run_btn = gr.Button("Run Analysis", variant="primary")
        output_html = gr.HTML(label="Report")
        
    reset_btn = gr.Button("Reset Everything", variant="stop")

    # Interactivity
    load_btn.click(add_test_case, inputs=[file_input], outputs=[tc_select, tc_msg])
    add_feat_btn.click(add_feature, inputs=[feat_name, tc_select], outputs=[feat_list, feat_msg])
    run_btn.click(run_analysis, outputs=[output_html])
    reset_btn.click(reset_state, outputs=[tc_select, feat_list, tc_msg])

if __name__ == "__main__":
    demo.launch()
