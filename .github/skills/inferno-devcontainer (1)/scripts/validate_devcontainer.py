#!/usr/bin/env python3
"""
Validate an Inferno-OS devcontainer configuration.
Checks devcontainer.json, Dockerfile, scripts, and cluster config for correctness.
"""

import json
import os
import sys
from pathlib import Path


class Validator:
    """Validate Inferno-OS devcontainer configuration."""

    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.devcontainer_dir = self.project_dir / ".devcontainer"
        self.errors = []
        self.warnings = []

    def error(self, msg: str):
        self.errors.append(f"  ✗ {msg}")

    def warn(self, msg: str):
        self.warnings.append(f"  ⚠ {msg}")

    def ok(self, msg: str):
        print(f"  ✓ {msg}")

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
        if "dockerfile" in build:
            dockerfile = self.devcontainer_dir / build["dockerfile"]
            if dockerfile.exists():
                self.ok(f"Dockerfile found: {build['dockerfile']}")
            else:
                self.error(f"Dockerfile not found: {dockerfile}")
        else:
            self.error("No dockerfile specified in build config")

        # Check Inferno-specific env vars
        env = config.get("containerEnv", {})
        inferno_vars = ["INFERNO_ROOT", "EMU", "LIMBO", "PATH"]
        for var in inferno_vars:
            if var in env:
                self.ok(f"Environment variable '{var}' configured")
            else:
                self.warn(f"Missing recommended env var: {var}")

        # Check port forwarding for 9P
        ports = config.get("forwardPorts", [])
        if 6666 in ports:
            self.ok("9P/Styx port 6666 forwarded")
        else:
            self.warn("9P/Styx port 6666 not in forwardPorts")

        # Check features
        features = config.get("features", {})
        if features:
            self.ok(f"{len(features)} devcontainer features configured")
        else:
            self.warn("No devcontainer features configured")

    def validate_dockerfile(self):
        """Validate Dockerfile for Inferno-OS build requirements."""
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

        # Check for Inferno build steps
        checks = [
            ("inferno-os", "Inferno-OS source clone/copy"),
            ("mkconfig", "mkconfig configuration"),
            ("makemk.sh", "mk bootstrap (makemk.sh)"),
            ("mk install", "mk install build step"),
            ("emu", "emu emulator reference"),
            ("limbo", "Limbo compiler reference"),
        ]
        for pattern, desc in checks:
            if pattern in content:
                self.ok(f"{desc} found")
            else:
                self.warn(f"{desc} not found in Dockerfile")

        # Check for X11 support
        if "libx11" in content.lower():
            self.ok("X11 development libraries included")
        else:
            self.warn("X11 libraries not found — GUI support may be limited")

    def validate_scripts(self):
        """Validate devcontainer lifecycle scripts."""
        print("\n[3] Validating scripts...")
        scripts_dir = self.devcontainer_dir / "scripts"

        required_scripts = ["post-create.sh", "post-start.sh"]
        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            if script_path.exists():
                self.ok(f"Script found: {script_name}")
                # Check executable
                if os.access(script_path, os.X_OK):
                    self.ok(f"  {script_name} is executable")
                else:
                    self.warn(f"  {script_name} is not executable")
            else:
                self.warn(f"Script not found: {script_name}")

    def validate_cluster_config(self):
        """Validate cluster deployment configuration."""
        print("\n[4] Validating cluster configuration...")
        compose_file = self.project_dir / "docker-compose.cluster.yml"

        if compose_file.exists():
            self.ok("docker-compose.cluster.yml found")
            content = compose_file.read_text()
            if "inferno-registry" in content:
                self.ok("Registry node defined")
            if "inferno-node" in content:
                self.ok("Worker nodes defined")
            if "inferno-net" in content:
                self.ok("Cluster network defined")
        else:
            self.warn("docker-compose.cluster.yml not found — cluster deployment unavailable")

    def run(self) -> bool:
        """Run all validations and report results."""
        print("=" * 60)
        print("Inferno-OS Devcontainer Validation")
        print(f"Project: {self.project_dir}")
        print("=" * 60)

        self.validate_devcontainer_json()
        self.validate_dockerfile()
        self.validate_scripts()
        self.validate_cluster_config()

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
            print(f"\n✗ Validation FAILED with {len(self.errors)} error(s)")
            return False
        else:
            print(f"\n✓ Validation PASSED ({len(self.warnings)} warning(s))")
            return True


if __name__ == "__main__":
    project_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    validator = Validator(project_dir)
    success = validator.run()
    sys.exit(0 if success else 1)
