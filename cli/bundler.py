"""
RepoArchitect AI — CLI Bundler
Bundles local project files into a single analyzable context.
Usage: python cli/bundler.py --path /your/project --output outputs/bundle.txt
"""

import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# File extensions to include
INCLUDE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.vue',
    '.html', '.css', '.scss', '.json', '.yaml', '.yml', '.toml',
    '.env.example', '.md', '.txt', '.sh', '.dockerfile'
}

# Folders to skip
SKIP_FOLDERS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.cache', 'coverage', '.pytest_cache',
    'eggs', '.eggs', 'wheels', 'htmlcov', '.tox', '.mypy_cache'
}

# Files to skip
SKIP_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitignore', 'package-lock.json',
    'yarn.lock', 'poetry.lock', 'Pipfile.lock'
}

MAX_FILE_SIZE_KB = 500  # Skip files larger than this


def should_include(path: Path) -> bool:
    """Check if file should be included in bundle."""
    if path.name in SKIP_FILES:
        return False
    if path.suffix.lower() not in INCLUDE_EXTENSIONS:
        return False
    if path.stat().st_size > MAX_FILE_SIZE_KB * 1024:
        return False
    return True


def bundle_project(project_path: str, output_path: str = None) -> dict:
    """
    Bundle all relevant project files into a single context dict.
    Returns bundle dict with metadata and file contents.
    """
    root = Path(project_path).resolve()
    if not root.exists():
        raise ValueError(f"Path does not exist: {project_path}")

    print(f"\n🔍 RepoArchitect AI — Scanning: {root}")
    print("=" * 55)

    files_data   = {}
    skipped      = []
    total_lines  = 0
    file_count   = 0

    for file_path in sorted(root.rglob("*")):
        # Skip hidden folders and blacklisted folders
        parts = file_path.parts
        if any(part.startswith('.') or part in SKIP_FOLDERS for part in parts):
            continue
        if not file_path.is_file():
            continue
        if not should_include(file_path):
            skipped.append(str(file_path.relative_to(root)))
            continue

        try:
            content    = file_path.read_text(encoding='utf-8', errors='ignore')
            rel_path   = str(file_path.relative_to(root))
            lines      = content.count('\n') + 1
            total_lines += lines
            file_count  += 1
            files_data[rel_path] = {
                'content'   : content,
                'lines'     : lines,
                'size_kb'   : round(file_path.stat().st_size / 1024, 2),
                'extension' : file_path.suffix.lower()
            }
            print(f"  ✓ {rel_path} ({lines} lines)")
        except Exception as e:
            skipped.append(f"{file_path.relative_to(root)} (error: {e})")

    # Build extension summary
    ext_summary = {}
    for f in files_data.values():
        ext = f['extension'] or 'no-ext'
        ext_summary[ext] = ext_summary.get(ext, 0) + 1

    bundle = {
        'metadata': {
            'project_path' : str(root),
            'project_name' : root.name,
            'scanned_at'   : datetime.now().isoformat(),
            'total_files'  : file_count,
            'total_lines'  : total_lines,
            'skipped_files': len(skipped),
            'extensions'   : ext_summary
        },
        'files': files_data
    }

    print(f"\n{'='*55}")
    print(f"✅ Bundled  : {file_count} files | {total_lines:,} lines")
    print(f"⏭️  Skipped  : {len(skipped)} files")
    print(f"📦 Languages: {dict(sorted(ext_summary.items(), key=lambda x: -x[1]))}")

    # Save bundle if output path given
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bundle, f, indent=2)
        print(f"💾 Bundle saved: {output_path}")

    return bundle


def bundle_to_text(bundle: dict, max_chars_per_file: int = 3000) -> str:
    """Convert bundle dict to a single text string for LLM context."""
    meta  = bundle['metadata']
    lines = [
        f"PROJECT: {meta['project_name']}",
        f"Total Files: {meta['total_files']} | Total Lines: {meta['total_lines']:,}",
        f"Languages: {meta['extensions']}",
        "=" * 60,
        ""
    ]
    for rel_path, fdata in bundle['files'].items():
        lines.append(f"\n### FILE: {rel_path} ({fdata['lines']} lines) ###")
        content = fdata['content']
        if len(content) > max_chars_per_file:
            content = content[:max_chars_per_file] + f"\n... [truncated, {fdata['lines']} total lines]"
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RepoArchitect AI — Project Bundler")
    parser.add_argument("--path",   required=True, help="Path to project folder")
    parser.add_argument("--output", default="outputs/bundle.json", help="Output bundle path")
    args = parser.parse_args()

    bundle = bundle_project(args.path, args.output)
    print(f"\n🚀 Ready for analysis! Run: streamlit run app/app.py")
