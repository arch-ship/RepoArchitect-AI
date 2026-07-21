"""
RepoArchitect AI — Streamlit Dashboard
Interactive AI Senior Software Architect
"""

import streamlit as st
import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(str(Path(__file__).parent.parent))

from cli.bundler import bundle_project, bundle_to_text
from core.analyzer import get_groq_client, run_full_analysis, ask_architect
from core.mapper import map_dependencies, get_project_stats, generate_structure_tree

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="RepoArchitect AI",
    page_icon="https://cdn-icons-png.flaticon.com/512/1197/1197460.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State ──────────────────────────────────────────────
defaults = {
    'bundle'       : None,
    'codebase_text': None,
    'analysis'     : None,
    'stats'        : None,
    'deps'         : None,
    'conversation' : [],
    'groq_key'     : os.getenv("GROQ_API_KEY", ""),
    'dark_mode'    : True,
    'analyzed'     : False,
    'chat_input'   : "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ────────────────────────────────────────────────────────
def get_css(dark):
    bg      = "#0d1117" if dark else "#f6f8fa"
    sidebar = "#161b22" if dark else "#ffffff"
    card    = "#161b22" if dark else "#ffffff"
    card2   = "#21262d" if dark else "#f0f4f8"
    text    = "#e6edf3" if dark else "#24292f"
    muted   = "#8b949e" if dark else "#656d76"
    border  = "#30363d" if dark else "#d0d7de"
    accent  = "#58a6ff"
    green   = "#3fb950"
    red     = "#f85149"
    purple  = "#bc8cff"
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}
.stApp {{
    background-color: {bg};
    color: {text};
}}
section[data-testid="stSidebar"] {{
    background-color: {sidebar} !important;
    border-right: 1px solid {border};
}}
.main-title {{
    font-size: 1.9rem;
    font-weight: 700;
    color: {accent};
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}}
.subtitle {{
    font-size: 0.85rem;
    color: {muted};
    margin-bottom: 24px;
    font-weight: 400;
}}
.stat-card {{
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
}}
.stat-number {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {accent};
    font-family: 'JetBrains Mono', monospace;
}}
.stat-label {{
    font-size: 0.75rem;
    color: {muted};
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-top: 4px;
}}
.feature-card {{
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 20px;
    height: 100%;
    transition: border-color 0.2s;
}}
.feature-card:hover {{ border-color: {accent}; }}
.feature-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: {text};
    margin-bottom: 8px;
}}
.feature-desc {{
    font-size: 0.82rem;
    color: {muted};
    line-height: 1.5;
}}
.chat-user {{
    background: {card2};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 3px solid {accent};
}}
.chat-ai {{
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 3px solid {green};
}}
.chat-label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
    color: {muted};
}}
.input-method {{
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s;
}}
.tag {{
    display: inline-block;
    background: {card2};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    color: {accent};
    margin: 2px;
}}
.analysis-section {{
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
}}
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: {card2};
    border-radius: 8px;
    padding: 4px;
    border: 1px solid {border};
}}
.stTabs [data-baseweb="tab"] {{
    font-weight: 500;
    font-size: 0.85rem;
    border-radius: 6px;
    padding: 6px 14px;
    color: {muted};
}}
.stTabs [aria-selected="true"] {{
    background: {card} !important;
    color: {text} !important;
    font-weight: 600;
}}
.stButton button {{
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}}
div[data-testid="metric-container"] {{
    background: {card};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 12px 16px;
}}
.status-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1f3a1f;
    border: 1px solid {green};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.8rem;
    color: {green};
    font-weight: 500;
}}
hr {{ border-color: {border} !important; opacity: 0.5; }}
</style>"""

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ── Helper: load bundle ────────────────────────────────────────
def load_bundle(bundle_data):
    if 'files' not in bundle_data or len(bundle_data['files']) == 0:
        return False, "No code files found!"
    st.session_state.bundle        = bundle_data
    st.session_state.codebase_text = bundle_to_text(bundle_data)
    st.session_state.stats         = get_project_stats(bundle_data)
    st.session_state.deps          = map_dependencies(bundle_data['files'])
    st.session_state.analyzed      = True
    st.session_state.analysis      = None
    st.session_state.conversation  = []
    return True, bundle_data['metadata']['total_files']

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### RepoArchitect AI")
    st.markdown("<span style='color:#8b949e;font-size:0.8rem'>AI-Powered Codebase Analysis</span>", unsafe_allow_html=True)
    st.divider()

    # Groq Key — auto-load from .env
    st.markdown("<span style='font-size:0.8rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.8px'>GROQ API KEY</span>", unsafe_allow_html=True)
    groq_input = st.text_input(
        "Groq Key", type="password",
        value=st.session_state.groq_key,
        placeholder="gsk_... (or set in .env file)",
        label_visibility="collapsed"
    )
    if groq_input != st.session_state.groq_key:
        st.session_state.groq_key = groq_input

    if st.session_state.groq_key:
        st.markdown('<div class="status-badge">&#9679; Groq Connected</div>', unsafe_allow_html=True)
    else:
        st.caption("Get free key: [console.groq.com](https://console.groq.com)")
        st.caption("Or add `GROQ_API_KEY=gsk_...` to `.env` file")

    st.divider()
    st.markdown("<span style='font-size:0.8rem;font-weight:600;color:#8b949e;text-transform:uppercase;letter-spacing:0.8px'>ANALYZE PROJECT</span>", unsafe_allow_html=True)

    input_method = st.radio("Method", ["Local Path", "ZIP Upload", "GitHub URL", "Bundle JSON"],
                             label_visibility="collapsed")

    if input_method == "Local Path":
        project_path = st.text_input("Path", placeholder="/path/to/project",
                                      label_visibility="collapsed")
        if st.button("Scan & Analyze", use_container_width=True, type="primary",
                     disabled=not (project_path and st.session_state.groq_key)):
            with st.spinner("Scanning..."):
                try:
                    ok, n = load_bundle(bundle_project(project_path))
                    if ok: st.success(f"{n} files bundled!")
                    else: st.error(n)
                except Exception as e:
                    st.error(str(e))

    elif input_method == "ZIP Upload":
        zip_file = st.file_uploader("Upload ZIP", type=['zip'], label_visibility="collapsed")
        if zip_file and st.button("Extract & Bundle", use_container_width=True, type="primary"):
            with st.spinner("Extracting..."):
                try:
                    import zipfile, tempfile, shutil
                    tmp = tempfile.mkdtemp()
                    with zipfile.ZipFile(zip_file, 'r') as z:
                        z.extractall(tmp)
                    ok, n = load_bundle(bundle_project(tmp))
                    shutil.rmtree(tmp)
                    if ok: st.success(f"{n} files ready!")
                    else: st.error(n)
                except Exception as e:
                    st.error(str(e))

    elif input_method == "GitHub URL":
        github_url = st.text_input("GitHub URL", placeholder="https://github.com/user/repo",
                                    label_visibility="collapsed")
        if st.button("Clone & Analyze", use_container_width=True, type="primary",
                     disabled=not (github_url and "github.com" in github_url)):
            with st.spinner("Cloning repository..."):
                try:
                    import subprocess, tempfile, shutil
                    tmp = tempfile.mkdtemp()
                    r   = subprocess.run(["git", "clone", "--depth=1", github_url, tmp],
                                         capture_output=True, text=True, timeout=60)
                    if r.returncode != 0:
                        st.error(f"Clone failed: {r.stderr[:200]}")
                    else:
                        ok, n = load_bundle(bundle_project(tmp))
                        shutil.rmtree(tmp)
                        if ok: st.success(f"{n} files cloned!")
                        else: st.error(n)
                except subprocess.TimeoutExpired:
                    st.error("Timed out — repo too large")
                except Exception as e:
                    st.error(str(e))

    elif input_method == "Bundle JSON":
        uploaded = st.file_uploader("Upload bundle.json", type=['json'],
                                     label_visibility="collapsed", key="bundle_up")
        if uploaded and not st.session_state.bundle:
            try:
                ok, n = load_bundle(json.loads(uploaded.read().decode('utf-8')))
                if ok: st.success(f"{n} files loaded!")
                else: st.error(n)
            except Exception as e:
                st.error(str(e))

    if st.session_state.bundle:
        st.divider()
        meta = st.session_state.bundle['metadata']
        st.markdown(f"**{meta['project_name']}**")
        st.caption(f"{meta['total_files']} files · {meta['total_lines']:,} lines")
        if st.button("Clear & Reset", use_container_width=True):
            for k in ['bundle','codebase_text','stats','deps','analysis','analyzed']:
                st.session_state[k] = None
            st.session_state.conversation = []
            st.session_state.analyzed     = False
            st.rerun()

    st.divider()
    if st.button("Light Mode" if st.session_state.dark_mode else "Dark Mode",
                  use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ── HEADER ─────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([6, 2])
with col_h1:
    st.markdown('<div class="main-title">RepoArchitect AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Autonomous Codebase Analysis · Architecture Mapping · Security Audit · AI Senior Architect</div>', unsafe_allow_html=True)

# ── LANDING ────────────────────────────────────────────────────
if not st.session_state.bundle:
    features = [
        ("Architecture Analysis", "Maps components, data flow, and structural patterns across your entire codebase."),
        ("Security Audit",        "Detects hardcoded secrets, injection risks, auth flaws, and anti-patterns."),
        ("Code Quality Report",   "Identifies code smells, duplication, missing patterns, and maintainability issues."),
        ("Improvement Roadmap",   "Generates a prioritized 4-phase roadmap tailored to your codebase."),
        ("AI Architect Chat",     "Ask anything — the AI references your actual files and answers with context."),
        ("Dependency Map",        "Visualizes all external packages and per-file import relationships."),
    ]
    cols = st.columns(3)
    for i, (title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")

    st.divider()
    st.markdown("**Quick Start**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Local Path**\n\nEnter your project folder path in the sidebar.")
    with c2:
        st.markdown("**ZIP Upload**\n\nZip your project and upload directly.")
    with c3:
        st.markdown("**GitHub URL**\n\nPaste any public repo URL — auto-clones.")

    st.code("# Or use CLI to bundle first:\npython cli/bundler.py --path /your/project --output outputs/bundle.json", language="bash")

else:
    # ── RUN ANALYSIS BUTTON ─────────────────────────────────────
    if not st.session_state.analysis and st.session_state.groq_key:
        if st.button("Run Full AI Analysis  →", type="primary", use_container_width=False):
            with st.status("Running AI analysis...", expanded=True) as status:
                try:
                    client   = get_groq_client(st.session_state.groq_key)
                    progress = st.progress(0)
                    def update_progress(msg, val):
                        st.write(msg); progress.progress(val)
                    results = run_full_analysis(client, st.session_state.codebase_text,
                                                progress_callback=update_progress)
                    st.session_state.analysis = results
                    status.update(label="Analysis complete!", state="complete")
                    st.rerun()
                except Exception as e:
                    status.update(label=f"Error: {e}", state="error")
    elif not st.session_state.groq_key:
        st.warning("Add Groq API key in sidebar to run AI analysis.")
    elif st.session_state.analysis:
        st.markdown('<div class="status-badge">&#9679; Analysis Complete</div><br>', unsafe_allow_html=True)

    # ── TABS ───────────────────────────────────────────────────
    stats    = st.session_state.stats
    deps     = st.session_state.deps
    analysis = st.session_state.analysis or {}

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Overview", "Architecture", "Security",
        "Code Quality", "Roadmap", "AI Chat", "Dependencies"
    ])

    # TAB 1 ── Overview
    with tab1:
        if stats:
            c1, c2, c3, c4 = st.columns(4)
            for col, label, val in [
                (c1, "FILES",      stats['total_files']),
                (c2, "LINES",      f"{stats['total_lines']:,}"),
                (c3, "TYPE",       stats['project_type'].split('(')[0].strip()),
                (c4, "FRAMEWORKS", len(stats.get('frameworks', [])))
            ]:
                with col:
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

            st.markdown("")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("**File Structure**")
                st.code(generate_structure_tree(st.session_state.bundle['files']), language=None)
            with col2:
                st.markdown("**Tech Stack**")
                if stats.get('frameworks'):
                    for fw in stats['frameworks']:
                        st.markdown(f'<span class="tag">{fw}</span>', unsafe_allow_html=True)
                    st.markdown("")
                else:
                    st.caption("No major frameworks detected")

                st.markdown("**Language Breakdown**")
                lang_data = {k: v for k,v in stats.get('type_readable',{}).items()
                             if k not in ['Markdown','JSON','YAML']}
                if lang_data:
                    dark = st.session_state.dark_mode
                    bg   = '#0d1117' if dark else '#f6f8fa'
                    tc   = '#e6edf3' if dark else '#24292f'
                    fig, ax = plt.subplots(figsize=(5, 3.5))
                    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
                    colors = ['#58a6ff','#3fb950','#bc8cff','#f85149','#d29922','#39d353']
                    wedges, _, autotexts = ax.pie(
                        list(lang_data.values()), labels=list(lang_data.keys()),
                        autopct='%1.0f%%', colors=colors[:len(lang_data)],
                        textprops={'color': tc, 'fontsize': 9}
                    )
                    for at in autotexts: at.set_color(tc)
                    ax.set_title('', color=tc)
                    plt.tight_layout()
                    st.pyplot(fig)

            st.markdown("**Largest Files**")
            for path, lines in stats.get('largest_files', [])[:8]:
                c1, c2 = st.columns([5, 1])
                c1.markdown(f'<span class="tag">{path}</span>', unsafe_allow_html=True)
                c2.caption(f"{lines:,} lines")

    # TAB 2 ── Architecture
    with tab2:
        if analysis.get('architecture'):
            st.markdown(analysis['architecture'])
        elif st.session_state.groq_key:
            if st.button("Analyze Architecture", type="primary"):
                with st.spinner("Analyzing..."):
                    from core.analyzer import analyze_architecture
                    r = analyze_architecture(get_groq_client(st.session_state.groq_key),
                                             st.session_state.codebase_text)
                    if not st.session_state.analysis: st.session_state.analysis = {}
                    st.session_state.analysis['architecture'] = r
                    st.rerun()
        else:
            st.info("Add Groq key to analyze.")

    # TAB 3 ── Security
    with tab3:
        if analysis.get('security'):
            st.markdown(analysis['security'])
        elif st.session_state.groq_key:
            if st.button("Run Security Audit", type="primary"):
                with st.spinner("Scanning..."):
                    from core.analyzer import analyze_security
                    r = analyze_security(get_groq_client(st.session_state.groq_key),
                                         st.session_state.codebase_text)
                    if not st.session_state.analysis: st.session_state.analysis = {}
                    st.session_state.analysis['security'] = r
                    st.rerun()
        else:
            st.info("Add Groq key to analyze.")

    # TAB 4 ── Code Quality
    with tab4:
        if analysis.get('quality'):
            st.markdown(analysis['quality'])
        elif st.session_state.groq_key:
            if st.button("Check Code Quality", type="primary"):
                with st.spinner("Checking..."):
                    from core.analyzer import analyze_code_quality
                    r = analyze_code_quality(get_groq_client(st.session_state.groq_key),
                                             st.session_state.codebase_text)
                    if not st.session_state.analysis: st.session_state.analysis = {}
                    st.session_state.analysis['quality'] = r
                    st.rerun()
        else:
            st.info("Add Groq key to analyze.")

    # TAB 5 ── Roadmap
    with tab5:
        if analysis.get('roadmap'):
            st.markdown(analysis['roadmap'])
            st.divider()
            st.download_button(
                "Download Roadmap (Markdown)",
                data=f"# RepoArchitect AI — Roadmap\n\n{datetime.now().strftime('%d %B %Y')}\n\n{analysis['roadmap']}",
                file_name="roadmap.md", mime="text/markdown"
            )
        elif st.session_state.groq_key:
            if st.button("Generate Roadmap", type="primary"):
                with st.spinner("Generating..."):
                    from core.analyzer import generate_roadmap
                    r = generate_roadmap(
                        get_groq_client(st.session_state.groq_key),
                        st.session_state.codebase_text,
                        analysis.get('architecture',''),
                        analysis.get('security',''),
                        analysis.get('quality','')
                    )
                    if not st.session_state.analysis: st.session_state.analysis = {}
                    st.session_state.analysis['roadmap'] = r
                    st.rerun()
        else:
            st.info("Add Groq key to generate roadmap.")

    # TAB 6 ── AI Chat
    with tab6:
        st.markdown("**AI Senior Architect** — Ask anything about your codebase. References actual files.")
        st.caption("For vague questions or TODO items, the AI will ask clarifying questions first.")
        st.divider()

        if not st.session_state.groq_key:
            st.warning("Add Groq API key in sidebar to use chat.")
        elif not st.session_state.bundle:
            st.info("Load a project first.")
        else:
            # Chat history
            chat_container = st.container()
            with chat_container:
                if not st.session_state.conversation:
                    st.markdown("**Example questions:**")
                    examples = [
                        "What is the overall architecture of this project?",
                        "Are there any security vulnerabilities I should fix?",
                        "How can I improve performance?",
                        "What design patterns are missing?",
                        "Explain the data flow through this system",
                        "How would you refactor the main module?",
                    ]
                    c1, c2 = st.columns(2)
                    for i, ex in enumerate(examples):
                        with (c1 if i % 2 == 0 else c2):
                            if st.button(ex, key=f"ex_{i}", use_container_width=True):
                                with st.spinner("Thinking..."):
                                    client   = get_groq_client(st.session_state.groq_key)
                                    response = ask_architect(client, st.session_state.codebase_text,
                                                             ex, st.session_state.conversation)
                                    st.session_state.conversation.append({"role":"user","content":ex})
                                    st.session_state.conversation.append({"role":"assistant","content":response})
                                    st.rerun()
                else:
                    for msg in st.session_state.conversation:
                        if msg['role'] == 'user':
                            st.markdown(f'''<div class="chat-user">
                                <div class="chat-label">You</div>
                                {msg["content"]}
                            </div>''', unsafe_allow_html=True)
                        else:
                            st.markdown(f'''<div class="chat-ai">
                                <div class="chat-label">AI Architect</div>
                                {msg["content"]}
                            </div>''', unsafe_allow_html=True)

            st.divider()
            user_input = st.chat_input("Ask the AI Architect about your codebase...")
            if user_input:
                with st.spinner("Thinking..."):
                    client   = get_groq_client(st.session_state.groq_key)
                    response = ask_architect(client, st.session_state.codebase_text,
                                             user_input, st.session_state.conversation)
                    st.session_state.conversation.append({"role":"user","content":user_input})
                    st.session_state.conversation.append({"role":"assistant","content":response})
                    st.rerun()

            if st.session_state.conversation:
                if st.button("Clear Chat"):
                    st.session_state.conversation = []
                    st.rerun()

    # TAB 7 ── Dependencies
    with tab7:
        if deps:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"**External Packages** — {deps['total_external']} total")
                if deps['external_packages']:
                    dark = st.session_state.dark_mode
                    bg   = '#0d1117' if dark else '#f6f8fa'
                    tc   = '#e6edf3' if dark else '#24292f'
                    top  = dict(list(deps['external_packages'].items())[:15])
                    fig, ax = plt.subplots(figsize=(7, 5))
                    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
                    bars = ax.barh(list(top.keys()), list(top.values()),
                                   color='#58a6ff', alpha=0.85)
                    ax.set_xlabel('Import Count', color=tc)
                    ax.tick_params(colors=tc, labelsize=9)
                    for spine in ax.spines.values(): spine.set_color('#30363d')
                    for bar, count in zip(bars, top.values()):
                        ax.text(bar.get_width()+0.05, bar.get_y()+bar.get_height()/2,
                                str(count), va='center', color=tc, fontsize=8)
                    plt.tight_layout()
                    st.pyplot(fig)

            with c2:
                st.markdown("**Per-File Dependencies**")
                for fp, imports in list(deps.get('file_dependencies',{}).items())[:20]:
                    if imports:
                        with st.expander(fp):
                            for imp in imports:
                                st.markdown(f'<span class="tag">{imp}</span>', unsafe_allow_html=True)
                            st.markdown("")
        else:
            st.info("Load a project to see dependency map.")