# Configure Python environment for test
# ---- Basics ----
import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import glob
import random
from typing import List, Union
from pathlib import Path, PosixPath

from starlette.testclient import TestClient

# ---- cell-instance-segmentation-_API modules ----
from api.main import app
from unet.model import get_model
from mocks import MockModel


# Call the mock model
def get_model_override():
    model = MockModel()
    return model

# Dependency injection
app.dependency_overrides[get_model] = get_model_override


@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def image_path():
    return Path(os.path.join(os.path.dirname(__file__), 'images'))

@pytest.fixture
def generate_multipartformdata(input: Union[Path, List[Path]]) -> List:
    """Generate multipart/form-data from input list"""
    files = []

    if type(input) == PosixPath:
        filename = input.name
        mime = f'image/{input.suffix[1:]}'
        files.append((filename, input.open(), mime))

    else:
        
        for fp in input: 
            filename = fp.name
            mime = f'image/{fp.suffix[1:]}'
            files.append((filename, fp.open(), mime))

    return files

@pytest.fixture
def fake_txt():
    fp = Path('fake.txt')
    return (fp.name, fp.open(), 'text/plain')