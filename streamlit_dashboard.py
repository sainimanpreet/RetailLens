import streamlit as st
import requests

st.set_page_config(
    page_title="RetailLens Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RetailLens AI Dashboard")

API = "http://127.0.0.1:8000"

try:
    metrics = requests.get(f"{API}/metrics").json()

    col1, col2, col3 = st.columns(3)

    col1.metric("Entries", metrics["entries"])
    col2.metric("Exits", metrics["exits"])
    col3.metric("Total Events", metrics["total_events"])

    st.divider()

    st.subheader("Store Analytics")

    st.write(f"**Total Events:** {metrics['total_events']}")
    st.write(f"**Entries:** {metrics['entries']}")
    st.write(f"**Exits:** {metrics['exits']}")

except Exception as e:
    st.error(f"Backend error: {e}")