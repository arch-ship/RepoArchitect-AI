"""
RepoArchitect AI — Streamlit Dashboard
Interactive AI Senior Software Architect
"""

import streamlit as st
import json
import os
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from cli.bundler import bundle_project, bundle_to_text
from core.analyzer import get_groq_client, run_full_analysis, ask_architect
from core.mapper import map_dependencies, get_project_stats, generate_structure_tree

# ── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="RepoArchitect AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State ──────────────────────────────────────────────
defaults = {
    'bundle'          : None,
    'codebase_text'   : None,
    'analysis'        : None,
    'stats'           : None,
    'deps'            : None,
    'conversation'    : [],
    'groq_key'        : "",
    'dark_mode'       : False,
    'analyzed'        : False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── CSS ────────────────────────────────────────────────────────
def get_css(dark):
    bg   = "#0e1117" if dark else "#f8f9fa"
    card = "#1e2130" if dark else "#ffffff"
    text = "#fafafa" if dark else "#111111"
    bord = "#444"    if dark else "#dee2e6"
    return f"""
<style>
.stApp {{ background-color:{bg}; color:{text}; }}
.main-title {{
    font-size:2.4rem; font-weight:900;
    background:linear-gradient(90deg,#667eea,#764ba2,#f093fb);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}}
.subtitle {{ font-size:1rem; color:#888; margin-top:-10px; margin-bottom:20px; }}
.analysis-card {{
    background:{card}; border:1px solid {bord};
    border-radius:14px; padding:1.5rem; margin-bottom:1rem;
}}
.stat-box {{
    background:linear-gradient(135deg,#667eea22,#764ba222);
    border:1px solid #667eea55; border-radius:10px;
    padding:1rem; text-align:center;
}}
.chat-user {{
    background:#667eea22; border-radius:12px;
    padding:0.8rem 1rem; margin:0.5rem 0;
    border-left:3px solid #667eea;
}}
.chat-ai {{
    background:{card}; border-radius:12px;
    padding:0.8rem 1rem; margin:0.5rem 0;
    border-left:3px solid #2ecc71;
}}
.stTabs [data-baseweb="tab"] {{ font-weight:700; font-size:0.95rem; }}
</style>"""

st.markdown(get_css(st.session_state.dark_mode), unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏗️ RepoArchitect AI")
    st.markdown("*AI Senior Software Architect*")
    st.divider()

    # Groq API Key
    st.markdown("**🔑 Groq API Key**")
    groq_input = st.text_input(
        "Groq Key", type="password",
        value=st.session_state.groq_key,
        placeholder="gsk_...",
        label_visibility="collapsed",
        help="Free key from console.groq.com"
    )
    if groq_input != st.session_state.groq_key:
        st.session_state.groq_key = groq_input
    if st.session_state.groq_key:
        st.success("Groq Connected ✅")
    else:
        st.warning("Add Groq key to analyze")
        st.caption("👉 console.groq.com (free)")

    st.divider()

    # Project Input
    st.markdown("**📁 Project Path**")
    project_path = st.text_input(
        "Path", placeholder="/path/to/your/project",
        label_visibility="collapsed"
    )

    analyze_btn = st.button("🚀 Analyze Project",
                             use_container_width=True,
                             type="primary",
                             disabled=not (st.session_state.groq_key and project_path))

    # Load existing bundle
    st.divider()
    st.markdown("**📦 Or Load Bundle**")
    uploaded = st.file_uploader("Upload bundle.json", type=['json'],
                                 label_visibility="collapsed")
    if uploaded:
        try:
            bundle_data = json.load(uploaded)
            st.session_state.bundle       = bundle_data
            st.session_state.codebase_text = bundle_to_text(bundle_data)
            st.session_state.stats        = get_project_stats(bundle_data)
            st.session_state.deps         = map_dependencies(bundle_data['files'])
            st.success("Bundle loaded!")
        except Exception as e:
            st.error(f"Invalid bundle: {e}")

    st.divider()
    theme_label = "☀️ Light" if st.session_state.dark_mode else "🌙 Dark"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    if st.session_state.analyzed:
        st.divider()
        st.markdown("**📊 Quick Stats**")
        if st.session_state.stats:
            s = st.session_state.stats
            st.caption(f"📁 {s['total_files']} files")
            st.caption(f"📝 {s['total_lines']:,} lines")
            st.caption(f"🔧 {s['project_type']}")
            if s['frameworks']:
                st.caption(f"⚡ {', '.join(s['frameworks'][:3])}")

# ── HEADER ─────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏗️ RepoArchitect AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Codebase Analysis • Architecture Mapping • Security Audit • AI Senior Architect</div>',
            unsafe_allow_html=True)
st.divider()

# ── ANALYZE PROJECT ────────────────────────────────────────────
if analyze_btn and project_path and st.session_state.groq_key:
    with st.status("🔍 Scanning project...", expanded=True) as status:
        try:
            st.write("📁 Bundling project files...")
            bundle = bundle_project(project_path)
            st.session_state.bundle        = bundle
            st.session_state.codebase_text = bundle_to_text(bundle)
            st.session_state.stats         = get_project_stats(bundle)
            st.session_state.deps          = map_dependencies(bundle['files'])

            st.write(f"✅ {bundle['metadata']['total_files']} files bundled")
            st.write("🤖 Running AI analysis (4 passes)...")

            client = get_groq_client(st.session_state.groq_key)
            progress = st.progress(0)

            def update_progress(msg, val):
                st.write(msg)
                progress.progress(val)

            results = run_full_analysis(
                client,
                st.session_state.codebase_text,
                progress_callback=update_progress
            )
            st.session_state.analysis = results
            st.session_state.analyzed = True
            status.update(label="✅ Analysis Complete!", state="complete")
        except Exception as e:
            status.update(label=f"❌ Error: {e}", state="error")
            st.error(f"Error: {e}")

# ── MAIN CONTENT ───────────────────────────────────────────────
if not st.session_state.bundle and not st.session_state.analyzed:
    # Landing page
    st.markdown("## 👋 Welcome to RepoArchitect AI")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="analysis-card">
        <h3>🏗️ Architecture Analysis</h3>
        <p>Understand your codebase structure, component relationships, and data flow at a glance.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="analysis-card">
        <h3>🔒 Security Audit</h3>
        <p>Detect hardcoded secrets, injection risks, auth flaws, and security anti-patterns.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="analysis-card">
        <h3>🤖 AI Architect Chat</h3>
        <p>Ask questions about your codebase. Get production-ready code. Interactive dialogue.</p>
        </div>""", unsafe_allow_html=True)

    st.info("👈 **Add your Groq API key and project path in the sidebar to get started!**")

    st.markdown("### 🚀 Quick Start")
    st.code("""# Option 1: Use the sidebar
# Enter your project path and click Analyze

# Option 2: Bundle via CLI first
python cli/bundler.py --path /your/project --output outputs/bundle.json
# Then upload bundle.json in the sidebar""", language="bash")

else:
    # ── TABS ──────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Overview",
        "🏗️ Architecture",
        "🔒 Security",
        "📝 Code Quality",
        "🗺️ Roadmap",
        "🤖 AI Architect Chat",
        "🌐 Dependencies"
    ])

    stats = st.session_state.stats
    deps  = st.session_state.deps
    analysis = st.session_state.analysis or {}

    # ── TAB 1: Overview ───────────────────────────────────────
    with tabs[0]:
        st.header("📊 Project Overview")

        if stats:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Files",  stats['total_files'])
            c2.metric("Total Lines",  f"{stats['total_lines']:,}")
            c3.metric("Project Type", stats['project_type'].split('(')[0].strip())
            c4.metric("Frameworks",   len(stats.get('frameworks', [])))

            st.divider()
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📁 File Structure")
                tree = generate_structure_tree(st.session_state.bundle['files'])
                st.code(tree, language=None)

            with col2:
                st.subheader("🔧 Tech Stack Detected")
                if stats.get('frameworks'):
                    for fw in stats['frameworks']:
                        st.markdown(f"✅ **{fw}**")
                else:
                    st.info("No major frameworks detected")

                st.divider()
                st.subheader("📊 Language Breakdown")
                if stats.get('type_readable'):
                    lang_data = {k: v for k, v in stats['type_readable'].items()
                                 if k not in ['Markdown', 'JSON']}
                    if lang_data:
                        bg = '#0e1117' if st.session_state.dark_mode else '#ffffff'
                        tc = 'white'   if st.session_state.dark_mode else 'black'
                        fig, ax = plt.subplots(figsize=(6, 4))
                        fig.patch.set_facecolor(bg)
                        ax.set_facecolor(bg)
                        colors = ['#667eea','#764ba2','#f093fb','#2ecc71',
                                  '#3498db','#e74c3c','#f39c12','#1abc9c']
                        wedges, texts, autotexts = ax.pie(
                            list(lang_data.values()),
                            labels=list(lang_data.keys()),
                            autopct='%1.1f%%',
                            colors=colors[:len(lang_data)],
                            textprops={'color': tc}
                        )
                        for at in autotexts:
                            at.set_color(tc)
                        ax.set_title('Files by Language', color=tc, fontweight='bold')
                        st.pyplot(fig)

            st.divider()
            st.subheader("📋 Largest Files")
            if stats.get('largest_files'):
                for path, lines in stats['largest_files'][:8]:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"📄 `{path}`")
                    with col2:
                        st.markdown(f"`{lines:,} lines`")

    # ── TAB 2: Architecture ───────────────────────────────────
    with tabs[1]:
        st.header("🏗️ Architecture Analysis")
        if analysis.get('architecture'):
            st.markdown(analysis['architecture'])
        elif st.session_state.bundle and st.session_state.groq_key:
            if st.button("🔍 Run Architecture Analysis"):
                with st.spinner("Analyzing architecture..."):
                    from core.analyzer import analyze_architecture
                    client = get_groq_client(st.session_state.groq_key)
                    result = analyze_architecture(client, st.session_state.codebase_text)
                    if not st.session_state.analysis:
                        st.session_state.analysis = {}
                    st.session_state.analysis['architecture'] = result
                    st.rerun()
        else:
            st.info("Run full analysis or add Groq key to analyze.")

    # ── TAB 3: Security ───────────────────────────────────────
    with tabs[2]:
        st.header("🔒 Security Audit")
        if analysis.get('security'):
            st.markdown(analysis['security'])
        elif st.session_state.bundle and st.session_state.groq_key:
            if st.button("🔒 Run Security Audit"):
                with st.spinner("Scanning for security issues..."):
                    from core.analyzer import analyze_security
                    client = get_groq_client(st.session_state.groq_key)
                    result = analyze_security(client, st.session_state.codebase_text)
                    if not st.session_state.analysis:
                        st.session_state.analysis = {}
                    st.session_state.analysis['security'] = result
                    st.rerun()
        else:
            st.info("Run full analysis or add Groq key to analyze.")

    # ── TAB 4: Code Quality ───────────────────────────────────
    with tabs[3]:
        st.header("📝 Code Quality Report")
        if analysis.get('quality'):
            st.markdown(analysis['quality'])
        elif st.session_state.bundle and st.session_state.groq_key:
            if st.button("📝 Run Quality Analysis"):
                with st.spinner("Checking code quality..."):
                    from core.analyzer import analyze_code_quality
                    client = get_groq_client(st.session_state.groq_key)
                    result = analyze_code_quality(client, st.session_state.codebase_text)
                    if not st.session_state.analysis:
                        st.session_state.analysis = {}
                    st.session_state.analysis['quality'] = result
                    st.rerun()
        else:
            st.info("Run full analysis or add Groq key to analyze.")

    # ── TAB 5: Roadmap ────────────────────────────────────────
    with tabs[4]:
        st.header("🗺️ Feature & Improvement Roadmap")
        if analysis.get('roadmap'):
            st.markdown(analysis['roadmap'])

            # Download roadmap
            st.divider()
            roadmap_text = f"# RepoArchitect AI — Project Roadmap\n\nGenerated: {datetime.now().strftime('%d %B %Y')}\n\n"
            roadmap_text += analysis['roadmap']
            st.download_button(
                "📥 Download Roadmap (Markdown)",
                data=roadmap_text,
                file_name="roadmap.md",
                mime="text/markdown"
            )
        elif st.session_state.bundle and st.session_state.groq_key:
            if st.button("🗺️ Generate Roadmap"):
                with st.spinner("Generating roadmap..."):
                    from core.analyzer import generate_roadmap
                    client = get_groq_client(st.session_state.groq_key)
                    arch = analysis.get('architecture', '')
                    sec  = analysis.get('security', '')
                    qual = analysis.get('quality', '')
                    result = generate_roadmap(
                        client, st.session_state.codebase_text, arch, sec, qual
                    )
                    if not st.session_state.analysis:
                        st.session_state.analysis = {}
                    st.session_state.analysis['roadmap'] = result
                    st.rerun()
        else:
            st.info("Run full analysis to generate roadmap.")

    # ── TAB 6: AI Architect Chat ──────────────────────────────
    with tabs[5]:
        st.header("🤖 AI Senior Architect Chat")
        st.markdown("Ask anything about your codebase. For vague questions or TODOs, the AI will ask clarifying questions first.")

        if not st.session_state.groq_key:
            st.warning("Add your Groq API key in the sidebar to use the chat.")
        elif not st.session_state.bundle:
            st.info("Analyze a project first to start chatting.")
        else:
            # Display conversation
            if st.session_state.conversation:
                for msg in st.session_state.conversation:
                    if msg['role'] == 'user':
                        st.markdown(f'<div class="chat-user">👤 <b>You:</b> {msg["content"]}</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-ai">🤖 <b>Architect:</b><br>{msg["content"]}</div>',
                                    unsafe_allow_html=True)
                st.divider()

            # Example questions
            if not st.session_state.conversation:
                st.markdown("**💡 Example questions:**")
                examples = [
                    "What is the overall architecture of this project?",
                    "Are there any security vulnerabilities I should fix immediately?",
                    "How can I improve the performance of this codebase?",
                    "What design patterns are missing that would improve this code?",
                    "Explain how the data flows through this system",
                ]
                for ex in examples:
                    if st.button(ex, key=f"ex_{ex[:20]}"):
                        st.session_state['prefill'] = ex
                        st.rerun()

            # Chat input
            prefill = st.session_state.pop('prefill', '')
            user_input = st.text_area(
                "Ask the AI Architect",
                value=prefill,
                placeholder="e.g. How can I refactor the authentication module?",
                height=100,
                label_visibility="collapsed"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                send_btn = st.button("Send 🚀", type="primary", use_container_width=True)
            with col2:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.conversation = []
                    st.rerun()

            if send_btn and user_input.strip():
                with st.spinner("🤖 AI Architect is thinking..."):
                    client   = get_groq_client(st.session_state.groq_key)
                    response = ask_architect(
                        client,
                        st.session_state.codebase_text,
                        user_input,
                        st.session_state.conversation
                    )
                    st.session_state.conversation.append(
                        {"role": "user", "content": user_input})
                    st.session_state.conversation.append(
                        {"role": "assistant", "content": response})
                    st.rerun()

    # ── TAB 7: Dependencies ───────────────────────────────────
    with tabs[6]:
        st.header("🌐 Dependency Map")
        if deps:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📦 External Packages")
                st.metric("Total External Deps", deps['total_external'])
                if deps['external_packages']:
                    top_deps = dict(list(deps['external_packages'].items())[:20])
                    bg = '#0e1117' if st.session_state.dark_mode else '#ffffff'
                    tc = 'white'   if st.session_state.dark_mode else 'black'
                    fig, ax = plt.subplots(figsize=(8, 5))
                    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
                    pkgs   = list(top_deps.keys())
                    counts = list(top_deps.values())
                    bars   = ax.barh(pkgs, counts, color='#667eea', alpha=0.85)
                    ax.set_xlabel('Import Count', color=tc)
                    ax.set_title('Most Used External Packages', color=tc, fontweight='bold')
                    ax.tick_params(colors=tc)
                    for spine in ax.spines.values(): spine.set_color('#444')
                    for bar, count in zip(bars, counts):
                        ax.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2,
                                str(count), va='center', color=tc, fontsize=9)
                    plt.tight_layout()
                    st.pyplot(fig)

            with col2:
                st.subheader("📄 Per-File Dependencies")
                file_deps = deps.get('file_dependencies', {})
                for filepath, imports in list(file_deps.items())[:15]:
                    if imports:
                        with st.expander(f"📄 {filepath}"):
                            st.write(", ".join(imports))
        else:
            st.info("Analyze a project to see dependency map.")
