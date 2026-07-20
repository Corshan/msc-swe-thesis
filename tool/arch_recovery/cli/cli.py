from arch_recovery.cli.options import test_name_option
from arch_recovery.paths import ProjectPaths
import click
import os
import tempfile
import shutil
from arch_recovery.config import Config
from arch_recovery.pipleline.instrumentor import Instrumentor
from arch_recovery.pipleline.collector import TraceCollector
from arch_recovery.pipleline.analyzer import ReconnaissanceAnalyzer
from arch_recovery.pipleline.extractor import StaticExtractor
from arch_recovery.pipleline.mapper import LSIMapper
from arch_recovery.pipleline.engine import ReflexionEngine
from arch_recovery.pipleline.mermaid_generator import MermaidGenerator
from arch_recovery.cli.options import project_path_option, langauage_option, test_command_option, output_option, project_path_src_option

@click.group()
def cli():
    """Automated Software Architecture Recovery CLI."""
    pass

@cli.command("instrument")
@project_path_option
@project_path_src_option
@langauage_option
def instrument_only(project_path: str, project_path_src: str, language: str):
    """
    Run only the instrumentation step for the target project.
    """
    # config = Config(project_path=project_path, project_src_path=project_path_src, language=language, test_command="")
    project_paths = ProjectPaths.from_root(project_path, project_path_src)
    
    instrumentor = Instrumentor(project_paths, language)
    instrumentor.instrument()
    
    click.echo(f"Instrumentation complete for {project_path}")

@cli.command("trace")
@project_path_option
@project_path_src_option
@test_command_option
@test_name_option
def run_tracer(project_path: str, project_path_src: str, test_command: str, test_name: str):
    """
    Run only the trace collection step for the target project.
    """
    project_paths = ProjectPaths.from_root(project_path, project_path_src)

    trace_collector = TraceCollector(project_paths, test_command, test_name)
    trace_collector.collect()
    
    click.echo(f"Trace collection complete for {project_path}")

@cli.command("compute")
@project_path_option
@project_path_src_option
def compute_recon_sets(project_path: str, project_path_src: str):
    """
    Compute the software reconnaissance sets.
    """
    project_paths = ProjectPaths.from_root(project_path, project_path_src)
    
    analyzer = ReconnaissanceAnalyzer()
    traces = analyzer.load_traces(project_paths.trace_dir)
    click.echo(f"Loaded {len(traces)} traces from {project_paths.trace_dir}")

    sets = analyzer.compute_sets(traces)

    for feature in sets:
        click.echo(f"\tFeature: {feature}")
        click.echo(f"\t\tCommon: {len(sets[feature].common)}")
        click.echo(f"\t\tInvolved: {len(sets[feature].involved)}")
        click.echo(f"\t\tEssential: {len(sets[feature].essential)}")
        click.echo(f"\t\tUnique: {len(sets[feature].unique)}")
    
    analyzer.save_feature_sets(sets, project_paths.trace_dir)
    click.echo(f"Saved feature sets to {project_paths.trace_dir / 'feature_sets.json'}")

    

@cli.command()
@project_path_option
@project_path_src_option
@langauage_option
@test_command_option
@output_option
def recover(project_path: str, project_path_src: str, language: str, test_command: str, output: str):
    """
    Run the full architecture recovery pipeline.
    """
    click.echo(f"Starting Architecture Recovery for {project_path}...")
    
    # Config expects both project_path and project_src_path; use the provided project_path for both
    config = Config(project_path=project_path, project_src_path=project_path_src, language=language, test_command=test_command)
   
    # Step 1: Instrumentation
    # instrumentor = Instrumentor(config)
    # instrumentor.instrument()

    click.echo(f"Saving traces to {config.trace_file_path}...")
    
    # Step 2: Trace Collection
    click.echo("Step 2: Collecting execution traces...")
    trace_collector = TraceCollector(config)
    trace_collector.collect()
    
    # # Step 3: Reconnaissance Sets
    # click.echo("Step 3: Computing Software Reconnaissance sets...")
    
    # traces = {}
    # if os.path.exists(config.trace_file_path):
    #     executed = set()
    #     with open(config.trace_file_path, "r", encoding="utf-8") as f:
    #         for line in f:
    #             if line.startswith("ENTER: "):
    #                 executed.add(line.strip()[7:])
    #     traces["test_run_all"] = executed
    # else:
    #     traces = {"test_login": {"auth::login", "db::query"}, "test_logout": {"auth::logout"}}
        
    # analyzer = ReconnaissanceAnalyzer()
    # feature_mapping = {"Feature_0": ["test_run_all"]} if "test_run_all" in traces else {"Feature_0": ["test_login"], "Feature_1": ["test_logout"]}
    # recon_sets = analyzer.compute_sets(traces, feature_mapping)
    
    # for feature, fset in recon_sets.items():
    #     click.echo(f"Feature: {feature}")
    #     click.echo(f"  Common: {len(fset.common)}")
    #     click.echo(f"  Involved: {len(fset.involved)}")
    #     click.echo(f"  Essential: {len(fset.essential)}")
    #     click.echo(f"  Unique: {len(fset.unique)}")
    # Clean up
    # if os.path.exists(config.instrumented_path):
    #     shutil.rmtree(config.instrumented_path)
    
    
    click.echo(f"Done! Results written to {os.path.join(config.project_path, output)}")


if __name__ == '__main__':
    cli()
