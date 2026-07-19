"""
RepoArchitect AI — Core Analyzer
Uses Groq LLaMA3 to analyze codebase architecture, security, and generate roadmap.
"""

import os
import json
from groq import Groq
from typing import Optional

# ── Groq Client ────────────────────────────────────────────────
def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def groq_call(client: Groq, prompt: str, system: str = None,
              max_tokens: int = 2000, model: str = "llama3-8b-8192") -> str:
    """Make a Groq API call and return response text."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Groq Error: {e}"


# ── Analysis Functions ─────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert Senior Software Architect and Security Engineer.
You analyze codebases and provide clear, actionable insights.
Always respond in structured format with emojis for readability.
Be specific — reference actual file names and code patterns you see."""


def analyze_architecture(client: Groq, codebase_text: str) -> str:
    """Analyze overall architecture of the codebase."""
    prompt = f"""Analyze the architecture of this codebase:

{codebase_text[:8000]}

Provide a detailed architecture analysis covering:

## 🏗️ Architecture Overview
- What type of architecture is this? (MVC, microservices, monolith, etc.)
- Main components and their responsibilities
- How components interact with each other

## 📁 Project Structure Analysis
- Is the folder structure logical and well-organized?
- What naming conventions are used?
- Any structural anti-patterns observed?

## 🔄 Data Flow
- How does data flow through the system?
- Entry points and exit points
- Key data transformations

## ⚠️ Structural Issues Found
- List specific structural problems with file references
- Tight coupling issues
- Missing abstractions or over-engineering

## ✅ Strengths
- What is done well architecturally?

Be specific and reference actual files/folders you see."""

    return groq_call(client, prompt, SYSTEM_PROMPT, max_tokens=2000)


def analyze_security(client: Groq, codebase_text: str) -> str:
    """Detect security anti-patterns and vulnerabilities."""
    prompt = f"""Perform a security audit of this codebase:

{codebase_text[:8000]}

Identify security issues and anti-patterns:

## 🔴 Critical Security Issues
- SQL injection risks
- Hardcoded secrets or API keys
- Exposed sensitive data
- Authentication/authorization flaws

## 🟡 Medium Risk Issues
- Input validation missing
- Insecure dependencies patterns
- CORS misconfiguration
- Error messages exposing internals

## 🟢 Low Risk / Best Practice Violations
- Missing rate limiting
- Logging sensitive data
- Weak error handling

## 🛡️ Security Score: X/10
Brief justification for the score.

## 🔧 Fix Recommendations
Top 5 specific fixes with code examples where possible.

Reference actual file names and line patterns you find."""

    return groq_call(client, prompt, SYSTEM_PROMPT, max_tokens=2000)


def analyze_code_quality(client: Groq, codebase_text: str) -> str:
    """Analyze code quality, patterns, and maintainability."""
    prompt = f"""Analyze the code quality of this codebase:

{codebase_text[:8000]}

## 📊 Code Quality Metrics
- Estimated maintainability score (1-10)
- Code duplication assessment
- Function/class complexity

## 🎨 Design Patterns Used
- Which patterns are correctly implemented?
- Which patterns are misused?
- Missing patterns that would help

## 🧹 Code Smells Detected
- Long functions or classes
- Dead code
- Magic numbers/strings
- Poor naming conventions

## 📝 Documentation Quality
- Is the code well-commented?
- Missing docstrings?
- README quality

## 🔧 Top Refactoring Suggestions
List 5 specific refactoring suggestions with file references."""

    return groq_call(client, prompt, SYSTEM_PROMPT, max_tokens=2000)


def generate_roadmap(client: Groq, codebase_text: str, architecture: str,
                     security: str, quality: str) -> str:
    """Generate an advanced feature roadmap based on analysis."""
    prompt = f"""Based on this codebase analysis, generate a detailed improvement roadmap.

CODEBASE SUMMARY:
{codebase_text[:3000]}

ARCHITECTURE ISSUES FOUND:
{architecture[:1000]}

SECURITY ISSUES FOUND:
{security[:1000]}

QUALITY ISSUES FOUND:
{quality[:1000]}

Generate a prioritized roadmap:

## 🗺️ Feature & Improvement Roadmap

### 🔴 Phase 1: Critical Fixes (Week 1-2)
- Must-do security and stability fixes
- Each item: what, why, estimated effort

### 🟡 Phase 2: Architecture Improvements (Month 1)
- Refactoring and structural improvements
- Each item: what, why, estimated effort

### 🟢 Phase 3: Feature Enhancements (Month 2-3)
- New features based on existing patterns
- Each item: what, why, estimated effort

### 🔵 Phase 4: Advanced & Scaling (Month 3-6)
- Long-term improvements
- Performance, scaling, monitoring

### 📈 Tech Debt Summary
- Total estimated tech debt hours
- Priority order to tackle

Be specific to THIS codebase, not generic advice."""

    return groq_call(client, prompt, SYSTEM_PROMPT, max_tokens=2500)


def ask_architect(client: Groq, codebase_text: str,
                  question: str, conversation_history: list) -> str:
    """
    Interactive AI Senior Architect — answers questions about the codebase.
    Maintains conversation history for context.
    """
    system = """You are an AI Senior Software Architect with deep knowledge of this specific codebase.
You have analyzed every file and understand the full system.
Answer questions precisely, referencing actual files and code patterns.
If the question is vague, ask ONE clarifying question before answering.
For incomplete code or TODOs, ask about requirements before generating code."""

    # Build conversation with history
    messages = [{"role": "system", "content": system}]

    # Add codebase context to first message
    context_msg = f"""I have analyzed this codebase for you:

{codebase_text[:5000]}

You are now the expert on this codebase. Answer questions about it."""
    messages.append({"role": "user", "content": context_msg})
    messages.append({"role": "assistant",
                     "content": "I have thoroughly analyzed your codebase and I'm ready to assist as your Senior Software Architect. What would you like to know?"})

    # Add conversation history
    for msg in conversation_history[-6:]:  # Keep last 6 exchanges for context
        messages.append(msg)

    # Add current question
    messages.append({"role": "user", "content": question})

    try:
        resp = client.chat.completions.create(
            model="llama3-70b-8192",  # Use larger model for interactive Q&A
            messages=messages,
            max_tokens=1500,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to 8b model
        try:
            resp = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=1500,
                temperature=0.4
            )
            return resp.choices[0].message.content.strip()
        except Exception as e2:
            return f"❌ Error: {e2}"


def run_full_analysis(client: Groq, codebase_text: str,
                      progress_callback=None) -> dict:
    """
    Run complete analysis pipeline.
    Returns dict with all analysis results.
    """
    results = {}

    if progress_callback: progress_callback("🏗️ Analyzing architecture...", 0.2)
    results['architecture'] = analyze_architecture(client, codebase_text)

    if progress_callback: progress_callback("🔒 Scanning security...", 0.4)
    results['security'] = analyze_security(client, codebase_text)

    if progress_callback: progress_callback("📊 Checking code quality...", 0.6)
    results['quality'] = analyze_code_quality(client, codebase_text)

    if progress_callback: progress_callback("🗺️ Generating roadmap...", 0.8)
    results['roadmap'] = generate_roadmap(
        client, codebase_text,
        results['architecture'],
        results['security'],
        results['quality']
    )

    if progress_callback: progress_callback("✅ Analysis complete!", 1.0)
    return results
