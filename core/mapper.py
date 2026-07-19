"""
RepoArchitect AI — Dependency & Structure Mapper
Maps imports, dependencies, and project structure for visualization.
"""

import re
import json
from pathlib import Path
from collections import defaultdict


def extract_python_imports(content: str) -> list:
    """Extract all imports from Python file."""
    imports = []
    patterns = [
        r'^import\s+([\w.]+)',
        r'^from\s+([\w.]+)\s+import',
    ]
    for line in content.split('\n'):
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                imports.append(match.group(1).split('.')[0])
    return list(set(imports))


def extract_js_imports(content: str) -> list:
    """Extract imports from JS/TS files."""
    imports = []
    patterns = [
        r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",
        r"require\(['\"]([^'\"]+)['\"]\)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for m in matches:
            pkg = m.split('/')[0].replace('@', '')
            if not m.startswith('.'):  # Skip relative imports
                imports.append(pkg)
    return list(set(imports))


def map_dependencies(files_data: dict) -> dict:
    """Map all dependencies across the project."""
    all_deps    = defaultdict(set)
    file_deps   = {}
    internal    = set()
    external    = defaultdict(int)

    # Get internal module names
    for rel_path in files_data:
        name = Path(rel_path).stem
        internal.add(name)

    for rel_path, fdata in files_data.items():
        ext     = fdata['extension']
        content = fdata['content']
        imports = []

        if ext == '.py':
            imports = extract_python_imports(content)
        elif ext in {'.js', '.ts', '.jsx', '.tsx', '.vue'}:
            imports = extract_js_imports(content)

        file_deps[rel_path] = imports
        for imp in imports:
            if imp not in internal:
                external[imp] += 1

    return {
        'file_dependencies' : file_deps,
        'external_packages' : dict(sorted(external.items(), key=lambda x: -x[1])),
        'total_external'    : len(external),
    }


def get_project_stats(bundle: dict) -> dict:
    """Generate comprehensive project statistics."""
    files_data = bundle['files']
    meta       = bundle['metadata']

    # Lines per language
    lang_lines = defaultdict(int)
    lang_files = defaultdict(int)
    for fdata in files_data.values():
        ext = fdata['extension'] or 'other'
        lang_lines[ext] += fdata['lines']
        lang_files[ext] += 1

    # Largest files
    largest = sorted(
        [(path, fdata['lines']) for path, fdata in files_data.items()],
        key=lambda x: -x[1]
    )[:10]

    # File type distribution
    type_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.jsx': 'React JSX', '.tsx': 'React TSX', '.vue': 'Vue',
        '.java': 'Java', '.go': 'Go', '.rs': 'Rust', '.cpp': 'C++',
        '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
        '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML',
        '.md': 'Markdown', '.sh': 'Shell'
    }

    # Detect project type
    all_extensions = set(meta['extensions'].keys())
    if '.py' in all_extensions and any(e in all_extensions for e in ['.html', '.js']):
        project_type = "Full-Stack (Python Backend)"
    elif '.py' in all_extensions:
        project_type = "Python Project"
    elif '.ts' in all_extensions or '.tsx' in all_extensions:
        project_type = "TypeScript/React Project"
    elif '.js' in all_extensions or '.jsx' in all_extensions:
        project_type = "JavaScript/Node.js Project"
    elif '.java' in all_extensions:
        project_type = "Java Project"
    elif '.go' in all_extensions:
        project_type = "Go Project"
    else:
        project_type = "Mixed/Other"

    # Check for common frameworks
    all_content = " ".join([f['content'][:500] for f in files_data.values()])
    frameworks  = []
    fw_patterns = {
        'FastAPI'    : r'fastapi|FastAPI',
        'Flask'      : r'from flask|import flask',
        'Django'     : r'django|Django',
        'React'      : r'import React|from react',
        'Next.js'    : r'next/|from next',
        'Express'    : r'express\(\)|require.*express',
        'Streamlit'  : r'import streamlit|st\.title',
        'LangChain'  : r'langchain|LangChain',
        'SQLAlchemy' : r'sqlalchemy|SQLAlchemy',
        'Pydantic'   : r'pydantic|BaseModel',
    }
    for fw, pattern in fw_patterns.items():
        if re.search(pattern, all_content):
            frameworks.append(fw)

    return {
        'project_type'   : project_type,
        'frameworks'     : frameworks,
        'total_files'    : meta['total_files'],
        'total_lines'    : meta['total_lines'],
        'lang_lines'     : dict(lang_lines),
        'lang_files'     : dict(lang_files),
        'largest_files'  : largest,
        'type_readable'  : {type_map.get(k, k): v for k, v in lang_files.items()},
    }


def generate_structure_tree(files_data: dict, max_depth: int = 4) -> str:
    """Generate a readable file tree string."""
    tree   = {}
    for path in sorted(files_data.keys()):
        parts = Path(path).parts
        node  = tree
        for part in parts[:max_depth]:
            node = node.setdefault(part, {})

    def render(node, prefix="", is_last=True):
        lines = []
        items = list(node.items())
        for i, (name, children) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            connector    = "└── " if is_last_item else "├── "
            lines.append(f"{prefix}{connector}{name}")
            if children:
                extension = "    " if is_last_item else "│   "
                lines.extend(render(children, prefix + extension, is_last_item))
        return lines

    return "\n".join(["📁 Project Root"] + render(tree))
