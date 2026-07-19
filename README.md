# 🏗️ RepoArchitect AI
### CBSOT Summer Internship 2026 | Agentic AI + NLP Codebase Analyzer

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-ff4b4b?logo=streamlit)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA3-orange)](https://console.groq.com)
[![LangChain](https://img.shields.io/badge/LangChain-AI%20Agents-green)](https://langchain.com)

> **An AI Senior Software Architect that autonomously analyzes entire codebases, maps architecture, detects security flaws, and answers questions about your code in real-time.**

---

## 📌 What is RepoArchitect AI?

RepoArchitect AI uses **Agentic AI + NLP** to:

1. **Bundle** your entire codebase via a terminal command — no manual copy-paste
2. **Analyze** architecture, security, and code quality as a unified system
3. **Generate** a prioritized improvement roadmap
4. **Chat** interactively with an AI Senior Architect about your code
5. **Map** all external dependencies visually

---

## 🔑 Groq API Key Setup

**Get free key (2 min):**
1. 👉 [console.groq.com](https://console.groq.com) → Sign up → API Keys → Create
2. Copy key (`gsk_...`)
3. Paste in Streamlit sidebar OR add to `.env` file

```bash
# .env file (optional)
GROQ_API_KEY=gsk_your_key_here
```

---

## 🗂️ Project Structure

```
RepoArchitect-AI/
│
├── 📁 cli/
│   ├── bundler.py          # CLI tool — scan & bundle project files
│   └── __init__.py
│
├── 📁 core/
│   ├── analyzer.py         # Groq LLaMA3 analysis engine
│   ├── mapper.py           # Dependency & structure mapper
│   └── __init__.py
│
├── 📁 app/
│   └── app.py              # Streamlit dashboard (7 tabs)
│
├── 📁 outputs/             # Generated bundles & reports
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 How to Run

### Step 1 — Install
```bash
git clone https://github.com/YOUR-USERNAME/RepoArchitect-AI.git
cd RepoArchitect-AI
pip install -r requirements.txt
```

### Step 2 — Bundle Your Project (CLI)
```bash
# Scan any project on your system
python cli/bundler.py --path /path/to/your/project --output outputs/bundle.json
```

### Step 3 — Launch Dashboard
```bash
streamlit run app/app.py
```

### Step 4 — Analyze
- Add Groq API key in sidebar
- Enter project path OR upload `bundle.json`
- Click **Analyze Project**
- Explore 7 analysis tabs

---

## 📱 Dashboard — 7 Tabs

| Tab | Feature |
|---|---|
| 📊 Overview | File stats, language breakdown, project structure tree |
| 🏗️ Architecture | Architecture type, component mapping, data flow, structural issues |
| 🔒 Security | Critical/medium/low security issues, security score, fix recommendations |
| 📝 Code Quality | Design patterns, code smells, maintainability score, refactoring suggestions |
| 🗺️ Roadmap | 4-phase improvement roadmap, tech debt summary, downloadable markdown |
| 🤖 AI Chat | Interactive Q&A with AI Senior Architect — context-aware, asks clarifying questions |
| 🌐 Dependencies | External package map, per-file dependency breakdown |

---

## 🌟 Key Features

### 📦 Smart CLI Bundler
```bash
python cli/bundler.py --path /your/project
```
- Recursively scans 18+ file types
- Skips `node_modules`, `.git`, `__pycache__`, build folders
- Skips files > 500KB
- Generates structured JSON bundle with metadata

### 🏗️ Architecture Analysis (Groq LLaMA3)
- Detects architecture type (MVC, microservices, monolith)
- Maps component relationships
- Identifies structural anti-patterns

### 🔒 Security Audit
- Hardcoded secrets detection
- SQL injection risks
- Authentication/authorization flaws
- Security score (1-10) with fix recommendations

### 🤖 Interactive AI Architect
- Context-aware Q&A about YOUR specific codebase
- Asks clarifying questions for vague inputs
- References actual file names in answers
- Maintains conversation history

### 🌐 Dependency Mapper
- Extracts imports from Python, JS, TS files
- Visualizes most-used external packages
- Per-file dependency breakdown

---

## 🛠️ Tech Stack

| Tool | Use |
|---|---|
| Python 3.10 | Core language |
| Groq LLaMA3-8b / 70b | AI analysis engine |
| LangChain | LLM orchestration |
| Streamlit | Interactive dashboard |
| Matplotlib | Visualizations |
| Pathlib | File system operations |
| Regex | Import extraction |

---

## 🔮 Future Enhancements

- [ ] CrewAI multi-agent orchestration (specialized agents per analysis type)
- [ ] ChromaDB/Qdrant vector DB for semantic code search
- [ ] Next.js frontend dashboard
- [ ] GitHub Actions integration
- [ ] Real-time file watching and re-analysis

---

## 🎓 Acknowledgements

- **Mentor:** Aryesh Rai Sir
- **CBSOT Team:** Kartik Mathur Sir, Varun Kohli Sir, Monu Kumar Sir
- **Organization:** Coding Blocks School of Technology

---

*Built with ❤️ during CBSOT Summer Internship 2026*
