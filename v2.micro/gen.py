import typer
import yaml
import logging
from typing import Dict, Any

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_file_contents() -> Dict[str, str]:
    try:
        with open('file_contents.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        typer.echo("Error: file_contents.yaml not found")
        raise typer.Exit(1)
    except yaml.YAMLError as e:
        typer.echo(f"Error parsing file_contents.yaml: {e}")
        raise typer.Exit(1)

def load_project_structure() -> Dict[str, Any]:
    try:
        with open('project_structure.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        typer.echo("Error: project_structure.yaml not found")
        raise typer.Exit(1)
    except yaml.YAMLError as e:
        typer.echo(f"Error parsing project_structure.yaml: {e}")
        raise typer.Exit(1)

def create_project(structure: Dict[str, Any], file_contents: Dict[str, str], root: str = '') -> None:
    """
    Creates project structure from the given dictionary.

    Args:
        structure (dict): Project structure definition
        file_contents (dict): File content templates
        root (str, optional): Root directory for project. Defaults to current directory.
    """
    # ...existing code...

@app.command()
def generate(
    output_dir: str = typer.Option(".", help="Output directory for the generated project"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    if verbose:
        logger.setLevel(logging.DEBUG)
    project_structure = load_project_structure()
    file_contents = load_file_contents()
    create_project(project_structure, file_contents, output_dir)
    typer.echo(f"Project structure created successfully in {output_dir}")

if __name__ == "__main__":
    app()
