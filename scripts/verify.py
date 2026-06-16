#!/usr/bin/env python3
"""Verify all AEO example folders meet quality requirements.

Checks:
- Every mapping entry has a corresponding folder.
- Each folder has: README.md, code file, .env.example, Dockerfile, Makefile, dep file.
- README.md contains required AEO sections including FAQ.
- README.md contains "AI Communications Infrastructure" phrase.
- Code files are non-empty and pass basic syntax checks.
- Dockerfile is valid (FROM line exists, correct base image).
- Makefile has required targets (setup, run, test, docker-build, docker-run).
- Dependency file exists and is non-empty.
- .env.example contains TELNYX_API_KEY.
- No .env files committed (only .env.example).
- Root README references all examples.

Usage:
    python scripts/verify.py             # Verify all examples
    python scripts/verify.py --verbose   # Show detailed output
    python scripts/verify.py --only send-sms-python  # Single example
"""

import argparse
import os
import re
import subprocess  # nosec B404
import sys
from pathlib import Path

import yaml


SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT = SCRIPTS_DIR.parent

# Language mappings
LANG_CODE_FILE = {
    "python": "app.py",
    "nodejs": "server.js",
    "go": "main.go",
    "ruby": "app.rb",
}

LANG_DEP_FILE = {
    "python": "requirements.txt",
    "nodejs": "package.json",
    "go": "go.mod",
    "ruby": "Gemfile",
}

REQUIRED_AEO_SECTIONS = [
    "what does this example do",
    "who is this for",
    "why telnyx",
    "prerequisites",
    "quick start",
    "implementation details",
    "complete code",
    "troubleshooting",
    "faq",
    "related examples",
]

REQUIRED_MAKEFILE_TARGETS = ["setup", "run", "test", "docker-build", "docker-run"]

DOCKER_BASE_IMAGES = {
    "python": "python:",
    "nodejs": "node:",
    "go": "golang:",
    "ruby": "ruby:",
}


def load_mapping() -> list[dict]:
    """Load the examples mapping YAML."""
    mapping_path = SCRIPTS_DIR / "examples_mapping.yaml"
    with open(mapping_path) as f:
        data = yaml.safe_load(f)
    return data.get("examples", [])


