#!/usr/bin/env python3
"""Generate API.md and GUIDE.md for new example folders, remove forbidden files.

Reads each example's source code and README.md to generate:
- API.md: endpoint reference derived from route definitions
- GUIDE.md: step-by-step tutorial derived from README content

Also removes forbidden scaffolding files (Dockerfile, Makefile, etc.).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LANG_MAP = {
    "python": {"code": "app.py", "dep": "requirements.txt", "run": "python app.py", "install": "pip install -r requirements.txt", "lang_label": "Python"},
    "nodejs": {"code": "server.js", "dep": "package.json", "run": "node server.js", "install": "npm install", "lang_label": "Node.js"},
    "go": {"code": "main.go", "dep": "go.mod", "run": "go run main.go", "install": "go mod tidy", "lang_label": "Go"},
    "ruby": {"code": "app.rb", "dep": "Gemfile", "run": "ruby app.rb", "install": "bundle install", "lang_label": "Ruby"},
    "php": {"code": "index.php", "dep": "composer.json", "run": "php -S localhost:5000 index.php", "install": "composer install", "lang_label": "PHP"},
    "java": {"code": "*.java", "dep": "pom.xml", "run": "mvn spring-boot:run", "install": "mvn clean install", "lang_label": "Java"},
    "csharp": {"code": "*.cs", "dep": "*.csproj", "run": "dotnet run", "install": "dotnet restore", "lang_label": "C#"},
}

FORBIDDEN = ["Dockerfile", "Makefile", "docker-compose.yml", "docker-compose.yaml", "Procfile"]


def detect_lang(folder_name: str) -> str | None:
    for suffix in LANG_MAP:
        if folder_name.endswith(f"-{suffix}"):
            return suffix
    return None


def human_title(folder_name: str) -> str:
    """Convert folder name to human-readable title."""
    lang = detect_lang(folder_name)
    if lang:
        base = folder_name[:-(len(lang) + 1)]
    else:
        base = folder_name
    return base.replace("-", " ").title()


def extract_readme_sections(readme_path: Path) -> dict:
    """Extract key sections from README.md."""
    if not readme_path.exists():
        return {}
    text = readme_path.read_text()
    sections = {}

    # Title (first H1)
    m = re.search(r"^# (.+)$", text, re.MULTILINE)
    if m:
        sections["title"] = m.group(1).strip()

    # Description (first paragraph after "What Does This Example Do?")
    m = re.search(r"## What Does This Example Do\?\s*\n\n(.+?)(?:\n\n|\n##)", text, re.DOTALL)
    if m:
        sections["description"] = m.group(1).strip()

    # Prerequisites
    m = re.search(r"## Prerequisites\s*\n\n((?:- .+\n?)+)", text)
    if m:
        sections["prerequisites"] = m.group(1).strip()

    # Resources
    m = re.search(r"## Resources\s*\n\n((?:- .+\n?)+)", text, re.DOTALL)
    if m:
        sections["resources"] = m.group(1).strip()

    return sections


def extract_env_vars(env_path: Path) -> list[tuple[str, str]]:
    """Extract env var names and example values from .env.example."""
    if not env_path.exists():
        return []
    result = []
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            result.append((key.strip(), val.strip()))
    return result


# --- Route extraction per language ---

def extract_routes_python(code: str) -> list[dict]:
    routes = []
    for m in re.finditer(r'@app\.route\(\s*"([^"]+)"\s*(?:,\s*methods\s*=\s*\[([^\]]+)\])?\)', code):
        path = m.group(1)
        methods = m.group(2)
        if methods:
            for method in re.findall(r'"(\w+)"', methods):
                routes.append({"method": method.upper(), "path": path})
        else:
            routes.append({"method": "GET", "path": path})
    return routes


def extract_routes_nodejs(code: str) -> list[dict]:
    routes = []
    for m in re.finditer(r'(?:app|router)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', code, re.IGNORECASE):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    return routes


def extract_routes_go(code: str) -> list[dict]:
    routes = []
    for m in re.finditer(r'router\.(GET|POST|PUT|DELETE|PATCH)\(\s*"([^"]+)"', code):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    return routes


def extract_routes_ruby(code: str) -> list[dict]:
    routes = []
    for m in re.finditer(r"(get|post|put|delete|patch)\s+['\"]([^'\"]+)['\"]", code, re.IGNORECASE):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    return routes


def extract_routes_php(code: str) -> list[dict]:
    routes = []
    # Slim/Laravel style
    for m in re.finditer(r"\$app->(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", code, re.IGNORECASE):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    # Also check for Route:: style
    for m in re.finditer(r"Route::(get|post|put|delete|patch)\(\s*['\"]([^'\"]+)['\"]", code, re.IGNORECASE):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    return routes


def extract_routes_java(code: str) -> list[dict]:
    routes = []
    for m in re.finditer(r"@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\(\s*(?:value\s*=\s*)?[\"']([^\"']+)[\"']", code):
        mapping = m.group(1)
        path = m.group(2)
        method_map = {
            "GetMapping": "GET", "PostMapping": "POST", "PutMapping": "PUT",
            "DeleteMapping": "DELETE", "PatchMapping": "PATCH", "RequestMapping": "GET"
        }
        routes.append({"method": method_map.get(mapping, "GET"), "path": path})
    return routes


def extract_routes_csharp(code: str) -> list[dict]:
    routes = []
    for m in re.finditer(r'app\.Map(Get|Post|Put|Delete|Patch)\(\s*"([^"]+)"', code):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    # Also check [HttpGet], [HttpPost] attributes with route
    for m in re.finditer(r'\[Http(Get|Post|Put|Delete|Patch)\(\s*"([^"]+)"\s*\)\]', code):
        routes.append({"method": m.group(1).upper(), "path": m.group(2)})
    return routes


ROUTE_EXTRACTORS = {
    "python": extract_routes_python,
    "nodejs": extract_routes_nodejs,
    "go": extract_routes_go,
    "ruby": extract_routes_ruby,
    "php": extract_routes_php,
    "java": extract_routes_java,
    "csharp": extract_routes_csharp,
}


def read_source(folder: Path, lang: str) -> str:
    """Read the main source code file."""
    info = LANG_MAP[lang]
    code_file = info["code"]
    if "*" in code_file:
        files = list(folder.glob(code_file))
        if files:
            # Read all matching files
            return "\n".join(f.read_text() for f in files)
        return ""
    path = folder / code_file
    if path.exists():
        return path.read_text()
    return ""


def describe_route(route: dict) -> str:
    """Generate a human-readable description for a route."""
    path = route["path"]
    method = route["method"]

    if "webhook" in path.lower():
        return "Inbound webhook endpoint called by Telnyx when an event occurs."
    if "health" in path.lower():
        return "Health check endpoint."
    if method == "GET":
        return f"Retrieve data from `{path}`."
    if method == "POST":
        return f"Submit data to `{path}`."
    if method == "PUT" or method == "PATCH":
        return f"Update data at `{path}`."
    if method == "DELETE":
        return f"Delete resource at `{path}`."
    return f"Handle {method} request to `{path}`."


def generate_api_md(folder: Path, lang: str, readme_sections: dict) -> str:
    """Generate API.md content from source code analysis."""
    title = readme_sections.get("title", human_title(folder.name))
    # Strip language suffix from title for API ref
    api_title = re.sub(r"\s+with\s+.*$", "", title, flags=re.IGNORECASE)

    source = read_source(folder, lang)
    extractor = ROUTE_EXTRACTORS.get(lang)
    routes = extractor(source) if extractor else []

    # Filter out health check
    app_routes = [r for r in routes if r["path"] != "/health"]

    lines = [
        f"# API Reference — {api_title}",
        "",
        "All endpoints accept and return JSON. Base URL in local development: `http://localhost:5000`.",
        "",
        "---",
    ]

    if app_routes:
        for route in app_routes:
            lines.extend([
                "",
                f"## `{route['method']} {route['path']}`",
                "",
                describe_route(route),
                "",
                "### Request",
                "",
                "```json",
                "{",
                '  "example": "see source code for full schema"',
                "}",
                "```",
                "",
                "### Response `200`",
                "",
                "```json",
                "{",
                '  "status": "ok"',
                "}",
                "```",
                "",
                "### Try it",
                "",
                "```bash",
            ])
            if route["method"] == "GET":
                lines.append(f"curl http://localhost:5000{route['path']}")
            else:
                lines.extend([
                    f"curl -X {route['method']} http://localhost:5000{route['path']} \\",
                    '  -H "Content-Type: application/json" \\',
                    "  -d '{}'",
                ])
            lines.extend([
                "```",
                "",
                "---",
            ])
    else:
        lines.extend([
            "",
            "## Endpoints",
            "",
            "See the source code and README for endpoint details.",
            "",
            "---",
        ])

    lines.extend([
        "",
        "## Error Handling",
        "",
        "All endpoints return JSON. On error:",
        "",
        '```json',
        '{"error": "Description of what went wrong"}',
        '```',
        "",
        "| Status | Meaning |",
        "|--------|---------|",
        "| `200` | Success |",
        "| `400` | Bad request — missing or invalid fields |",
        "| `401` | Invalid API key or webhook signature |",
        "| `429` | Rate limit exceeded |",
        "| `500` | Server error |",
        "| `503` | Upstream network error talking to Telnyx |",
    ])

    return "\n".join(lines) + "\n"


def detect_product(folder_name: str) -> str:
    """Detect the Telnyx product category from the folder name."""
    name = folder_name.lower()
    if any(w in name for w in ["sms", "mms", "messaging", "text"]):
        return "messaging"
    if any(w in name for w in ["call", "voice", "ivr", "conference", "whisper", "transfer", "speech", "voicemail", "hold-music", "warm-transfer"]):
        return "voice"
    if any(w in name for w in ["sip"]):
        return "sip"
    if any(w in name for w in ["iot", "mqtt", "sim", "wireless", "esim"]):
        return "iot"
    if any(w in name for w in ["ai", "assistant"]):
        return "ai"
    if any(w in name for w in ["number", "lookup", "cnam"]):
        return "numbers"
    if any(w in name for w in ["webrtc"]):
        return "webrtc"
    if any(w in name for w in ["whatsapp"]):
        return "messaging"
    return "voice"


PRODUCT_DOCS = {
    "messaging": ("Messaging", "https://developers.telnyx.com/docs/messaging"),
    "voice": ("Voice API", "https://developers.telnyx.com/docs/voice"),
    "sip": ("SIP Trunking", "https://developers.telnyx.com/docs/sip-trunking"),
    "iot": ("IoT SIM Management", "https://developers.telnyx.com/docs/iot"),
    "ai": ("AI Assistants", "https://developers.telnyx.com/docs/ai"),
    "numbers": ("Phone Numbers", "https://developers.telnyx.com/docs/numbers"),
    "webrtc": ("WebRTC", "https://developers.telnyx.com/docs/webrtc"),
}


def generate_guide_md(folder: Path, lang: str, readme_sections: dict) -> str:
    """Generate GUIDE.md content from README sections."""
    title = readme_sections.get("title", human_title(folder.name))
    description = readme_sections.get("description", f"Build a {human_title(folder.name).lower()} example.")
    # Truncate description to first sentence
    first_sentence = description.split(". ")[0] + "."

    info = LANG_MAP[lang]
    product = detect_product(folder.name)
    product_name, product_docs = PRODUCT_DOCS.get(product, ("Voice API", "https://developers.telnyx.com/docs/voice"))

    env_vars = extract_env_vars(folder / ".env.example")

    source = read_source(folder, lang)
    extractor = ROUTE_EXTRACTORS.get(lang)
    routes = extractor(source) if extractor else []
    app_routes = [r for r in routes if r["path"] != "/health"]

    lines = [
        f"# {title}",
        "",
        first_sentence,
        "",
        "## How It Works",
        "",
        "```",
        "  Client request",
        "        │",
        "        ▼",
        f"  ┌────────────────────┐",
        f"  │  {info['lang_label']} Server{' ' * max(0, 12 - len(info['lang_label']))}│  receives request",
        f"  └─────────┬──────────┘",
        "        │  Telnyx API call",
        "        ▼",
        f"  ┌────────────────────┐",
        f"  │  Telnyx {product_name}{' ' * max(0, 10 - len(product_name))}│  processes and responds",
        f"  └────────────────────┘",
        "```",
        "",
        "## Telnyx Products Used",
        "",
        f"- **{product_name}** — [Documentation]({product_docs})",
        "",
        "## Prerequisites",
        "",
    ]

    prereqs = readme_sections.get("prerequisites", "")
    if prereqs:
        lines.append(prereqs)
    else:
        lines.extend([
            f"- {info['lang_label']} installed",
            "- A [Telnyx account](https://portal.telnyx.com/sign-up) with funded balance",
            "- An [API key](https://portal.telnyx.com/api-keys)",
            "- [ngrok](https://ngrok.com) for webhook testing",
        ])

    lines.extend([
        "",
        "## Step 1: Set Up the Project",
        "",
        "```bash",
        "git clone https://github.com/team-telnyx/telnyx-code-examples.git",
        f"cd telnyx-code-examples/{folder.name}",
        "cp .env.example .env",
        f"{info['install']}",
        "```",
        "",
        "Edit `.env` with your Telnyx credentials:",
        "",
    ])

    if env_vars:
        lines.append("| Variable | Description |")
        lines.append("|----------|-------------|")
        for key, val in env_vars:
            lines.append(f"| `{key}` | {val} |")
        lines.append("")

    lines.extend([
        "## Step 2: Understand the Code",
        "",
        f"The main application logic lives in `{info['code']}`.",
        "",
    ])

    if app_routes:
        lines.append("### All Endpoints")
        lines.append("")
        lines.append("| Method | Path | Purpose |")
        lines.append("|--------|------|---------|")
        for r in app_routes:
            purpose = "Webhook handler" if "webhook" in r["path"].lower() else "API endpoint"
            lines.append(f"| `{r['method']}` | `{r['path']}` | {purpose} |")
        lines.append("")

    lines.extend([
        "## Step 3: Run It",
        "",
        "```bash",
        f"{info['run']}",
        "```",
        "",
        "The server starts on `http://localhost:5000`.",
        "",
        "For webhook-based features, expose your local server:",
        "",
        "```bash",
        "ngrok http 5000",
        "```",
        "",
        "## Step 4: Test It",
        "",
    ])

    if app_routes:
        # Find a good test endpoint (prefer non-webhook POST or any GET)
        test_route = None
        for r in app_routes:
            if r["method"] == "GET" and "webhook" not in r["path"].lower():
                test_route = r
                break
        if not test_route:
            for r in app_routes:
                if r["method"] == "POST" and "webhook" not in r["path"].lower():
                    test_route = r
                    break
        if not test_route:
            test_route = app_routes[0]

        lines.append("```bash")
        if test_route["method"] == "GET":
            lines.append(f"curl http://localhost:5000{test_route['path']}")
        else:
            lines.extend([
                f"curl -X {test_route['method']} http://localhost:5000{test_route['path']} \\",
                '  -H "Content-Type: application/json" \\',
                '  -d \'{"to": "+15551234567"}\'',
            ])
        lines.append("```")
    else:
        lines.append("See the README for testing instructions.")

    lines.extend([
        "",
        "## Going to Production",
        "",
        "- **Environment variables** — never commit API keys; use a secrets manager.",
        "- **Authentication** — protect your endpoints with API key validation.",
        "- **Monitoring** — add structured logging and alerting.",
        "- **Rate limiting** — protect endpoints from abuse.",
        "- **Database** — replace any in-memory storage with a persistent store.",
        "",
        "## Resources",
        "",
        f"- [Source code](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/{folder.name}/README.md)",
        f"- [API reference](https://raw.githubusercontent.com/team-telnyx/telnyx-code-examples/main/{folder.name}/API.md)",
        f"- [{product_name} Documentation]({product_docs})",
        "- [Telnyx Portal](https://portal.telnyx.com)",
    ])

    return "\n".join(lines) + "\n"


def fix_readme_make_docker_refs(readme_path: Path):
    """Remove Make/Docker references from README Quick Start."""
    if not readme_path.exists():
        return
    text = readme_path.read_text()
    original = text

    # Remove Option 2: Docker section
    text = re.sub(
        r"### Option 2: Docker\s*\n\n```bash\n(?:.*\n)*?```\n\n",
        "",
        text,
    )

    # Remove "make setup" / "make run" from Option 1 and replace with actual commands
    # This is tricky - just remove make references from quick start
    text = re.sub(r"^make docker-build\n", "", text, flags=re.MULTILINE)
    text = re.sub(r"^make docker-run\n", "", text, flags=re.MULTILINE)

    # Remove FAQ answer referencing Dockerfile
    text = text.replace(
        "Yes. This example includes error handling, environment-based configuration, and a Dockerfile for containerized deployment. Review the security and scaling sections before deploying to production.",
        "Yes. This example includes error handling and environment-based configuration. Review the security and scaling sections before deploying to production."
    )

    if text != original:
        readme_path.write_text(text)


def main() -> int:
    # Get list of changed example dirs from diff against main
    sys.path.insert(0, str(ROOT / "scripts" / "review"))
    from _changed import changed_example_dirs

    changed = set(changed_example_dirs(ROOT, "origin/main"))
    if not changed:
        print("No changed example folders found.")
        return 0

    print(f"Processing {len(changed)} example folders...")

    created_api = 0
    created_guide = 0
    deleted_forbidden = 0
    fixed_readmes = 0

    for folder_name in sorted(changed):
        folder = ROOT / folder_name
        if not folder.is_dir():
            continue
        lang = detect_lang(folder_name)
        if not lang:
            continue

        # 1. Remove forbidden files
        for forbidden in FORBIDDEN:
            fpath = folder / forbidden
            if fpath.exists():
                fpath.unlink()
                deleted_forbidden += 1
                print(f"  Deleted: {folder_name}/{forbidden}")

        # 2. Generate API.md if missing
        api_path = folder / "API.md"
        if not api_path.exists():
            readme_sections = extract_readme_sections(folder / "README.md")
            content = generate_api_md(folder, lang, readme_sections)
            api_path.write_text(content)
            created_api += 1
            print(f"  Created: {folder_name}/API.md")

        # 3. Generate GUIDE.md if missing
        guide_path = folder / "GUIDE.md"
        if not guide_path.exists():
            readme_sections = extract_readme_sections(folder / "README.md")
            content = generate_guide_md(folder, lang, readme_sections)
            guide_path.write_text(content)
            created_guide += 1
            print(f"  Created: {folder_name}/GUIDE.md")

        # 4. Fix README.md references to Docker/Make
        readme_path = folder / "README.md"
        if readme_path.exists():
            old = readme_path.read_text()
            fix_readme_make_docker_refs(readme_path)
            if readme_path.read_text() != old:
                fixed_readmes += 1

    print(f"\nSummary:")
    print(f"  API.md created:     {created_api}")
    print(f"  GUIDE.md created:   {created_guide}")
    print(f"  Forbidden deleted:  {deleted_forbidden}")
    print(f"  READMEs updated:    {fixed_readmes}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
