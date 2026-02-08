import json
import sys
from pathlib import Path

# Add the sidecar directory to the path so we can import from main
sidecar_dir = Path(__file__).parent.parent
sys.path.append(str(sidecar_dir))

from main import app  # noqa: E402


def generate_openapi():
    # Ensure the output directory exists
    output_dir = sidecar_dir.parent / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export OpenAPI schema
    openapi_schema = app.openapi()

    output_file = output_dir / "openapi.json"
    with open(output_file, "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"✅ OpenAPI schema generated at {output_file}")


if __name__ == "__main__":
    generate_openapi()
