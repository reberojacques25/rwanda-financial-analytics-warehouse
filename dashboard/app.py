"""RFAW Streamlit Dashboard - Rwanda Financial Analytics Warehouse."""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rfaw.config import PROCESSED_DIR, METADATA_DIR

st.set_page_config(
    page_title="RFAW Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏦 Rwanda Financial Analytics Warehouse")
st.markdown("Evidence-based financial analytics using verified public data from BNR, NISR, World Bank, and other authoritative sources.")


def load_data():
    """Load processed data if available."""
    data = {}
    for name in ["interest_rates_monthly.csv", "interest_rates_annual.csv", "macro_indicators.csv"]:
        fpath = PROCESSED_DIR / name
        if fpath.exists():
            data[name.replace(".csv", "")] = pd.read_csv(fpath, parse_dates=["date"])
        else:
            data[name.replace(".csv", "")] = pd.DataFrame()
    return data


def load_source_catalog():
    """Load source catalog."""
    import yaml
    catalog_path = METADATA_DIR / "source_catalog.yml"
    if catalog_path.exists():
        with open(catalog_path) as f:
            return yaml.safe_load(f)
    return {"sources": []}


data = load_data()
catalog = load_source_catalog()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Executive Overview",
    "Interest Rates",
    "Macro Indicators",
    "Data Quality",
    "Sources & Methodology",
    "Limitations"
])

# --- Executive Overview ---
if page == "Executive Overview":
    st.header("Executive Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Data Sources", len(catalog.get("sources", [])))
    with col2:
        ir = data.get("interest_rates_monthly", pd.DataFrame())
        st.metric("Interest Rate Observations", len(ir))
    with col3:
        macro = data.get("macro_indicators", pd.DataFrame())
        st.metric("Macro Observations", len(macro))
    with col4:
        ir_annual = data.get("interest_rates_annual", pd.DataFrame())
        st.metric("Derived Annual Averages", len(ir_annual))

    st.subheader("Key Indicators")
    if not macro.empty:
        latest = macro.sort_values("date").groupby("indicator_id").last().reset_index()
        for _, row in latest.iterrows():
            st.write(f"**{row['indicator_name']}** ({row['date'].strftime('%Y')}): {row['value']:,.2f} {row.get('unit', '')}")

    if data.get("interest_rates_monthly") is not None and not data["interest_rates_monthly"].empty:
        st.subheader("Latest Interest Rates")
        latest_rates = data["interest_rates_monthly"].sort_values("date").groupby("indicator_id").last().reset_index()
        for _, row in latest_rates.iterrows():
            st.write(f"**{row['indicator_name']}** ({row['date'].strftime('%Y-%m')}): {row['value']:.2f}%")

# --- Interest Rates ---
elif page == "Interest Rates":
    st.header("Interest Rate Trends")

    ir_monthly = data.get("interest_rates_monthly", pd.DataFrame())
    ir_annual = data.get("interest_rates_annual", pd.DataFrame())

    if ir_monthly.empty and ir_annual.empty:
        st.warning("No interest rate data available. Run the pipeline first: `python scripts/run_pipeline.py`")
    else:
        if not ir_monthly.empty:
            st.subheader("Monthly Interest Rates")
            indicators = ir_monthly["indicator_id"].unique()
            selected = st.multiselect("Select indicators", indicators, default=list(indicators[:3]))

            filtered = ir_monthly[ir_monthly["indicator_id"].isin(selected)]

            try:
                import plotly.express as px
                fig = px.line(filtered, x="date", y="value", color="indicator_name",
                             title="Monthly Interest Rate Trends", labels={"value": "Rate (%)"})
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.dataframe(filtered)

            st.subheader("Data Table")
            st.dataframe(filtered.sort_values("date", ascending=False))

        if not ir_annual.empty:
            st.subheader("Annual Average Rates (Derived)")
            st.caption("Note: Annual averages are DERIVED metrics computed from monthly observations.")
            st.dataframe(ir_annual.sort_values("date", ascending=False))

            try:
                import plotly.express as px
                fig = px.bar(ir_annual, x="date", y="value", color="indicator_name",
                            title="Annual Average Interest Rates", labels={"value": "Rate (%)"})
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                pass

