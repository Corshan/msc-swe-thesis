from arch_recovery.cli.options import test_name_option
from arch_recovery.paths import ProjectPaths
import click
import os
from arch_recovery.pipleline.instrumentor import Instrumentor
from arch_recovery.pipleline.collector import TraceCollector
from arch_recovery.pipleline.analyzer import ReconnaissanceAnalyzer
from arch_recovery.pipleline.diagram_generator import FeatureDiagramGenerator, StructuralDiagramGenerator
from arch_recovery.pipleline.diagram_renderer import DiagramRenderer
from arch_recovery.cli.options import project_path_option, langauage_option, test_command_option, output_option, project_path_src_option, extensions_option, format_option

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
    project_paths = ProjectPaths.from_root(project_path, project_path_src)
    
    instrumentor = Instrumentor(project_paths, language)
    instrumentor.instrument()
    
    click.echo(f"Instrumentation complete for {project_path}")

@cli.command("trace")
@project_path_option
@test_command_option
@test_name_option
def run_tracer(project_path: str, test_command: str, test_name: str):
    """
    Run only the trace collection step for the target project.
    """
    project_paths = ProjectPaths.from_root(project_path, "")

    trace_collector = TraceCollector(project_paths, test_command, test_name)
    trace_collector.collect()
    
    click.echo(f"Trace collection complete for {project_path}")

@cli.command("compute")
@project_path_option
def compute_recon_sets(project_path: str):
    """
    Compute the software reconnaissance sets.
    """
    project_paths = ProjectPaths.from_root(project_path, "")
    
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
    
    analyzer.save_feature_sets(sets, project_paths.output_dir)
    click.echo(f"Saved feature sets to {project_paths.output_dir / 'feature_sets.json'}")

@cli.command("diagram")
@project_path_option
@format_option
def generate_diagram(project_path: str, format: str):
    """
    Generate an architectural diagram from the computed feature sets.
    """
    project_paths = ProjectPaths.from_root(project_path, "")
    feature_sets_path = project_paths.output_dir / "feature_sets.json"
    mmd_output_path = project_paths.diagrams_dir / "architecture.mmd"
    img_output_path = project_paths.diagrams_dir / f"architecture.{format}"
    
    diagram_generator = FeatureDiagramGenerator(feature_sets_path)
    
    try:
        click.echo(f"Generating and rendering architectural feature diagram ({format.upper()})...")
        diagram_generator.generate_and_render(mmd_output_path, img_output_path)
        click.echo(f"Finished. Saved to {img_output_path}")
    except Exception as e:
        click.echo(str(e), err=True)

@cli.command("structure-diagram")
@project_path_option
@project_path_src_option
@extensions_option
@format_option
def generate_structure_diagram(project_path: str, project_path_src: str, extensions: str, format: str):
    """
    Generate a package-level structural diagram of the source code.
    """
    project_paths = ProjectPaths.from_root(project_path, project_path_src)
    mmd_output_path = project_paths.diagrams_dir / "structure.mmd"
    img_output_path = project_paths.diagrams_dir / f"structure.{format}"
    
    allowed_exts = tuple(ext.strip() for ext in extensions.split(",")) if extensions else None
    diagram_generator = StructuralDiagramGenerator(project_paths.src, allowed_extensions=allowed_exts)
    
    try:
        click.echo(f"Generating and rendering package-level structural diagram ({format.upper()})...")
        diagram_generator.generate_and_render(mmd_output_path, img_output_path)
        click.echo(f"Finished. Saved to {img_output_path}")
    except Exception as e:
        click.echo(str(e), err=True)

if __name__ == '__main__':
    cli()
