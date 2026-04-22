import streamlit as st
import os
import tempfile

from core.parser import load_profile, ControlFile
from core.recon_calc import ReconAnalyzer
from core.reporter import generate_html_report, generate_markdown_report

# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ReconCalc Python Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Session state initialisation
# ─────────────────────────────────────────────
if "test_cases" not in st.session_state:
    st.session_state.test_cases = {}   # filename -> set(procedures)
if "features" not in st.session_state:
    st.session_state.features = []     # [{name, test_cases: [str]}]
if "results" not in st.session_state:
    st.session_state.results = None

# ─────────────────────────────────────────────
#  Sidebar – navigation & reset
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🔍 ReconCalc")
    st.caption("Software Reconnaissance Tool")
    st.divider()

    st.markdown(f"**Test Cases loaded:** {len(st.session_state.test_cases)}")
    st.markdown(f"**Features defined:** {len(st.session_state.features)}")

    st.divider()
    if st.button("🗑️ Reset Everything", use_container_width=True):
        st.session_state.test_cases = {}
        st.session_state.features = []
        st.session_state.results = None
        st.rerun()

    st.divider()
    st.markdown("### About")
    st.caption(
        "ReconCalc maps software **features** to code **procedures** "
        "using set operations on execution profiles."
    )

# ─────────────────────────────────────────────
#  Main area – tabs
# ─────────────────────────────────────────────
st.title("🔍 ReconCalc Python Pro")
st.markdown("Map software features to code elements using Software Reconnaissance.")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📁 1. Load Profiles", "🏷️ 2. Define Features", "📊 3. Run Analysis", "📄 4. Export Report"]
)

# ── TAB 1: Load Profiles ────────────────────
with tab1:
    st.header("Load Execution Profiles")
    st.markdown(
        "Upload your execution profile files (`.pro` or `.txt`). "
        "Each file represents one test case."
    )

    col_upload, col_ctl = st.columns(2)

    with col_upload:
        st.subheader("Upload Profile Files")
        uploaded_files = st.file_uploader(
            "Choose profile files",
            accept_multiple_files=True,
            type=["txt", "pro"],
            label_visibility="collapsed",
        )
        if st.button("➕ Add Profiles", use_container_width=True):
            if uploaded_files:
                for f in uploaded_files:
                    content = f.read().decode("utf-8")
                    procedures = {line.strip() for line in content.splitlines() if line.strip()}
                    st.session_state.test_cases[f.name] = procedures
                st.success(f"Loaded {len(uploaded_files)} profile(s).")
            else:
                st.warning("No files selected.")

    with col_ctl:
        st.subheader("Or Import a Control File (.ctl)")
        ctl_file = st.file_uploader(
            "Choose a .ctl file",
            type=["ctl"],
            label_visibility="collapsed",
            key="ctl_uploader",
        )
        if st.button("📂 Import from .ctl", use_container_width=True):
            if ctl_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ctl", mode="wb") as tmp:
                    tmp.write(ctl_file.read())
                    tmp_path = tmp.name

                ctl = ControlFile(tmp_path)
                os.unlink(tmp_path)

                st.info(
                    f"Control file detected **{len(ctl.features)}** features "
                    f"and **{len(ctl.testcases)}** test cases.\n\n"
                    "⚠️ Profile files still need to be uploaded above — "
                    "the .ctl file only defines the mapping."
                )
                # Pre-populate features from the control file
                st.session_state.features = [
                    {"name": feat, "test_cases": mapping}
                    for feat, mapping in zip(ctl.features, ctl.mapping)
                ]
                st.success("Features imported from control file!")
            else:
                st.warning("No .ctl file selected.")

    st.divider()
    if st.session_state.test_cases:
        st.subheader("Loaded Test Cases")
        for name, procs in st.session_state.test_cases.items():
            with st.expander(f"📄 `{name}` — {len(procs)} procedures"):
                st.code("\n".join(sorted(procs)))
    else:
        st.info("No profiles loaded yet.")

