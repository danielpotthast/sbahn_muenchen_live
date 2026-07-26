#!/usr/bin/env python3
"""Validate the SBM HACS integration structure."""

import os
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def validate_integration():
    """Check if all required files exist and are valid."""

    print("🔍 Validating SBM HACS Integration...")
    print()

    errors = []
    warnings = []

    os.chdir(REPO_ROOT)

    # Check root files
    root_files = {
        "hacs.json": "HACS configuration",
        "README.md": "Documentation",
    }

    for filename, description in root_files.items():
        if os.path.exists(filename):
            print(f"✅ {filename} ({description})")
        else:
            errors.append(f"❌ Missing {filename}")

    # Check custom_components/sbahn_muenchen_live directory
    component_dir = "custom_components/sbahn_muenchen_live"
    if not os.path.exists(component_dir):
        errors.append(f"❌ Missing directory: {component_dir}")
        print()
        print("=" * 60)
        print("VALIDATION FAILED")
        for error in errors:
            print(error)
        return False

    # Check component files
    component_files = {
        "__init__.py": "Integration initialization",
        "manifest.json": "Integration manifest",
        "config_flow.py": "Config flow",
        "const.py": "Constants",
        "coordinator.py": "Data update coordinator",
        "sensor.py": "Sensor platform",
        "sbmapi.py": "API wrapper",
        "stations.py": "Static station reference data",
    }

    for filename, description in component_files.items():
        filepath = os.path.join(component_dir, filename)
        if os.path.exists(filepath):
            print(f"✅ {filepath} ({description})")
        else:
            errors.append(f"❌ Missing {filepath}")

    print()

    # Validate manifest.json
    manifest_path = os.path.join(component_dir, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            required_keys = ["domain", "name", "version", "requirements", "codeowners"]
            for key in required_keys:
                if key in manifest:
                    print(f"✅ manifest.json has '{key}'")
                else:
                    warnings.append(f"⚠️  manifest.json missing '{key}'")

            # Check dependencies
            if "requirements" in manifest:
                print(f"   Dependencies: {', '.join(manifest['requirements'])}")

        except json.JSONDecodeError as e:
            errors.append(f"❌ Invalid JSON in manifest.json: {e}")

    # Validate hacs.json
    if os.path.exists("hacs.json"):
        try:
            with open("hacs.json") as f:
                hacs_config = json.load(f)

            if hacs_config.get("name"):
                print(f"✅ HACS name: {hacs_config['name']}")
            if "domains" in hacs_config and "sensor" in hacs_config["domains"]:
                print(f"✅ HACS domain: sensor")

        except json.JSONDecodeError as e:
            errors.append(f"❌ Invalid JSON in hacs.json: {e}")

    print()
    print("=" * 60)

    if errors:
        print("❌ VALIDATION FAILED")
        for error in errors:
            print(error)
        return False

    if warnings:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        for warning in warnings:
            print(warning)
    else:
        print("✅ VALIDATION PASSED")

    print()
    print("📦 Integration Structure:")
    print("   sbm-live/")
    print("   ├── hacs.json")
    print("   ├── README.md")
    print("   └── custom_components/")
    print("       └── sbahn_muenchen_live/")
    print("           ├── __init__.py")
    print("           ├── manifest.json")
    print("           ├── config_flow.py")
    print("           ├── const.py")
    print("           ├── coordinator.py")
    print("           ├── sensor.py")
    print("           ├── sbmapi.py")
    print("           └── stations.py")
    print()
    print("📝 Next Steps:")
    print("   1. Test in Home Assistant by copying custom_components/sbahn_muenchen_live")
    print("      to your Home Assistant config directory")
    print("   2. Restart Home Assistant")
    print("   3. Settings -> Devices & Services -> Add Integration ->")
    print("      \"S-Bahn München Live\", then pick a station")
    print("   4. Check for sensor.airport_departures entity")
    print()

    return True

if __name__ == "__main__":
    import sys
    success = validate_integration()
    sys.exit(0 if success else 1)
