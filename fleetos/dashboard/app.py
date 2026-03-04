"""
FleetOS Dashboard — Streamlit real-time monitoring UI.

Run with:
    streamlit run fleetos/dashboard/app.py

Features:
  • Live fleet run progress
  • Agent confidence scores
  • Artifact browser
  • Approval queue
  • Memory / knowledge graph summary
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="FleetOS Control Centre",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

def _init_state():
    defaults = {
        "run_history": [],          # list of completed run results
        "current_run": None,        # dict while a run is in progress
        "approval_queue": [],       # runs waiting for human approval
        "total_artifacts": 0,
        "total_runs": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()

# ---------------------------------------------------------------------------
# Sidebar — configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=FleetOS", use_column_width=True)
    st.markdown("---")

    st.subheader("⚙️ Configuration")
    ollama_url = st.text_input(
        "Ollama URL",
        value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    model = st.text_input(
        "Model",
        value=os.getenv("OLLAMA_MODEL", "llama3.1"),
    )
    max_parallel = st.slider("Max Parallel Agents", 1, 8, 4)
    auto_approve = st.checkbox("Auto-approve high-confidence runs (≥80)", value=True)

    st.markdown("---")
    st.subheader("📊 Session Stats")
    st.metric("Total Runs", st.session_state.total_runs)
    st.metric("Total Artifacts", st.session_state.total_artifacts)

    approval_count = len(st.session_state.approval_queue)
    st.metric("Pending Approvals", approval_count, delta=approval_count or None)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

col_title, col_status = st.columns([3, 1])
with col_title:
    st.title("🚀 FleetOS Control Centre")
    st.caption("Autonomous AI fleet — plan, execute, and grow your business.")

with col_status:
    # Ollama health check
    _ollama_ok = False
    try:
        import urllib.request
        with urllib.request.urlopen(f"{ollama_url}/api/tags", timeout=2) as r:
            _ollama_ok = r.status == 200
    except Exception:
        pass

    st.metric("Ollama", "🟢 Online" if _ollama_ok else "🔴 Offline")

st.markdown("---")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_run, tab_history, tab_approvals, tab_memory = st.tabs(
    ["▶  Run Fleet", "📋 History", "✅ Approvals", "🧠 Memory"]
)

# ------------------------------------------------------------------ TAB 1 --
with tab_run:
    st.subheader("Launch a new fleet run")

    col_cmd, col_tpl = st.columns([3, 1])
    with col_cmd:
        command = st.text_area(
            "Command",
            placeholder='e.g. "Launch my AI newsletter to $15k MRR in 90 days"',
            height=80,
        )
    with col_tpl:
        template_choice = st.selectbox(
            "Template",
            ["auto-detect", "newsletter_v1", "leadgen_agency_v1", "microsaas_v1"],
        )

    launch = st.button("🚀 Launch Fleet", type="primary", disabled=not command.strip())

    if launch and command.strip():
        # Build state for the graph
        state: Dict[str, Any] = {
            "raw_command": command,
            "session_id": f"run_{int(time.time())}",
            "status": "starting",
        }

        if template_choice != "auto-detect":
            # Force the selected template
            state["template_name"] = template_choice

        progress_bar = st.progress(0, text="Initialising fleet…")
        status_area = st.empty()
        results_area = st.empty()

        steps = [
            (10, "Parsing command…"),
            (25, "Planning fleet roles…"),
            (40, "Scoring confidence…"),
            (60, "Executing agents in parallel…"),
            (80, "Collecting artifacts…"),
            (90, "Storing to memory…"),
            (100, "Generating report…"),
        ]

        try:
            # Import graph lazily
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
            from fleetos.core.graph import build_graph, FleetState

            graph = build_graph()

            # Simulate step-by-step progress for UX
            for pct, label in steps[:-2]:
                progress_bar.progress(pct, text=label)
                time.sleep(0.3)

            # Actual execution
            progress_bar.progress(60, text="Executing agents in parallel…")
            result_state: FleetState = graph.invoke(state)  # type: ignore

            progress_bar.progress(100, text="✅ Complete!")
            status_area.success(f"Run finished — {len(result_state.get('results', []))} artifacts")

            # Store in history
            st.session_state.run_history.insert(0, result_state)
            st.session_state.total_runs += 1
            st.session_state.total_artifacts += result_state.get("artifacts_stored", 0)

            # Display summary
            summary = result_state.get("summary", "No summary generated.")
            results_area.markdown(f"```\n{summary}\n```")

            # Approval queue
            if result_state.get("needs_approval") and not result_state.get("approved"):
                st.session_state.approval_queue.append(result_state)
                st.warning("⏸️ Run paused — human approval required. Check the Approvals tab.")

        except Exception as exc:
            progress_bar.progress(100, text="❌ Error")
            status_area.error(f"Fleet run failed: {exc}")
            st.exception(exc)

# ------------------------------------------------------------------ TAB 2 --
with tab_history:
    st.subheader("Run history")

    if not st.session_state.run_history:
        st.info("No runs yet. Launch a fleet from the Run tab.")
    else:
        for idx, run in enumerate(st.session_state.run_history):
            session_id = run.get("session_id", f"run_{idx}")
            completed = run.get("completed_at", "—")
            status_icon = "✅" if run.get("status") == "success" else "⚠️"
            confidence = run.get("confidence", 0)

            with st.expander(f"{status_icon} {session_id}  |  {completed}  |  Confidence: {confidence:.0f}/100"):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Agents", len(run.get("agents", [])))
                col_b.metric("Artifacts", len(run.get("results", [])))
                col_c.metric("Errors", len(run.get("errors", [])))

                st.markdown("**Summary**")
                st.code(run.get("summary", "—"), language="text")

                if run.get("results"):
                    st.markdown("**Artifacts**")
                    for artifact in run["results"]:
                        role = artifact.get("role", "?")
                        output = artifact.get("artifact") or artifact.get("output") or "—"
                        st.markdown(f"**`{role}`**")
                        st.markdown(str(output)[:800])
                        st.markdown("---")

# ------------------------------------------------------------------ TAB 3 --
with tab_approvals:
    st.subheader("Approval queue")

    if not st.session_state.approval_queue:
        st.success("No pending approvals — all clear!")
    else:
        for idx, run in enumerate(list(st.session_state.approval_queue)):
            session_id = run.get("session_id", f"run_{idx}")
            confidence = run.get("confidence", 0)
            risk = run.get("risk_level", "unknown")

            with st.expander(f"⏸️ {session_id}  |  Confidence: {confidence:.0f}  |  Risk: {risk.upper()}"):
                st.markdown(f"**Command:** {run.get('raw_command', '—')}")
                st.markdown(f"**Template:** {run.get('template_name', '—')}")
                st.markdown("**Planned agents:**")
                for a in run.get("agents", []):
                    st.markdown(f"- **{a['role']}**: {a['task'][:100]}")

                col_approve, col_reject = st.columns(2)
                if col_approve.button("✅ Approve", key=f"approve_{idx}"):
                    run["approved"] = True
                    run["approval_reason"] = "manual_dashboard"
                    st.session_state.approval_queue.pop(idx)
                    st.session_state.run_history.insert(0, run)
                    st.rerun()

                if col_reject.button("❌ Reject", key=f"reject_{idx}"):
                    run["approved"] = False
                    run["status"] = "rejected"
                    st.session_state.approval_queue.pop(idx)
                    st.rerun()

# ------------------------------------------------------------------ TAB 4 --
with tab_memory:
    st.subheader("🧠 Memory store")
    st.caption("Artifacts accumulated across all fleet runs in this session.")

    all_artifacts = []
    for run in st.session_state.run_history:
        for artifact in run.get("results", []):
            all_artifacts.append({
                "session": run.get("session_id", "?"),
                "role": artifact.get("role", "?"),
                "content": str(artifact.get("artifact") or artifact.get("output") or "—"),
                "timestamp": artifact.get("timestamp", "?"),
            })

    if not all_artifacts:
        st.info("Memory is empty. Run the fleet to populate it.")
    else:
        # Filter
        roles = list({a["role"] for a in all_artifacts})
        selected_role = st.selectbox("Filter by role", ["All"] + sorted(roles))
        search_query = st.text_input("Search content", placeholder="keyword…")

        filtered = all_artifacts
        if selected_role != "All":
            filtered = [a for a in filtered if a["role"] == selected_role]
        if search_query:
            filtered = [a for a in filtered if search_query.lower() in a["content"].lower()]

        st.markdown(f"**{len(filtered)} artifacts**")
        for a in filtered:
            with st.expander(f"[{a['role']}] {a['timestamp'][:19]}"):
                st.markdown(f"**Session:** `{a['session']}`")
                st.markdown(a["content"][:1000])

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.caption(f"FleetOS v0.2.0 · {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC · Model: {model}")
