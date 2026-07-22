import click 

LANGUAGES = ["python", "java", "cpp"]

def langauage_option(func):
    return click.option(
        '--language', 
        '-l', 
        type=click.Choice(LANGUAGES), 
        required=True, 
        help="Target system language (e.g. python, java, cpp)"
    )(func)

def project_path_option(func):
    return click.option(
        '--project-path', 
        '-p', 
        type=click.Path(exists=True, file_okay=False), 
        required=True, 
        help="Path to the project directory"
    )(func)

def project_path_src_option(func):
    return click.option(
        '--project-path-src', 
        '-s', 
        type=click.Path(exists=True, file_okay=False), 
        required=True, 
        help="Path to the project source directory"
    )(func)

def test_command_option(func):
    return click.option(
        '--test-command', 
        '-tc', 
        type=str, 
        required=True, 
        help="Command to run the feature test suites (e.g., 'pytest')"
    )(func)

def test_name_option(func):
    return click.option(
        '--test-name', 
        '-tn', 
        type=str, 
        required=True, 
        help="Name of the test to run (e.g., 'test_login')"
    )(func)

def output_option(func):
    return click.option(
        '--output', 
        '-o', 
        type=click.Path(), 
        default="architecture_recovery.md", 
        help="Output markdown file"
    )(func)

def extensions_option(func):
    return click.option(
        '--extensions', 
        '-e', 
        type=str, 
        default="", 
        help="Comma-separated list of allowed file extensions (e.g., '.py,.md'). If empty, all non-hidden files are included."
    )(func)

def format_option(func):
    return click.option(
        '--format', 
        '-f', 
        type=click.Choice(["svg", "png", "pdf"]), 
        default="svg", 
        help="Output image format for the diagram."
    )(func)