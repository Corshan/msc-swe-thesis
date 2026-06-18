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

def test_command_option(func):
    return click.option(
        '--test-command', 
        '-tc', 
        type=str, 
        required=True, 
        help="Command to run the feature test suites (e.g., 'pytest')"
    )(func)

def output_option(func):
    return click.option(
        '--output', 
        '-o', 
        type=click.Path(), 
        default="architecture_recovery.md", 
        help="Output markdown file"
    )(func)