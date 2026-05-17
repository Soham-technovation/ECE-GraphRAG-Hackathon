"""
ECEGraphAI Dashboard Header - Usage Examples

This module provides two professional header components for the Streamlit dashboard:

1. render_header() - Static header with default metrics (47% token reduction)
2. render_header_with_stats() - Dynamic header with real metrics from pipeline runs
"""

import streamlit as st
from dashboard_header import render_header, render_header_with_stats


def example_static_header():
    """Example: Using the static header with default metrics."""
    st.set_page_config(page_title="ECEGraphAI", layout="wide")
    render_header()
    st.write("Main dashboard content goes here...")


def example_dynamic_header():
    """Example: Using the dynamic header with real metrics."""
    st.set_page_config(page_title="ECEGraphAI", layout="wide")

    # Simulated pipeline results
    token_reduction = 47.3  # From actual runs
    cost_reduction = 52.1   # From actual runs
    accuracy_maintained = True

    render_header_with_stats(
        token_reduction=token_reduction,
        cost_reduction=cost_reduction,
        accuracy_maintained=accuracy_maintained
    )

    st.markdown("## Compare Pipeline Performance")
    st.write("Detailed metrics and analysis...")


def example_with_real_data():
    """Example: Integration with actual pipeline results."""
    st.set_page_config(page_title="ECEGraphAI", layout="wide")

    # Assuming you have pipeline results
    rag_tokens = 1500
    graph_tokens = 795
    rag_cost = 0.0045
    graph_cost = 0.0021

    # Calculate percentages
    token_reduction = ((rag_tokens - graph_tokens) / rag_tokens) * 100
    cost_reduction = ((rag_cost - graph_cost) / rag_cost) * 100
    accuracy_maintained = True

    render_header_with_stats(
        token_reduction=token_reduction,
        cost_reduction=cost_reduction,
        accuracy_maintained=accuracy_maintained
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tokens", f"{graph_tokens}", f"{token_reduction:.1f}% less")
    with col2:
        st.metric("Cost", f"${graph_cost:.4f}", f"{cost_reduction:.1f}% cheaper")
    with col3:
        st.metric("Quality", "✓ Maintained", "BERTScore 0.88+")


if __name__ == "__main__":
    # Uncomment the example you want to run:
    example_static_header()
    # example_dynamic_header()
    # example_with_real_data()