# --- Macro Indicators ---
elif page == "Macro Indicators":
    st.header("Macroeconomic Indicators")
    macro = data.get("macro_indicators", pd.DataFrame())

    if macro.empty:
        st.warning("No macro data available. Run the pipeline first.")
    else:
        indicators = macro["indicator_id"].unique()
        selected = st.multiselect("Select indicators", indicators, default=list(indicators[:3]))

        filtered = macro[macro["indicator_id"].isin(selected)]

        try:
            import plotly.express as px
            fig = px.line(filtered, x="date", y="value", color="indicator_name",
                         title="Macroeconomic Indicators (World Bank)", labels={"value": "Value"})
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.dataframe(filtered)

        st.subheader("Data Table")
        st.dataframe(filtered.sort_values("date", ascending=False))

        st.caption("Source: World Bank World Development Indicators. Evidence classification: VERIFIED_SECONDARY.")

# --- Data Quality ---
elif page == "Data Quality":
    st.header("Data Quality")

    st.subheader("Source Catalog Validation")
    sources = catalog.get("sources", [])
    st.write(f"Total sources cataloged: **{len(sources)}**")

    ev_classes = {}
    for s in sources:
        ec = s.get("evidence_classification", "UNKNOWN")
        ev_classes[ec] = ev_classes.get(ec, 0) + 1

    st.write("**Evidence Classifications:**")
    for cls, count in ev_classes.items():
        st.write(f"  - {cls}: {count}")

    st.subheader("Observed vs Derived")
    observed = sum(1 for s in sources if s.get("is_observed"))
    derived = sum(1 for s in sources if s.get("is_derived"))
    st.write(f"  - Observed: {observed}")
    st.write(f"  - Derived: {derived}")

# --- Sources & Methodology ---
elif page == "Sources & Methodology":
    st.header("Data Sources & Methodology")

    st.subheader("Source Catalog")
    sources = catalog.get("sources", [])

    for s in sources:
        with st.expander(f"{s.get('source_id', '?')} — {s.get('dataset_name', '?')}"):
            st.write(f"**Organization:** {s.get('source_organization', 'N/A')}")
            st.write(f"**URL:** {s.get('source_url', 'N/A')}")
            st.write(f"**Frequency:** {s.get('frequency', 'N/A')}")
            st.write(f"**Coverage:** {s.get('date_coverage', 'N/A')}")
            st.write(f"**Evidence:** {s.get('evidence_classification', 'N/A')}")
            st.write(f"**Observed:** {s.get('is_observed', 'N/A')} | **Derived:** {s.get('is_derived', 'N/A')}")
            st.write(f"**Limitations:** {s.get('limitations', 'N/A')}")
            st.write(f"**License:** {s.get('license', 'N/A')}")

    st.subheader("Methodology")
    st.markdown("""
    - **Evidence-first approach:** Every observation is traceable to a source URL and retrieval date.
    - **No fabrication:** Missing data is documented as missing, not interpolated.
    - **Observed vs Derived:** Clear separation between observed values and computed metrics.
    - **Evidence classifications:** VERIFIED_PRIMARY, VERIFIED_SECONDARY, DERIVED, ESTIMATED, UNVERIFIED.
    - **Provenance:** Every dataset records source organization, URL, retrieval date, and methodology.
    """)

# --- Limitations ---
elif page == "Limitations":
    st.header("Limitations")

    st.markdown("""
    ### Known Data Limitations

    1. **Bank-level granularity:** Public data supports banking-sector aggregate analysis, not a complete
       bank-by-bank panel for all licensed Rwandan banks.

    2. **PDF extraction required:** BNR financial sector statistics and NISR GDP publications are primarily
       in PDF format. Automated extraction is needed and values must be verified against source documents.

    3. **Frequency alignment:** Interest rate data is monthly; macro indicators are annual. Do not mix
       frequencies without documented aggregation rules.

    4. **Secondary sources:** World Bank and IMF data are VERIFIED_SECONDARY. They compile from national
       sources but may include estimates or revisions.

    5. **NPL ratio vs NPL stock:** BNR publishes NPL ratios more readily than NPL amounts. Do not
       infer NPL stock from rounded ratios.

    6. **Historical revisions:** GDP and national accounts may be revised or rebased. Always preserve
       the publication version and methodology.

    7. **No causal claims:** The data supports descriptive and correlational analysis, not causal inference
       without additional explanatory variables and rigorous methodology.

    8. **Redistribution:** BNR and NISR data redistribution status is unclear. Raw data is not committed
       to the repository. Processed observations are stored locally only.
    """)
