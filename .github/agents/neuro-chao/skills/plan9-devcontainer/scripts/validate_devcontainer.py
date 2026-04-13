#!/usr/bin/env python3
"""
Validate a Plan 9 devcontainer configuration.
Checks devcontainer.json, Dockerfile, scripts, and grid config for correctness.
"""

import json
import os
import sys
from pathlib import Path


class Validator:
    """Validate Plan 9 devcontainer configuration."""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.devcontainer_dir = self.project_dir / ".devcontainer"
        self.errors = []
        self.warnings = []

    def error(self, msg: str):
        self.errors.append(f"  - {msg}")

    def warn(self, msg: str):
        self.warnings.append(f"  ! {msg}")

    def ok(self, msg: str):
        print(f"  + {msg}")

    def validate_devcontainer_json(self):
        """Validate devcontainer.json structure and required fields."""
        print("\n[1] Validating devcontainer.json...")
        json_path = self.devcontainer_dir / "devcontainer.json"

        if not json_path.exists():
            self.error("devcontainer.json not found")
            return

        try:
            with open(json_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.error(f"Invalid JSON: {e}")
            return

        # Required fields
        required = ["name", "build", "containerEnv"]
        for field in required:
            if field in config:
                self.ok(f"Field '{field}' present")
            else:
                self.error(f"Missing required field: {field}")

        # Check build config
        build = config.get("build", {})
        dockerfile_name = build.get("dockerfile", "Dockerfile")
        dockerfile = self.devcontainer_dir / dockerfile_name
        if dockerfile.exists():
            self.ok(f"Dockerfile found: {dockerfile_name}")
        else:
            self.error(f"Dockerfile not found: {dockerfile}")

        # Check Plan 9 specific env vars
        env = config.get("containerEnv", {})
        plan9_vars = ["PLAN9", "PATH"]
        for var in plan9_vars:
            if var in env:
                self.ok(f"Environment variable '{var}' configured")
            else:
                self.warn(f"Missing recommended env var: {var}")

        # Check port forwarding for 9P2000
        ports = config.get("forwardPorts", [])
        if 564 in ports:
            self.ok("9P2000 port 564 forwarded")
        else:
            self.warn("9P2000 port 564 not in forwardPorts")

        # Check features
        features = config.get("features", {})
        if features:
            self.ok(f"{len(features)} devcontainer features configured")
        else:
            self.warn("No devcontainer features configured")

    def validate_dockerfile(self):
        """Validate Dockerfile for Plan 9 build requirements."""
        print("\n[2] Validating Dockerfile...")
        dockerfile = self.devcontainer_dir / "Dockerfile"

        if not dockerfile.exists():
            self.error("Dockerfile not found")
            return

        content = dockerfile.read_text()

        # Check for multi-stage build
        if content.count("FROM ") >= 2:
            self.ok("Multi-stage build detected")
        else:
            self.warn("Single-stage build — consider multi-stage for smaller images")

        # Check for Plan 9 build steps
        checks = [
            ("plan9port", "plan9port source reference"),
            ("QEMU", "QEMU emulator"),
            ("qemu", "QEMU emulator"),
            ("9front", "9front fork reference"),
            ("mk", "mk build system"),
            ("acme", "acme editor reference"),
            ("rc", "rc shell reference"),
        ]
        found_qemu = False
        for pattern, desc in checks:
            if pattern.lower() in content.lower():
                self.ok(f"{desc} found")
                if "qemu" in pattern.lower():
                    found_qemu = True
            else:
                if "qemu" in pattern.lower() and found_qemu:
                    continue
                self.warn(f"{desc} not found in Dockerfile")

    def validate_scripts(self):
        """Validate devcontainer lifecycle scripts."""
        print("\n[3] Validating scripts...")
        scripts_dir = self.devcontainer_dir / "scripts"

        required_scripts = ["post-create.sh", "post-start.sh"]
        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            if script_path.exists():
                self.ok(f"Script found: {script_name}")
                if os.access(script_path, os.X_OK):
                    self.ok(f"  {script_name} is executable")
                else:
                    self.warn(f"  {script_name} is not executable")
            else:
                self.warn(f"Script not found: {script_name}")

    def validate_grid_config(self):
        """Validate grid deployment configuration."""
        print("\n[4] Validating grid configuration...")
        compose_file = self.project_dir / "docker-compose.grid.yml"

        if compose_file.exists():
            self.ok("docker-compose.grid.yml found")
            content = compose_file.read_text()
            if "plan9-registry" in content:
                self.ok("Registry/auth node defined")
            if "plan9-cpu" in content:
                self.ok("CPU server nodes defined")
            if "plan9-net" in content:
                self.ok("Grid network defined")
        else:
            self.warn("docker-compose.grid.yml not found — grid deployment unavailable")

    def run(self) -> bool:
        """Run all validations and report results."""
        print("=" * 60)
        print("Plan 9 Devcontainer Validation")
        print(f"Project: {self.project_dir}")
        print("=" * 60)

        self.validate_devcontainer_json()
        self.validate_dockerfile()
        self.validate_scripts()
        self.validate_grid_config()

        print("\n" + "=" * 60)
        print("Results:")
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(w)
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for e in self.errors:
                print(e)
            print(f"\n- Validation FAILED with {len(self.errors)} error(s)")
            return False
        else:
            print(f"\n+ Validation PASSED ({len(self.warnings)} warning(s))")
            return True


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    validator = Validator(project_dir)
    success = validator.run()
    sys.exit(0 if success else 1)
