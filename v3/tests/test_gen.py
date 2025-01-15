import pytest
from gen import create_project, load_file_contents, load_project_structure

def test_load_file_contents():
    contents = load_file_contents()
    assert isinstance(contents, dict)
    assert len(contents) > 0

def test_load_project_structure():
    structure = load_project_structure()
    assert isinstance(structure, dict)
    assert len(structure) > 0

# Add more tests as needed
