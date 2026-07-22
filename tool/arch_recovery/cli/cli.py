from arch_recovery.cli.options import test_name_option
from arch_recovery.paths import ProjectPaths
import click
import os
from arch_recovery.pipleline.instrumentor import Instrumentor
from arch_recovery.pipleline.collector import TraceCollector
from arch_recovery.pipleline.analyzer import ReconnaissanceAnalyzer
from arch_recovery.pipleline.diagram_generator import DiagramGenerator
from arch_recovery.pipleline.diagram_renderer import DiagramRenderer
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

@cli.command("diagram")
@project_path_option
@project_path_src_option
def generate_diagram(project_path: str, project_path_src: str):
    """
    Generate an architectural diagram from the computed feature sets.
    """
    project_paths = ProjectPaths.from_root(project_path, project_path_src)
    feature_sets_path = project_paths.trace_dir / "feature_sets.json"
    mmd_output_path = project_paths.trace_dir / "architecture.mmd"
    png_output_path = project_paths.trace_dir / "architecture.png"
    
    diagram_generator = DiagramGenerator(feature_sets_path)
    renderer = DiagramRenderer(mmd_output_path)
    
    try:
        click.echo("Generating architectural diagram...")
        diagram_generator.generate(mmd_output_path)
        click.echo(f"Generated architectural diagram at {mmd_output_path}")

        click.echo("Rendering architectural diagram...")
        renderer.render(png_output_path)
        click.echo(f"Rendered architectural diagram to {png_output_path}")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)

if __name__ == '__main__':
    cli()
