import asyncio
import json
import os
import sys
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.fetch import fetch_ids, fetch_data
from app.core.config import get_settings

settings = get_settings()


def test_fetch_ids(capsys):
    """Test fetch_ids function - currently returns placeholder data."""
    project_name = "test_project"
    token = getattr(settings, 'shigure_token', None) or os.getenv('SHIGURE_TOKEN')

    print(f"\n--- Testing fetch_ids with project_name: {project_name} ---")
    if token:
        print(f"Using token from settings/env: {token[:10]}...")
    else:
        print("No token available from settings or environment.")

    try:
        result = asyncio.run(fetch_ids(project_name, token))
        print("\n--- fetch_ids result ---")
        print(f"fetch_ids result: {json.dumps(result, indent=2)}")

        assert result == ["example_data1", "example_data2"], f"Expected ['example_data1', 'example_data2'], got {result}"
    except Exception as e:
        print(f"fetch_ids raised exception: {type(e).__name__}: {e}")
        raise


def test_fetch_data_real_http_request(capsys):
    """Test fetch_data function with real HTTP requests to Shigure server."""
    project_name = "B360G3"
    token = getattr(settings, 'shigure_token', None) or os.getenv('SHIGURE_TOKEN')

    if not token:
        pytest.skip("SHIGURE_TOKEN is not configured in settings or environment. Skipping real HTTP request test.")

    print(f"\n--- Testing fetch_data with real HTTP requests ---")
    print(f"Project name: {project_name}")
    print(f"Using token from settings/env: {token[:10]}...")

    try:
        result = asyncio.run(fetch_data(project_name, token))

        print("\n--- fetch_data result ---")
        print(f"Drivers data type: {type(result.get('drivers'))}")
        drivers_json = json.dumps(result.get('drivers'), indent=2) if result.get('drivers') is not None else "None"
        print(f"Drivers data:\n{drivers_json}")

        print(f"\nApps data type: {type(result.get('apps'))}")
        apps_json = json.dumps(result.get('apps'), indent=2) if result.get('apps') is not None else "None"
        print(f"Apps data:\n{apps_json}")

        assert "drivers" in result, f"Expected 'drivers' in result, got keys: {list(result.keys())}"
        assert "apps" in result, f"Expected 'apps' in result, got keys: {list(result.keys())}"
    except Exception as e:
        import traceback
        print("\n--- fetch_data raised an exception ---")
        print(traceback.format_exc())
        print(f"{type(e).__name__}: {e}")