# ── TAB 2: Define Features ──────────────────
with tab2:
    st.header("Define Features")
    st.markdown(
        "Add the software features you want to map, then select which test cases **exhibit** each one."
    )

    if not st.session_state.test_cases:
        st.warning("Please load profile files in Tab 1 first.")
    else:
        with st.form("add_feature_form", clear_on_submit=True):
            feat_name = st.text_input("Feature Name", placeholder="e.g. Rotate House")
            exhibited_by = st.multiselect(
                "Exhibited by test cases:",
                options=list(st.session_state.test_cases.keys()),
            )
            submitted = st.form_submit_button("➕ Add Feature", use_container_width=True)
            if submitted:
                if not feat_name:
                    st.error("Please enter a feature name.")
                elif any(f["name"] == feat_name for f in st.session_state.features):
                    st.error(f'Feature "{feat_name}" already exists.')
                else:
                    st.session_state.features.append(
                        {"name": feat_name, "test_cases": exhibited_by}
                    )
                    st.success(f'Added feature: "{feat_name}"')

        st.divider()
        if st.session_state.features:
            st.subheader("Current Feature Mapping")
            for i, feat in enumerate(st.session_state.features):
                col_feat, col_del = st.columns([5, 1])
                with col_feat:
                    tc_str = ", ".join(f"`{t}`" for t in feat["test_cases"]) or "_none_"
                    st.markdown(f"**{i+1}. {feat['name']}** → {tc_str}")
                with col_del:
                    if st.button("✖", key=f"del_{i}"):
                        st.session_state.features.pop(i)
                        st.rerun()
        else:
            st.info("No features defined yet.")

# ── TAB 3: Run Analysis ─────────────────────
with tab3:
    st.header("Run Analysis")

    ready = st.session_state.test_cases and st.session_state.features
    if not ready:
        st.warning("Complete Steps 1 and 2 before running the analysis.")
    else:
        if st.button("🚀 Run Reconnaissance", use_container_width=True, type="primary"):
            with st.spinner("Performing set operations..."):
                features = [f["name"] for f in st.session_state.features]
                testcases = list(st.session_state.test_cases.keys())
                mapping = [f["test_cases"] for f in st.session_state.features]

                def profile_loader(name):
                    return st.session_state.test_cases.get(name, set())

                analyzer = ReconAnalyzer(features, testcases, mapping, profile_loader)
                st.session_state.results = analyzer.analyze_all()
            st.success("Analysis complete!")

    if st.session_state.results:
        results = st.session_state.results
        st.divider()
        st.subheader("🔵 Common Elements (CELEMS)")
        st.caption(f"{len(results['celems'])} procedure(s) always executed")
        st.code("\n".join(sorted(results["celems"])) or "None", language=None)

        for feat in results["features"]:
            st.divider()
            st.subheader(f"Feature: {feat['name']}")
            cols = st.columns(2)
            sections = [
                ("🟡 Unique (UELEMS)", feat["uelems"]),
                ("🟠 Relevant (RELEMS)", feat["relems"]),
                ("🟣 Always Involved (IIELEMS)", feat["iielems"]),
                ("🔵 Involved (IELEMS)", feat["ielems"]),
                ("🟤 Shared (SHARED)", feat["shared"]),
            ]
            for idx, (label, elems) in enumerate(sections):
                with cols[idx % 2]:
                    st.markdown(f"**{label}** — {len(elems)} item(s)")
                    st.code("\n".join(sorted(elems)) or "None", language=None)

# ── TAB 4: Export Report ────────────────────
with tab4:
    st.header("Export Report")

    if not st.session_state.results:
        st.warning("Run the analysis in Tab 3 first.")
    else:
        col_html, col_md = st.columns(2)

        with col_html:
            st.subheader("HTML Report")
            html = generate_html_report(st.session_state.results)
            st.download_button(
                label="⬇️ Download HTML Report",
                data=html,
                file_name="reconnaissance_report.html",
                mime="text/html",
                use_container_width=True,
            )

        with col_md:
            st.subheader("Markdown Report")
            md = generate_markdown_report(st.session_state.results)
            st.download_button(
                label="⬇️ Download Markdown Report",
                data=md,
                file_name="reconnaissance_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.divider()
        st.subheader("Preview")
        st.components.v1.html(generate_html_report(st.session_state.results), height=600, scrolling=True)