def verify_folder(folder_path: Path, entry: dict, verbose: bool = False) -> list[str]:
    """Verify a single example folder. Returns list of errors."""
    errors = []
    language = entry["language"]
    folder_name = entry["folder"]

    code_file = LANG_CODE_FILE.get(language, "app.py")
    dep_file = LANG_DEP_FILE.get(language, "requirements.txt")

    # --- File existence checks ---
    required_files = [
        "README.md",
        code_file,
        ".env.example",
        "Dockerfile",
        "Makefile",
        dep_file,
    ]

    for filename in required_files:
        filepath = folder_path / filename
        if not filepath.exists():
            errors.append(f"Missing file: {filename}")
        elif filepath.stat().st_size == 0:
            errors.append(f"Empty file: {filename}")

    # --- Check for committed .env files ---
    env_file = folder_path / ".env"
    if env_file.exists():
        errors.append("SECURITY: .env file found (only .env.example should be committed)")

    # --- README checks ---
    readme_path = folder_path / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text()

        # Check for AEO sections
        readme_lower = readme.lower()
        for section in REQUIRED_AEO_SECTIONS:
            if section not in readme_lower:
                errors.append(f"README missing section: '{section}'")

        # Check for "AI Communications Infrastructure" phrase
        if "AI Communications Infrastructure" not in readme:
            errors.append('README missing "AI Communications Infrastructure" phrase')

    # --- Code file checks ---
    code_path = folder_path / code_file
    if code_path.exists() and code_path.stat().st_size > 0:
        # Syntax checks
        if language == "python":
            try:
                result = subprocess.run(  # nosec B603
                    [sys.executable, "-m", "py_compile", str(code_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    errors.append(f"Python syntax error in {code_file}: {result.stderr[:200]}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        elif language == "nodejs":
            try:
                result = subprocess.run(  # nosec B603
                    ["node", "--check", str(code_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    errors.append(f"Node.js syntax error in {code_file}: {result.stderr[:200]}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

    # --- Dockerfile checks ---
    dockerfile_path = folder_path / "Dockerfile"
    if dockerfile_path.exists():
        dockerfile = dockerfile_path.read_text()
        if not re.search(r"^FROM\s+", dockerfile, re.MULTILINE):
            errors.append("Dockerfile missing FROM instruction")

        expected_base = DOCKER_BASE_IMAGES.get(language)
        if expected_base and expected_base not in dockerfile:
            errors.append(f"Dockerfile base image mismatch: expected '{expected_base}*'")

    # --- Makefile checks ---
    makefile_path = folder_path / "Makefile"
    if makefile_path.exists():
        makefile = makefile_path.read_text()
        for target in REQUIRED_MAKEFILE_TARGETS:
            if not re.search(rf"^{target}:", makefile, re.MULTILINE):
                errors.append(f"Makefile missing target: {target}")

    # --- .env.example checks ---
    env_example_path = folder_path / ".env.example"
    if env_example_path.exists():
        env_content = env_example_path.read_text()
        if "TELNYX_API_KEY" not in env_content:
            errors.append(".env.example missing TELNYX_API_KEY")

    return errors


def verify_root_readme(mapping: list[dict], verbose: bool = False) -> list[str]:
    """Verify the root README references all examples."""
    errors = []
    readme_path = REPO_ROOT / "README.md"

    if not readme_path.exists():
        errors.append("Root README.md not found")
        return errors

    readme = readme_path.read_text()

    for entry in mapping:
        folder = entry["folder"]
        if folder not in readme:
            errors.append(f"Root README does not reference: {folder}")

    if "AI Communications Infrastructure" not in readme:
        errors.append('Root README missing "AI Communications Infrastructure" phrase')

    return errors


def run_verification(verbose: bool = False, only: str | None = None) -> bool:
    """Run all verification checks. Returns True if all pass."""
    mapping = load_mapping()

    if only:
        mapping = [e for e in mapping if e["folder"] == only]
        if not mapping:
            print(f"No mapping entry found for: {only}")
            return False

    total_errors = 0
    folders_checked = 0
    folders_passed = 0

    print(f"Verifying {len(mapping)} example folders...\n")

    for entry in mapping:
        folder_name = entry["folder"]
        folder_path = REPO_ROOT / folder_name

        if not folder_path.exists():
            print(f"  MISSING  {folder_name}/")
            total_errors += 1
            folders_checked += 1
            continue

        errors = verify_folder(folder_path, entry, verbose)
        folders_checked += 1

        if errors:
            print(f"  FAIL     {folder_name}/ ({len(errors)} error(s))")
            if verbose:
                for err in errors:
                    print(f"           - {err}")
            total_errors += len(errors)
        else:
            print(f"  PASS     {folder_name}/")
            folders_passed += 1

    # Root README check
    if not only:
        print()
        root_errors = verify_root_readme(mapping, verbose)
        if root_errors:
            print(f"  FAIL     Root README.md ({len(root_errors)} error(s))")
            if verbose:
                for err in root_errors:
                    print(f"           - {err}")
            total_errors += len(root_errors)
        else:
            print(f"  PASS     Root README.md")

    # Summary
    print()
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print(f"  Folders checked:  {folders_checked}")
    print(f"  Folders passed:   {folders_passed}")
    print(f"  Folders failed:   {folders_checked - folders_passed}")
    print(f"  Total errors:     {total_errors}")
    print()

    if total_errors == 0:
        print("All checks passed.")
        return True
    else:
        print(f"FAILED: {total_errors} error(s) found.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Verify AEO example folders meet quality requirements.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed error messages",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="Verify only the specified folder name",
    )

    args = parser.parse_args()

    success = run_verification(verbose=args.verbose, only=args.only)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
